"""
MC Castellazzo — Patch wagtail-localize "Update translations" view
====================================================================
Aggiunge un terzo flag al form di /admin/localize/update/<id>/:

    [✓] Forza traduzione di TUTTI i contenuti

Quando attivo (insieme a "Usa machine translation"), elimina le traduzioni già
esistenti dei segmenti della pagina sorgente, in modo che il machine translator
le rigeneri da zero — utile dopo modifiche estese o cambi di terminologia.

Implementato come patch leggera per non forkare wagtail-localize. Applicato in
`apps.core.apps.CoreConfig.ready()`.
"""
from __future__ import annotations

import logging

from django import forms
from django.utils.translation import gettext_lazy as _
from wagtail_localize.views import update_translations as _ut

logger = logging.getLogger(__name__)
_audit_logger = logging.getLogger("security")

_original_form_init = _ut.UpdateTranslationsForm.__init__
_original_form_valid = _ut.UpdateTranslationsView.form_valid


def _patched_form_init(self, *args, **kwargs):
    _original_form_init(self, *args, **kwargs)
    # Il flag ha senso solo se è configurato un machine translator
    if getattr(self, "_has_machine_translator", False):
        self.fields["retranslate_all"] = forms.BooleanField(
            label=_("Forza traduzione di TUTTI i contenuti"),
            help_text=_(
                "Sovrascrive le traduzioni esistenti: rilancia la traduzione "
                "automatica anche sui segmenti già tradotti. "
                "Richiede l'opzione \"Usa machine translation\" attiva."
            ),
            required=False,
        )


def _patched_form_valid(self, form):
    """Estende `form_valid` cancellando le traduzioni esistenti se richiesto."""
    if form.cleaned_data.get("retranslate_all") and form.cleaned_data.get(
        "use_machine_translation"
    ):
        # Import locale per evitare problemi di app-loading
        from wagtail_localize.models import StringTranslation

        source = self.object
        enabled = source.translations.filter(enabled=True)
        target_locale_ids = list(enabled.values_list("target_locale_id", flat=True))
        string_ids = list(
            source.stringsegment_set.values_list("string_id", flat=True)
        )
        if string_ids and target_locale_ids:
            deleted, _details = StringTranslation.objects.filter(
                translation_of_id__in=string_ids,
                locale_id__in=target_locale_ids,
            ).delete()
            logger.info(
                "Force re-translate: cleared %s StringTranslation rows "
                "(source=%s, locales=%s)",
                deleted, source.id, target_locale_ids,
            )
            _audit_logger.info(
                "SECURITY user=%s#%s event=localize.force_retranslate "
                "source_id=%s deleted=%s locales=%s",
                self.request.user.get_username(),
                self.request.user.pk,
                source.id,
                deleted,
                target_locale_ids,
            )
    return _original_form_valid(self, form)


def apply() -> None:
    """Applica le patch (idempotente)."""
    if getattr(_ut.UpdateTranslationsForm.__init__, "_mcc_patched", False):
        return
    _ut.UpdateTranslationsForm.__init__ = _patched_form_init
    _ut.UpdateTranslationsView.form_valid = _patched_form_valid
    _ut.UpdateTranslationsForm.__init__._mcc_patched = True  # type: ignore[attr-defined]
    logger.debug("wagtail-localize: 'retranslate_all' flag patch applied")
