#!/usr/bin/env python3
"""
Comprehensive tests for EML Parser

This test suite covers the main functionality of the EML parser library.
"""

import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path to import eml_parser
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from eml_parser import EmlReader, MultiPartParser


class TestMultiPartParser:
    """Test MultiPartParser class."""
    
    def test_invalid_input(self):
        """Test handling of invalid input."""
        with pytest.raises(ValueError, match="Invalid content for MultiPartParser"):
            MultiPartParser("invalid string input")
    
    def test_simple_text_email(self):
        """Test parsing a simple text email."""
        email_content = b"""Subject: Test Subject
From: sender@example.com
To: recipient@example.com
Content-Type: text/plain

Hello, this is a test email."""
        
        parser = MultiPartParser(email_content)
        
        assert parser.get_header('subject') == 'Test Subject'
        assert parser.get_header('from') == 'sender@example.com'
        assert parser.get_header('to') == 'recipient@example.com'
        assert parser.get_body() == 'Hello, this is a test email.'
        assert not parser.is_attachment
        assert not parser.is_inline_image
    
    def test_content_type_parsing(self):
        """Test content type parsing."""
        email_content = b"""Content-Type: text/html; charset=utf-8

<p>HTML content</p>"""
        
        parser = MultiPartParser(email_content)
        content_type = parser.get_content_type()
        
        assert content_type['media_type'] == 'text'
        assert content_type['sub_type'] == 'html'
        assert 'charset=utf-8' in content_type['args']
        assert parser.content_type == 'text/html'
    
    def test_base64_decoding(self):
        """Test base64 content decoding."""
        # "Hello World" in base64
        email_content = b"""Content-Transfer-Encoding: base64

SGVsbG8gV29ybGQ="""
        
        parser = MultiPartParser(email_content)
        body = parser.get_body()
        
        assert body == b'Hello World'
    
    def test_quoted_printable_decoding(self):
        """Test quoted-printable content decoding."""
        email_content = b"""Content-Transfer-Encoding: quoted-printable

Hello=20World=21"""
        
        parser = MultiPartParser(email_content)
        body = parser.get_body()
        
        assert body == b'Hello World!'
    
    def test_header_decoding(self):
        """Test RFC1342 header decoding."""
        email_content = b"""Subject: =?UTF-8?B?VGVzdCBTdWJqZWN0?=
From: sender@example.com

Body content"""
        
        parser = MultiPartParser(email_content)
        
        # Without decoding
        subject_raw = parser.get_header('subject')
        assert '=?UTF-8?B?' in subject_raw
        
        # With decoding
        subject_decoded = parser.get_header('subject', decode=True)
        assert subject_decoded == 'Test Subject'


class TestEmlReader:
    """Test EmlReader class."""
    
    def test_simple_email(self):
        """Test reading a simple email."""
        email_content = b"""Date: Mon, 01 Jan 2024 12:00:00 +0000
Subject: Test Email
From: sender@example.com
To: recipient@example.com
Content-Type: text/plain

This is a test email body."""
        
        reader = EmlReader(email_content)
        
        assert reader.get_subject() == 'Test Email'
        assert reader.get_from() == 'sender@example.com'
        assert reader.get_to() == 'recipient@example.com'
        assert reader.get_message_text() == 'This is a test email body.'
        assert reader.get_type() == 'sent'  # No 'Received' header
        
        # Test date parsing
        date = reader.get_date()
        assert isinstance(date, datetime)
        assert date.year == 2024
        assert date.month == 1
        assert date.day == 1
    
    def test_multipart_email(self):
        """Test reading a multipart email."""
        boundary = "----=_Part_123456"
        email_content = f"""Subject: Multipart Test
From: sender@example.com
To: recipient@example.com
Content-Type: multipart/mixed; boundary="{boundary}"

------=_Part_123456
Content-Type: text/plain

Plain text content.

------=_Part_123456
Content-Type: text/html

<p>HTML content.</p>

------=_Part_123456--""".encode()
        
        reader = EmlReader(email_content)
        
        assert reader.get_subject() == 'Multipart Test'
        assert reader.get_message_text() == 'Plain text content.'
        assert reader.get_message_html() == '<p>HTML content.</p>'
    
    def test_attachment_detection(self):
        """Test attachment detection and extraction."""
        boundary = "----=_Part_123456"
        email_content = f"""Subject: Email with Attachment
From: sender@example.com
To: recipient@example.com
Content-Type: multipart/mixed; boundary="{boundary}"

------=_Part_123456
Content-Type: text/plain

Email with attachment.

------=_Part_123456
Content-Type: application/pdf
Content-Disposition: attachment; filename="document.pdf"
Content-Transfer-Encoding: base64

JVBERi0xLjQK

------=_Part_123456--""".encode()
        
        reader = EmlReader(email_content)
        attachments = reader.get_attachments()
        
        assert len(attachments) == 1
        assert attachments[0]['filename'] == 'document.pdf'
        assert attachments[0]['content_type'] == 'application/pdf'
        assert len(attachments[0]['content']) > 0
    
    def test_inline_image_detection(self):
        """Test inline image detection."""
        boundary = "----=_Part_123456"
        email_content = f"""Subject: Email with Inline Image
From: sender@example.com
To: recipient@example.com
Content-Type: multipart/related; boundary="{boundary}"

------=_Part_123456
Content-Type: text/html

<p>See image: <img src="cid:image1@example.com"></p>

------=_Part_123456
Content-Type: image/png
Content-Disposition: inline
Content-ID: <image1@example.com>
Content-Transfer-Encoding: base64

iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==

------=_Part_123456--""".encode()
        
        reader = EmlReader(email_content)
        inline_images = reader.get_inline_images()
        
        assert len(inline_images) == 1
        assert inline_images[0]['content_id'] == 'image1@example.com'
        assert inline_images[0]['content_type'] == 'image/png'
    
    def test_html_with_inline_images(self):
        """Test HTML processing with inline images."""
        boundary = "----=_Part_123456"
        email_content = f"""Subject: HTML with Images
Content-Type: multipart/related; boundary="{boundary}"

------=_Part_123456
Content-Type: text/html

<p>Image: <img src="cid:test@example.com"></p>

------=_Part_123456
Content-Type: image/png
Content-ID: <test@example.com>
Content-Transfer-Encoding: base64

iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==

------=_Part_123456--""".encode()
        
        reader = EmlReader(email_content)
        
        # Test with data URLs
        html_with_data_urls = reader.get_message_html_with_inline_images(use_data_urls=True)
        assert 'data:image/png;base64,' in html_with_data_urls
        assert 'cid:test@example.com' not in html_with_data_urls
        
        # Test with file saving
        with tempfile.TemporaryDirectory() as temp_dir:
            html_with_files = reader.get_message_html_with_inline_images(save_images_to=temp_dir)
            
            # Check that image file was created
            image_files = list(Path(temp_dir).glob('*.png'))
            assert len(image_files) > 0
            
            # Check that HTML references the file
            assert str(image_files[0].name) in html_with_files
            assert 'cid:test@example.com' not in html_with_files
    
    def test_email_type_detection(self):
        """Test email type detection (sent vs received)."""
        # Email without Received header (sent)
        sent_email = b"""Subject: Sent Email
From: me@example.com
To: you@example.com

Sent email content."""
        
        reader = EmlReader(sent_email)
        assert reader.get_type() == 'sent'
        
        # Email with Received header (received)
        received_email = b"""Received: from mail.example.com
Subject: Received Email
From: you@example.com
To: me@example.com

Received email content."""
        
        reader = EmlReader(received_email)
        assert reader.get_type() == 'received'
    
    def test_missing_headers(self):
        """Test handling of missing headers."""
        email_content = b"""Content-Type: text/plain

Body only email."""
        
        reader = EmlReader(email_content)
        
        assert reader.get_subject() is None
        assert reader.get_from() is None
        assert reader.get_to() is None
        assert reader.get_date() is None
        assert reader.get_message_text() == 'Body only email.'
    
    def test_multiple_header_values(self):
        """Test handling of headers with multiple values."""
        email_content = b"""Received: from server1.example.com
Received: from server2.example.com
To: user1@example.com
To: user2@example.com

Multiple values test."""
        
        reader = EmlReader(email_content)
        
        # Should return list for multiple values
        received_headers = reader.get_header('received')
        assert isinstance(received_headers, list)
        assert len(received_headers) == 2
        assert 'server1.example.com' in received_headers[0]
        assert 'server2.example.com' in received_headers[1]


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_empty_content(self):
        """Test handling of empty content."""
        reader = EmlReader(b"")
        
        assert reader.get_subject() is None
        assert reader.get_message_text() is None
        assert len(reader.get_attachments()) == 0
    
    def test_malformed_headers(self):
        """Test handling of malformed headers."""
        email_content = b"""This is not a proper header
Subject Test Subject
From: sender@example.com

Body content."""
        
        # Should not crash
        reader = EmlReader(email_content)
        assert reader.get_subject() == 'Test Subject'
    
    def test_invalid_date(self):
        """Test handling of invalid date formats."""
        email_content = b"""Date: Not a valid date
Subject: Test

Body."""
        
        reader = EmlReader(email_content)
        assert reader.get_date() is None
    
    def test_invalid_encoding(self):
        """Test handling of invalid encoding."""
        email_content = b"""Content-Transfer-Encoding: invalid-encoding

Body content."""
        
        # Should not crash and fall back to binary
        reader = EmlReader(email_content)
        body = reader.get_message_text()
        assert body is not None


# Utility functions for testing
def create_sample_multipart_email():
    """Create a sample multipart email for testing."""
    boundary = "----=_Part_" + "123456789"
    
    return f"""Subject: Sample Multipart Email
From: sender@example.com
To: recipient@example.com
Date: Mon, 01 Jan 2024 12:00:00 +0000
Content-Type: multipart/mixed; boundary="{boundary}"

------=_Part_123456789
Content-Type: text/plain

This is the plain text part of the email.

------=_Part_123456789
Content-Type: text/html

<p>This is the <strong>HTML</strong> part of the email.</p>

------=_Part_123456789
Content-Type: application/pdf
Content-Disposition: attachment; filename="sample.pdf"
Content-Transfer-Encoding: base64

JVBERi0xLjQKJcfsj6IKNSAwIG9iago8PAovTGVuZ3RoIDYgMCBSCi9GaWx0ZXIgL0ZsYXRlRGVjb2RlCj4+CnN0cmVhbQp4nDPUU0ssLdZRUAcCGGxVIVJpXQVpJzIAAAASdGKWJlZnUa5iNQUA//6i0KV

------=_Part_123456789--""".encode()


if __name__ == "__main__":
    pytest.main([__file__]) 