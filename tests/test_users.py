"""
Tests for user models.

mccastellazzob.com - Moto Club Castellazzo Bormida
"""

import pytest
from django.contrib.auth import get_user_model

from tests.factories.users import AdminUserFactory
from tests.factories.users import UserFactory


User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test per il modello User."""

    def test_create_user(self):
        """Test creazione utente base."""
        user = UserFactory()
        assert user.email is not None
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_user_with_email(self):
        """Test creazione utente con email specifica."""
        user = UserFactory(email="custom@example.com")
        assert user.email == "custom@example.com"

    def test_user_str(self):
        """Test rappresentazione stringa."""
        user = UserFactory(email="test@example.com")
        assert str(user) == "test@example.com"

    def test_create_superuser(self):
        """Test creazione superuser."""
        admin = AdminUserFactory()
        assert admin.is_staff is True
        assert admin.is_superuser is True

    def test_user_manager_create_user(self):
        """Test UserManager.create_user."""
        user = User.objects.create_user(
            email="manager@example.com",
            password="testpass123",
        )
        assert user.email == "manager@example.com"
        assert user.check_password("testpass123")

    def test_user_manager_create_user_no_email(self):
        """Test che create_user richieda email."""
        with pytest.raises(ValueError):
            User.objects.create_user(email="", password="test")

    def test_user_manager_create_superuser(self):
        """Test UserManager.create_superuser."""
        admin = User.objects.create_superuser(
            email="super@example.com",
            password="adminpass",
        )
        assert admin.is_staff is True
        assert admin.is_superuser is True
