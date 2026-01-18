"""
Tests for ContactPage form with Honeypot, Timestamp, and attachments.
"""
import pytest
import time
from unittest.mock import patch, MagicMock
from django.test import Client, override_settings
from apps.website.models import ContactPage


@pytest.fixture
def contact_page(db):
    """Create a minimal ContactPage instance for testing methods."""
    # Create a mock page - we only need to test the methods
    page = ContactPage()
    page.email = "test@example.com"
    page.show_contact_form = True
    return page


class TestContactPageTimestamp:
    """Test Timestamp anti-spam functionality."""
    
    def test_generate_timestamp_token(self, contact_page):
        """Test that timestamp token is generated correctly."""
        token_data = contact_page.generate_captcha_token()
        
        assert 'timestamp_token' in token_data
        assert ':' in token_data['timestamp_token']
        # Should have format: timestamp:signature
        parts = token_data['timestamp_token'].split(':')
        assert len(parts) == 2
    
    def test_verify_timestamp_correct_time(self, contact_page):
        """Test timestamp verification after 10+ seconds."""
        token_data = contact_page.generate_captcha_token()
        
        # Mock time to be 11 seconds later
        with patch('apps.website.models.about.time.time', return_value=time.time() + 11):
            success, error = contact_page.verify_timestamp(token_data['timestamp_token'])
        
        assert success is True
        assert error == ""
    
    def test_verify_timestamp_too_fast(self, contact_page):
        """Test timestamp verification when form submitted too quickly."""
        token_data = contact_page.generate_captcha_token()
        
        # Submit immediately (no time mock - should fail)
        success, error = contact_page.verify_timestamp(token_data['timestamp_token'])
        
        assert success is False
        assert error != ""
    
    def test_verify_timestamp_expired(self, contact_page):
        """Test timestamp verification when token is too old."""
        token_data = contact_page.generate_captcha_token()
        
        # Mock time to be 2 hours later
        with patch('apps.website.models.about.time.time', return_value=time.time() + 7200):
            success, error = contact_page.verify_timestamp(token_data['timestamp_token'])
        
        assert success is False
        assert "scaduto" in error.lower() or "expired" in error.lower()


class TestContactPageHoneypot:
    """Test honeypot functionality."""
    
    def test_honeypot_empty_passes(self, contact_page, rf):
        """Test that empty honeypot passes verification."""
        request = rf.post('/contact/', {'website': ''})
        assert contact_page.verify_honeypot(request) is True
    
    def test_honeypot_filled_fails(self, contact_page, rf):
        """Test that filled honeypot fails verification."""
        request = rf.post('/contact/', {'website': 'spam-bot-filled-this'})
        assert contact_page.verify_honeypot(request) is False


class TestContactPageAttachments:
    """Test attachment validation."""
    
    def test_validate_valid_attachment(self, contact_page):
        """Test validation of valid attachments."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        file = SimpleUploadedFile(
            name="test.pdf",
            content=b"PDF content",
            content_type="application/pdf"
        )
        
        valid_files, errors = contact_page.validate_attachments([file])
        
        assert len(valid_files) == 1
        assert len(errors) == 0
    
    def test_validate_invalid_extension(self, contact_page):
        """Test validation rejects invalid file extensions."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        file = SimpleUploadedFile(
            name="malware.exe",
            content=b"EXE content",
            content_type="application/octet-stream"
        )
        
        valid_files, errors = contact_page.validate_attachments([file])
        
        assert len(valid_files) == 0
        assert len(errors) == 1
    
    def test_validate_too_many_files(self, contact_page):
        """Test validation limits number of files."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        files = [
            SimpleUploadedFile(f"test{i}.pdf", b"content", "application/pdf")
            for i in range(5)  # More than MAX_FILES (3)
        ]
        
        valid_files, errors = contact_page.validate_attachments(files)
        
        assert len(valid_files) <= contact_page.MAX_FILES
        assert len(errors) >= 1
