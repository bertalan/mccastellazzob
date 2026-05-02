# Security Remediation Decisions — Open Findings (V2)

Data: 2026-05-02
Stato: Decisioni approvate, implementazione da eseguire in step successivo
Scope: V2-010, V2-011, V2-012, V2-014, V2-015, V2-017, V2-018, V2-019

## Executive Decisions

- V2-010: RawHTMLBlock consentito solo a superuser.
- V2-011: SSRF mitigato con allowlist domini estendibile da settings (HTTPS only).
- V2-012: Email verification intermedia: mandatory in produzione, optional in dev/stage.
- V2-012-RL: Rate limit auth standard: login 5/min per IP+username, reset 3/15min per email+IP.
- V2-014: Audit logging app-level su DB + log file JSON.
- V2-015: Rate limit traduzione: staff 10/min + 200/day.
- V2-017: CSP rollout in Report-Only per 2 settimane, poi enforced.
- V2-018: CVE check con pip-audit + Dependabot.
- V2-019: ALLOWED_HOSTS fail-fast fuori ambiente dev.

## Detailed Plan Per Finding

### V2-010 — RawHTMLBlock (architetturale)
Decisione
- Mantenere RawHTMLBlock ma renderlo utilizzabile solo da superuser.

Implementazione prevista
- Identificare dove RawHTMLBlock viene registrato/usato nei blocchi pagina.
- Applicare controllo permessi lato editor/admin (visibilita chooser + validazione server-side).
- Se utente non superuser, bloccare salvataggio con messaggio chiaro.

Acceptance criteria
- Editor non superuser non possono aggiungere/modificare RawHTMLBlock.
- Superuser mantiene funzionalita completa.
- Nessuna regressione sui contenuti esistenti.

Rischio residuo
- Resta rischio insider superuser (accettato).

---

### V2-011 — SSRF Nominatim/MyMemory
Decisione
- Allowlist domini estendibile da settings, enforcement HTTPS only.

Implementazione prevista
- Introdurre in settings lista host consentiti (es. NOMINATIM_ALLOWED_HOSTS, TRANSLATION_ALLOWED_HOSTS).
- In funzioni HTTP, validare URL finale:
  - schema == https
  - host in allowlist
  - no redirect verso host non consentiti
- Impostare timeout brevi e max redirect controllato.

Acceptance criteria
- Richieste verso host non allowlisted vengono rifiutate con errore gestito.
- Richieste valide continuano a funzionare.

Rischio residuo
- Dipendenza dalla sicurezza del provider esterno.

---

### V2-012 — Email verification + auth rate limiting
Decisione
- Mandatory solo in produzione; optional in dev/stage.
- Rate limit standard su login/reset.

Implementazione prevista
- Allauth:
  - prod: ACCOUNT_EMAIL_VERIFICATION = "mandatory"
  - dev/stage: mantenere optional per UX e test.
- Rate limiting auth:
  - login: 5/min per IP+username
  - password reset: 3/15min per email+IP
- Definire risposta coerente (429) e messaggi non enumerabili.

Acceptance criteria
- In produzione non si completa signup senza email verificata.
- Endpoint auth applicano i limiti definiti.

Rischio residuo
- Possibili falsi positivi rate-limit su reti condivise.

---

### V2-014 — Audit log
Decisione
- Implementazione app-level su DB + log file JSON.

Implementazione prevista
- Definire eventi minimi da tracciare:
  - bulk upload immagini
  - auto-translate page
  - azioni admin sensibili (modifiche contenuti critici)
- Salvare su modello DB dedicato (evento, actor, target, timestamp, esito, metadata).
- Emissione parallela in logger JSON per integrazione futura SIEM.

Acceptance criteria
- Eventi sensibili appaiono sia in DB sia nei log JSON.
- Ricerca eventi base possibile da admin (read-only).

Rischio residuo
- Nessuna correlazione centralizzata finche SIEM non e integrato.

---

### V2-015 — Rate limit translation API
Decisione
- Limite staff: 10/min + 200/day.

Implementazione prevista
- Applicare rate limit su view di traduzione automatica.
- Chiave limite: user_id (primaria) + fallback IP.
- Logging evento di throttling (per audit).

Acceptance criteria
- Burst oltre 10/min bloccato.
- Oltre 200/day bloccato.
- Utente riceve feedback chiaro.

Rischio residuo
- Necessaria calibrazione dopo osservazione reale traffico.

---

### V2-017 — CSP
Decisione
- Fase iniziale Report-Only 2 settimane, poi enforced.

Implementazione prevista
- Introdurre django-csp.
- Configurare policy iniziale conservativa con sorgenti necessarie (Leaflet/AOS/static locali).
- Abilitare report-uri/report-to e raccogliere violazioni.
- Dopo tuning, passare a enforced.

Acceptance criteria
- Nessuna rottura funzionale critica in fase Report-Only.
- Policy enforced senza blocchi principali UX.

Rischio residuo
- Inline script/style legacy potrebbero richiedere nonce/hash o refactor.

---

### V2-018 — CVE check (CI)
Decisione
- pip-audit + Dependabot.

Implementazione prevista
- Aggiungere workflow CI:
  - install dependencies
  - pip-audit fail su vulnerability high/critical (o su qualsiasi CVE se preferito)
- Abilitare Dependabot per aggiornamenti periodici Python/GitHub Actions.

Acceptance criteria
- PR/CI fallisce quando emergono CVE oltre soglia.
- PR automatiche Dependabot attive.

Rischio residuo
- Possibili falsi positivi advisory; serve triage periodico.

---

### V2-019 — ALLOWED_HOSTS fallback
Decisione
- Fail-fast fuori dev.

Implementazione prevista
- In base settings:
  - se DEBUG=False e ALLOWED_HOSTS assente/vuoto -> RuntimeError
  - in DEBUG=True mantenere fallback localhost.
- Documentare variabile obbligatoria per stage/prod.

Acceptance criteria
- Ambiente non-dev non parte con ALLOWED_HOSTS non configurato.
- Dev locale continua a funzionare senza friction.

Rischio residuo
- Nessuno significativo se variabili ambiente sono gestite correttamente.

## Sequenza di Esecuzione Raccomandata

1. V2-019 (fail-fast hosts) e V2-011 (allowlist SSRF): riduzione rischio configurativo immediato.
2. V2-015 + V2-012-RL: prevenzione abuso endpoint.
3. V2-010: hardening editor su contenuto HTML raw.
4. V2-014: audit trail tecnico-operativo.
5. V2-017: CSP report-only e tuning.
6. V2-018: automazione CI per vulnerabilita dipendenze.
7. V2-012 email mandatory in prod (coordinata con processo onboarding utenti).

## Note operative per il prossimo step

- Eseguire implementazione in branch dedicato (es. security/v2-hardening-phase2).
- Aprire PR per blocchi tematici (config, auth/rate-limit, logging, csp, ci).
- Aggiungere test automatici mirati per ogni finding implementato.
- Pianificare una finestra di osservazione per CSP Report-Only (14 giorni).
