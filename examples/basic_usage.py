#!/usr/bin/env python3
"""
Basic usage example for EML Parser

This example demonstrates how to parse an .eml file and extract
basic information like headers, content, and attachments.
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the path to import eml_parser
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from eml_parser import EmlReader


def parse_email_file(eml_file_path):
    """Parse an EML file and display basic information."""
    
    if not os.path.exists(eml_file_path):
        print(f"Error: File '{eml_file_path}' not found.")
        return
    
    try:
        # Read the EML file
        with open(eml_file_path, 'rb') as f:
            email_content = f.read()
        
        # Create EML reader
        reader = EmlReader(email_content)
        
        # Display basic email information
        print("=" * 60)
        print("EMAIL INFORMATION")
        print("=" * 60)
        
        # Headers
        print(f"Subject:    {reader.get_subject() or 'No Subject'}")
        print(f"From:       {reader.get_from() or 'Unknown'}")
        print(f"To:         {reader.get_to() or 'Unknown'}")
        
        # Optional headers
        cc = reader.get_cc()
        if cc:
            print(f"CC:         {cc}")
        
        bcc = reader.get_bcc()
        if bcc:
            print(f"BCC:        {bcc}")
        
        reply_to = reader.get_reply_to()
        if reply_to:
            print(f"Reply-To:   {reply_to}")
        
        # Date
        date = reader.get_date()
        if date:
            print(f"Date:       {date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Email type
        print(f"Type:       {reader.get_type()}")
        
        # Content information
        print("\n" + "=" * 60)
        print("CONTENT INFORMATION")
        print("=" * 60)
        
        text_content = reader.get_message_text()
        html_content = reader.get_message_html()
        
        print(f"Has Text:   {'Yes' if text_content else 'No'}")
        print(f"Has HTML:   {'Yes' if html_content else 'No'}")
        
        if text_content:
            text_preview = text_content[:200] + "..." if len(text_content) > 200 else text_content
            print(f"Text Preview: {repr(text_preview)}")
        
        # Attachments
        attachments = reader.get_attachments()
        inline_images = reader.get_inline_images()
        
        print("\n" + "=" * 60)
        print("ATTACHMENTS & IMAGES")
        print("=" * 60)
        
        print(f"Attachments: {len(attachments)}")
        print(f"Inline Images: {len(inline_images)}")
        
        # List attachments
        if attachments:
            print("\nAttachments:")
            for i, attachment in enumerate(attachments, 1):
                print(f"  {i}. {attachment['filename']} ({attachment['filesize']} bytes)")
                print(f"     Content-Type: {attachment['content_type']}")
        
        # List inline images
        if inline_images:
            print("\nInline Images:")
            for i, image in enumerate(inline_images, 1):
                print(f"  {i}. {image['filename']} ({image['filesize']} bytes)")
                print(f"     Content-Type: {image['content_type']}")
                print(f"     Content-ID: {image['content_id']}")
        
        # Additional headers
        print("\n" + "=" * 60)
        print("ADDITIONAL HEADERS")
        print("=" * 60)
        
        interesting_headers = [
            'message-id', 'content-type', 'mime-version', 
            'x-mailer', 'user-agent', 'return-path'
        ]
        
        for header in interesting_headers:
            value = reader.get_header(header)
            if value:
                print(f"{header.title()}: {value}")
        
    except Exception as e:
        print(f"Error parsing email: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function to handle command line arguments."""
    
    if len(sys.argv) != 2:
        print("Usage: python basic_usage.py <eml_file_path>")
        print("\nExample:")
        print("  python basic_usage.py ../email.eml")
        sys.exit(1)
    
    eml_file_path = sys.argv[1]
    parse_email_file(eml_file_path)


if __name__ == "__main__":
    main() 