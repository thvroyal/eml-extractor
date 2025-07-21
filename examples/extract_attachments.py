#!/usr/bin/env python3
"""
Attachment extraction example for EML Parser

This example demonstrates how to extract and save all attachments
and inline images from an .eml file.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path to import eml_extractor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from eml_extractor import EmlReader


def extract_attachments(eml_file_path, output_dir="extracted_files"):
    """Extract all attachments and inline images from an EML file."""
    
    if not os.path.exists(eml_file_path):
        print(f"Error: File '{eml_file_path}' not found.")
        return False
    
    try:
        # Read the EML file
        with open(eml_file_path, 'rb') as f:
            email_content = f.read()
        
        # Create EML reader
        reader = EmlReader(email_content)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Extract regular attachments
        attachments = reader.get_attachments()
        print(f"Found {len(attachments)} attachment(s)")
        
        for i, attachment in enumerate(attachments):
            filename = attachment['filename']
            if not filename:
                # Generate filename based on content type
                content_type = attachment['content_type'] or 'application/octet-stream'
                extension = content_type.split('/')[-1]
                filename = f"attachment_{i+1}.{extension}"
            
            # Ensure unique filename
            filepath = output_path / filename
            counter = 1
            original_filepath = filepath
            while filepath.exists():
                stem = original_filepath.stem
                suffix = original_filepath.suffix
                filepath = output_path / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # Save attachment
            with open(filepath, 'wb') as f:
                f.write(attachment['content'])
            
            print(f"  Saved: {filepath} ({attachment['filesize']} bytes)")
            print(f"         Content-Type: {attachment['content_type']}")
        
        # Extract inline images
        inline_images = reader.get_inline_images()
        print(f"\nFound {len(inline_images)} inline image(s)")
        
        # Create subdirectory for inline images
        images_dir = output_path / "inline_images"
        if inline_images:
            images_dir.mkdir(exist_ok=True)
        
        for i, image in enumerate(inline_images):
            filename = image['filename']
            if not filename:
                # Generate filename based on content type
                content_type = image['content_type'] or 'image/png'
                extension = content_type.split('/')[-1]
                content_id = image['content_id'] or f"image_{i+1}"
                # Clean content_id for filename
                clean_id = "".join(c for c in content_id if c.isalnum() or c in "._-")
                filename = f"{clean_id}.{extension}"
            
            # Ensure unique filename
            filepath = images_dir / filename
            counter = 1
            original_filepath = filepath
            while filepath.exists():
                stem = original_filepath.stem
                suffix = original_filepath.suffix
                filepath = images_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # Save inline image
            with open(filepath, 'wb') as f:
                f.write(image['content'])
            
            print(f"  Saved: {filepath} ({image['filesize']} bytes)")
            print(f"         Content-Type: {image['content_type']}")
            print(f"         Content-ID: {image['content_id']}")
        
        total_files = len(attachments) + len(inline_images)
        if total_files > 0:
            print(f"\nSuccessfully extracted {total_files} file(s) to '{output_dir}'")
        else:
            print("\nNo attachments or inline images found in the email.")
        
        return True
        
    except Exception as e:
        print(f"Error extracting attachments: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to handle command line arguments."""
    
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python extract_attachments.py <eml_file_path> [output_directory]")
        print("\nExample:")
        print("  python extract_attachments.py ../email.eml")
        print("  python extract_attachments.py ../email.eml ./my_attachments")
        sys.exit(1)
    
    eml_file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "extracted_files"
    
    success = extract_attachments(eml_file_path, output_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 