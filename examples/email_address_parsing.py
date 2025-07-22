#!/usr/bin/env python3
"""
Email Address Parsing Example for EML Parser

This example demonstrates the new email address parsing capabilities
that can extract display names and email addresses separately.
"""

import os
import sys

# Add the parent directory to the path to import eml_extractor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from eml_extractor import EmlReader


def demonstrate_address_parsing(eml_file_path):
    """Demonstrate the email address parsing functionality."""
    
    if not os.path.exists(eml_file_path):
        print(f"Error: File '{eml_file_path}' not found.")
        return
    
    try:
        # Read the EML file
        with open(eml_file_path, 'rb') as f:
            email_content = f.read()
        
        # Create EML reader
        reader = EmlReader(email_content)
        
        print("=" * 60)
        print("EMAIL ADDRESS PARSING DEMONSTRATION")
        print("=" * 60)
        
        # From header parsing
        print("\n🔹 FROM HEADER:")
        print(f"Raw From:        {reader.get_from()}")
        print(f"From Email:      {reader.get_from_email()}")
        print(f"From Name:       {reader.get_from_name()}")
        
        from_name, from_email = reader.get_from_parsed()
        print(f"Parsed:          Name='{from_name}', Email='{from_email}'")
        
        # To header parsing
        print("\n🔹 TO HEADER:")
        print(f"Raw To:          {reader.get_to()}")
        print(f"To Emails:       {reader.get_to_emails()}")
        print(f"To Names:        {reader.get_to_names()}")
        print(f"Parsed To:")
        for name, email in reader.get_to_parsed():
            print(f"  - Name='{name}', Email='{email}'")
        
        # CC header parsing (if present)
        cc_header = reader.get_cc()
        if cc_header:
            print("\n🔹 CC HEADER:")
            print(f"Raw CC:          {cc_header}")
            print(f"CC Emails:       {reader.get_cc_emails()}")
            print(f"CC Names:        {reader.get_cc_names()}")
            print(f"Parsed CC:")
            for name, email in reader.get_cc_parsed():
                print(f"  - Name='{name}', Email='{email}'")
        
        # BCC header parsing (if present)
        bcc_header = reader.get_bcc()
        if bcc_header:
            print("\n🔹 BCC HEADER:")
            print(f"Raw BCC:         {bcc_header}")
            print(f"BCC Emails:      {reader.get_bcc_emails()}")
            print(f"BCC Names:       {reader.get_bcc_names()}")
            print(f"Parsed BCC:")
            for name, email in reader.get_bcc_parsed():
                print(f"  - Name='{name}', Email='{email}'")
        
        # Reply-To header parsing (if present)
        reply_to_header = reader.get_reply_to()
        if reply_to_header:
            print("\n🔹 REPLY-TO HEADER:")
            print(f"Raw Reply-To:    {reply_to_header}")
            print(f"Reply-To Email:  {reader.get_reply_to_email()}")
            
            reply_name, reply_email = reader.get_reply_to_parsed()
            print(f"Parsed:          Name='{reply_name}', Email='{reply_email}'")
        
        # Comparison with old vs new methods
        print("\n" + "=" * 60)
        print("COMPARISON: OLD VS NEW METHODS")
        print("=" * 60)
        
        print("\n🔸 OLD METHOD (Raw headers):")
        print(f"From: {reader.get_from()}")
        print(f"To:   {reader.get_to()}")
        
        print("\n🔸 NEW METHODS (Parsed addresses):")
        print(f"From Email: {reader.get_from_email()}")
        print(f"To Emails:  {', '.join(reader.get_to_emails())}")
        
        print("\n🔸 USAGE EXAMPLES:")
        print("# Get just email addresses for processing:")
        print(f"sender_email = reader.get_from_email()  # '{reader.get_from_email()}'")
        print(f"recipient_emails = reader.get_to_emails()  # {reader.get_to_emails()}")
        
        print("\n# Get display names for user-friendly display:")
        print(f"sender_name = reader.get_from_name()  # '{reader.get_from_name()}'")
        print(f"recipient_names = reader.get_to_names()  # {reader.get_to_names()}")
        
        print("\n# Get both name and email together:")
        print(f"from_name, from_email = reader.get_from_parsed()")
        print(f"# Result: name='{from_name}', email='{from_email}'")
        
    except Exception as e:
        print(f"Error parsing email: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function to handle command line arguments."""
    
    if len(sys.argv) != 2:
        print("Usage: python email_address_parsing.py <eml_file_path>")
        print("\nExample:")
        print("  python email_address_parsing.py ../\"Health Insurance Notice 2025.eml\"")
        sys.exit(1)
    
    eml_file_path = sys.argv[1]
    demonstrate_address_parsing(eml_file_path)


if __name__ == "__main__":
    main() 