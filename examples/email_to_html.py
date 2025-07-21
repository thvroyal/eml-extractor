#!/usr/bin/env python3
"""
Email to HTML conversion example for EML Parser

This example demonstrates how to convert an .eml file to a standalone
HTML file with proper inline image handling.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path to import eml_extractor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from eml_extractor import EmlReader


def email_to_html(eml_file_path, output_html_path=None, embed_images=False):
    """Convert an EML file to HTML format."""
    
    if not os.path.exists(eml_file_path):
        print(f"Error: File '{eml_file_path}' not found.")
        return False
    
    try:
        # Generate output filename if not provided
        if not output_html_path:
            eml_path = Path(eml_file_path)
            output_html_path = eml_path.with_suffix('.html')
        
        # Read the EML file
        with open(eml_file_path, 'rb') as f:
            email_content = f.read()
        
        # Create EML reader
        reader = EmlReader(email_content)
        
        print(f"Converting '{eml_file_path}' to HTML...")
        
        # Get HTML content with inline images
        if embed_images:
            print("Embedding images as data URLs...")
            html_content = reader.get_message_html_with_inline_images(use_data_urls=True)
        else:
            # Save images to a subdirectory
            images_dir = Path(output_html_path).stem + "_images"
            print(f"Saving images to '{images_dir}' directory...")
            html_content = reader.get_message_html_with_inline_images(
                save_images_to=images_dir
            )
        
        # Fallback to plain text if no HTML content
        if not html_content:
            print("No HTML content found, using plain text...")
            text_content = reader.get_message_text()
            if text_content:
                # Convert plain text to HTML with basic formatting
                html_content = text_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                html_content = html_content.replace('\n\n', '</p><p>').replace('\n', '<br>')
                html_content = f"<p>{html_content}</p>"
            else:
                html_content = "<p><em>No content found in email.</em></p>"
        
        # Create complete HTML document
        subject = reader.get_subject() or 'Email'
        sender = reader.get_from() or 'Unknown Sender'
        recipients = reader.get_to() or 'Unknown Recipients'
        date = reader.get_date()
        date_str = date.strftime('%Y-%m-%d %H:%M:%S') if date else 'Unknown Date'
        
        # Get attachment information
        attachments = reader.get_attachments()
        inline_images = reader.get_inline_images()
        
        # Build attachment list HTML
        attachment_html = ""
        if attachments:
            attachment_html = "<div class='attachments'><h3>Attachments:</h3><ul>"
            for attachment in attachments:
                filename = attachment['filename'] or 'Unknown filename'
                filesize = attachment['filesize']
                content_type = attachment['content_type'] or 'Unknown type'
                attachment_html += f"<li>{filename} ({filesize} bytes, {content_type})</li>"
            attachment_html += "</ul></div>"
        
        # CSS styles
        css_styles = """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }
        .email-container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        .email-header {
            background-color: #f0f2f5;
            padding: 20px;
            border-bottom: 1px solid #ddd;
        }
        .email-header h1 {
            margin: 0 0 15px 0;
            color: #1a1a1a;
            font-size: 24px;
        }
        .header-info {
            display: grid;
            gap: 8px;
            font-size: 14px;
            color: #666;
        }
        .header-row {
            display: flex;
        }
        .header-label {
            font-weight: bold;
            min-width: 80px;
            color: #444;
        }
        .email-content {
            padding: 20px;
        }
        .attachments {
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 4px;
            border-left: 4px solid #007bff;
        }
        .attachments h3 {
            margin: 0 0 10px 0;
            color: #007bff;
        }
        .attachments ul {
            margin: 0;
            padding-left: 20px;
        }
        .attachments li {
            margin: 5px 0;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #999;
            font-size: 12px;
            background-color: #f0f2f5;
            border-top: 1px solid #ddd;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        """
        
        # Build complete HTML document
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
    <style>
{css_styles}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="email-header">
            <h1>{subject}</h1>
            <div class="header-info">
                <div class="header-row">
                    <span class="header-label">From:</span>
                    <span>{sender}</span>
                </div>
                <div class="header-row">
                    <span class="header-label">To:</span>
                    <span>{recipients}</span>
                </div>
                <div class="header-row">
                    <span class="header-label">Date:</span>
                    <span>{date_str}</span>
                </div>
            </div>
        </div>
        
        <div class="email-content">
            {html_content}
            {attachment_html}
        </div>
        
        <div class="footer">
            Generated by EML Parser - {len(attachments)} attachment(s), {len(inline_images)} inline image(s)
        </div>
    </div>
</body>
</html>"""
        
        # Save HTML file
        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"Successfully converted to: {output_html_path}")
        
        # Summary
        print(f"Email subject: {subject}")
        print(f"Attachments: {len(attachments)}")
        print(f"Inline images: {len(inline_images)}")
        print(f"Images embedded: {'Yes' if embed_images else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"Error converting email to HTML: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to handle command line arguments."""
    
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("Usage: python email_to_html.py <eml_file_path> [output_html_path] [--embed-images]")
        print("\nOptions:")
        print("  --embed-images    Embed images as data URLs instead of saving to files")
        print("\nExamples:")
        print("  python email_to_html.py ../email.eml")
        print("  python email_to_html.py ../email.eml output.html")
        print("  python email_to_html.py ../email.eml output.html --embed-images")
        sys.exit(1)
    
    eml_file_path = sys.argv[1]
    output_html_path = None
    embed_images = False
    
    # Parse arguments
    for arg in sys.argv[2:]:
        if arg == '--embed-images':
            embed_images = True
        elif not output_html_path:
            output_html_path = arg
    
    success = email_to_html(eml_file_path, output_html_path, embed_images)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 