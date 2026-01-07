"""
User factories.

mccastellazzob.com - Moto Club Castellazzo Bormida
Factories per modello User.
"""

import factory
from django.contrib.auth import get_user_model


User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory per creare utenti."""

    class Meta:
        model = User
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name", locale="it_IT")
    last_name = factory.Faker("last_name", locale="it_IT")
    is_active = True
    is_staff = False
    is_superuser = False

    @factory.lazy_attribute
    def username(self):
        """Genera username dall'email."""
        return self.email.split("@")[0]

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override per usare create_user."""
        password = kwargs.pop("password", "testpass123")
        user = super()._create(model_class, *args, **kwargs)
        user.set_password(password)
        user.save()
        return user


class AdminUserFactory(UserFactory):
    """Factory per creare superuser."""

    is_staff = True
    is_superuser = True
    email = factory.Sequence(lambda n: f"admin{n}@example.com")
