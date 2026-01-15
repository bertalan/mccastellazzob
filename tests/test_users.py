"""
MC Castellazzo - User Tests
"""
import pytest
import uuid

from apps.custom_user.models import User


@pytest.mark.django_db
class TestUserModel:
    """Tests for User model."""
    
    def test_create_user(self):
        """Test user creation."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser
    
    def test_create_superuser(self):
        """Test superuser creation."""
        unique_username = f"admin-{uuid.uuid4().hex[:8]}"
        admin = User.objects.create_superuser(
            username=unique_username,
            email=f"{unique_username}@example.com",
            password="adminpass123",
        )
        
        assert admin.is_staff
        assert admin.is_superuser
    
    def test_user_str(self):
        """Test user string representation."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Mario",
            last_name="Rossi",
        )
        
        assert str(user) == "Mario Rossi"
    
    def test_user_str_without_name(self):
        """Test user string representation without full name."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        
        assert str(user) == "testuser"
    
    def test_user_preferred_language_default(self):
        """Test default preferred language is Italian."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        
        assert user.preferred_language == "it"
    
    def test_user_member_fields(self):
        """Test member-specific fields."""
        from datetime import date
        
        user = User.objects.create_user(
            username="member",
            email="member@example.com",
            password="memberpass123",
            is_member=True,
            membership_date=date(2020, 1, 15),
        )
        
        assert user.is_member
        assert user.membership_date == date(2020, 1, 15)
