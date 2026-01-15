"""
MC Castellazzo - User Factories
"""
import factory
from factory.django import DjangoModelFactory

from apps.custom_user.models import User


class UserFactory(DjangoModelFactory):
    """Factory for User model."""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name", locale="it_IT")
    last_name = factory.Faker("last_name", locale="it_IT")
    preferred_language = "it"
    is_active = True
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        password = extracted or "testpass123"
        self.set_password(password)


class MemberUserFactory(UserFactory):
    """Factory for member users."""
    
    is_member = True
    membership_date = factory.Faker("date_this_decade")


class AdminUserFactory(UserFactory):
    """Factory for admin users."""
    
    is_staff = True
    is_superuser = True
