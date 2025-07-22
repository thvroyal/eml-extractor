# EML Extractor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/eml-extractor.svg)](https://badge.fury.io/py/eml-extractor)

A pure Python library for extracting data from .eml email files. This library provides a clean and simple API for extracting email headers, body content, attachments, and inline images from .eml files without any external dependencies.

## Features

- **Pure Python**: No external dependencies, uses only the Python standard library
- **Full EML Support**: Parse complete .eml email files including multipart messages
- **Extract Headers**: Get all email headers (From, To, Subject, Date, etc.)
- **Body Content**: Extract both plain text and HTML content
- **Attachments**: Extract and save email attachments
- **Inline Images**: Handle inline images with proper content-id mapping
- **Encoding Support**: Automatic handling of various text encodings and transfer encodings
- **Type Hints**: Full type annotations for better IDE support and code safety

## Installation

Install the library using pip:

```bash
pip install eml-extractor
```

Or install from source:

```bash
git clone https://github.com/thvroyal/eml-extractor.git
cd eml-extractor
pip install .
```

For development with testing dependencies:

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from eml_extractor import EmlReader

# Read an .eml file
with open('email.eml', 'rb') as f:
    email_content = f.read()

# Parse the email
reader = EmlReader(email_content)

# Extract basic information
print(f"Subject: {reader.get_subject()}")
print(f"From: {reader.get_from()}")
print(f"To: {reader.get_to()}")
print(f"Date: {reader.get_date()}")

# Get email body
text_content = reader.get_message_text()
html_content = reader.get_message_html()

# Extract attachments
attachments = reader.get_attachments()
for attachment in attachments:
    print(f"Attachment: {attachment['filename']} ({attachment['filesize']} bytes)")
    
    # Save attachment
    with open(attachment['filename'], 'wb') as f:
        f.write(attachment['content'])
```

## Detailed Usage

### Reading Email Files

```python
from eml_extractor import EmlReader

# Method 1: Read from file
with open('email.eml', 'rb') as f:
    reader = EmlReader(f.read())

# Method 2: If you already have email bytes
email_bytes = b"Subject: Test\r\n\r\nHello World"
reader = EmlReader(email_bytes)
```

### Extracting Headers

```python
# Basic headers with automatic decoding
subject = reader.get_subject()
sender = reader.get_from()  # "John Doe <john@example.com>"
recipients = reader.get_to()  # "Jane Smith <jane@example.com>, Bob Wilson <bob@example.com>"
cc_recipients = reader.get_cc()
bcc_recipients = reader.get_bcc()
reply_to = reader.get_reply_to()
date = reader.get_date()  # Returns datetime object

# NEW: Parse email addresses separately
sender_email = reader.get_from_email()  # "john@example.com"
sender_name = reader.get_from_name()    # "John Doe"

# Get both name and email together
sender_name, sender_email = reader.get_from_parsed()  # ("John Doe", "john@example.com")

# Handle multiple recipients
recipient_emails = reader.get_to_emails()  # ["jane@example.com", "bob@example.com"]
recipient_names = reader.get_to_names()    # ["Jane Smith", "Bob Wilson"]

# Get all recipients with names and emails
for name, email in reader.get_to_parsed():
    print(f"To: {name} <{email}>")

# Same methods available for CC and BCC
cc_emails = reader.get_cc_emails()
bcc_emails = reader.get_bcc_emails()

# Check if email was sent or received
email_type = reader.get_type()  # 'sent' or 'received'

# Get any header by name
content_type = reader.get_header('content-type')
message_id = reader.get_header('message-id')

# Get header with decoding options
decoded_subject = reader.get_header('subject', decode=True, remove_line_breaks=True)
```

### Working with Message Content

```python
# Get plain text content
text_content = reader.get_message_text()
if text_content:
    print("Plain text:")
    print(text_content)

# Get HTML content
html_content = reader.get_message_html()
if html_content:
    print("HTML content:")
    print(html_content)

# Get HTML with inline images as data URLs
html_with_images = reader.get_message_html_with_inline_images(use_data_urls=True)

# Get HTML and save inline images to directory
html_with_images = reader.get_message_html_with_inline_images(save_images_to="./images/")
```

### Handling Attachments

```python
# Get all attachments (excluding inline images)
attachments = reader.get_attachments()

for i, attachment in enumerate(attachments):
    print(f"Attachment {i+1}:")
    print(f"  Filename: {attachment['filename']}")
    print(f"  Content Type: {attachment['content_type']}")
    print(f"  Size: {attachment['filesize']} bytes")
    
    # Save attachment to file
    filename = attachment['filename'] or f"attachment_{i+1}"
    with open(filename, 'wb') as f:
        f.write(attachment['content'])
```

### Working with Inline Images

```python
# Get inline images
inline_images = reader.get_inline_images()

for i, image in enumerate(inline_images):
    print(f"Inline Image {i+1}:")
    print(f"  Filename: {image['filename']}")
    print(f"  Content ID: {image['content_id']}")
    print(f"  Content Type: {image['content_type']}")
    print(f"  Size: {image['filesize']} bytes")
    
    # Save inline image
    filename = image['filename'] or f"inline_image_{i+1}.png"
    with open(filename, 'wb') as f:
        f.write(image['content'])
```

### Advanced Usage

```python
from eml_extractor import EmlReader, MultiPartParser

# Access the underlying MultiPartParser for advanced operations
reader = EmlReader(email_bytes)
parser = reader._multipart_parser

# Get specific content type parts
text_part = parser.get_part_by_content_type('text', 'plain')
html_part = parser.get_part_by_content_type('text', 'html')

# Check if a part is an attachment or inline image
for part in parser.get_multi_parts():
    if part.is_attachment:
        print(f"Found attachment: {part.get_filename()}")
    elif part.is_inline_image:
        print(f"Found inline image: {part.get_filename()}")
```

## API Reference

### EmlReader Class

The main class for parsing .eml files.

#### Constructor

```python
EmlReader(array_buffer: Union[bytes, bytearray])
```

Creates a new EML reader instance.

**Parameters:**
- `array_buffer`: Raw email content as bytes or bytearray

#### Methods

##### Header Methods

- `get_subject() -> Optional[str]`: Get email subject with automatic decoding
- `get_from() -> Optional[str]`: Get From header (raw format with display name and email)
- `get_to() -> Optional[str]`: Get To header (raw format with display names and emails)
- `get_cc() -> Optional[str]`: Get CC header (raw format with display names and emails)
- `get_bcc() -> Optional[str]`: Get BCC header (raw format with display names and emails)
- `get_reply_to() -> Optional[str]`: Get Reply-To header (raw format)
- `get_date() -> Optional[datetime]`: Get email date as datetime object
- `get_type() -> str`: Returns 'sent' or 'received'
- `get_header(key: str, decode: bool = False, remove_line_breaks: bool = False) -> Union[str, List[str], None]`: Get any header value

##### Email Address Parsing Methods (NEW)

**From Header:**
- `get_from_email() -> Optional[str]`: Get only the email address from From header
- `get_from_name() -> Optional[str]`: Get only the display name from From header  
- `get_from_parsed() -> Tuple[Optional[str], Optional[str]]`: Get both display name and email address from From header

**To Header:**
- `get_to_emails() -> List[str]`: Get only the email addresses from To header
- `get_to_names() -> List[str]`: Get only the display names from To header
- `get_to_parsed() -> List[Tuple[Optional[str], Optional[str]]]`: Get both display names and email addresses from To header

**CC Header:**
- `get_cc_emails() -> List[str]`: Get only the email addresses from CC header
- `get_cc_names() -> List[str]`: Get only the display names from CC header
- `get_cc_parsed() -> List[Tuple[Optional[str], Optional[str]]]`: Get both display names and email addresses from CC header

**BCC Header:**
- `get_bcc_emails() -> List[str]`: Get only the email addresses from BCC header
- `get_bcc_names() -> List[str]`: Get only the display names from BCC header
- `get_bcc_parsed() -> List[Tuple[Optional[str], Optional[str]]]`: Get both display names and email addresses from BCC header

**Reply-To Header:**
- `get_reply_to_email() -> Optional[str]`: Get only the email address from Reply-To header
- `get_reply_to_parsed() -> Tuple[Optional[str], Optional[str]]`: Get both display name and email address from Reply-To header

##### Content Methods

- `get_message_text() -> Optional[str]`: Get plain text content
- `get_message_html() -> Optional[str]`: Get HTML content
- `get_message_html_with_inline_images(save_images_to: Optional[str] = None, use_data_urls: bool = False) -> Optional[str]`: Get HTML with inline images processed

##### Attachment Methods

- `get_attachments() -> List[Dict[str, Any]]`: Get all attachments (excluding inline images)
- `get_inline_images() -> List[Dict[str, Any]]`: Get all inline images

### MultiPartParser Class

Low-level parser for MIME multipart content.

#### Constructor

```python
MultiPartParser(raw_content: Union[bytes, bytearray])
```

#### Properties

- `is_attachment -> bool`: Check if this part is an attachment
- `is_inline_image -> bool`: Check if this part is an inline image  
- `content_type -> Optional[str]`: Get the full content type string

#### Methods

- `get_content_type() -> Dict[str, Optional[str]]`: Get content type information
- `get_body() -> Union[bytes, str, None]`: Get the parsed body content
- `get_header(key: str, decode: bool = False, remove_line_breaks: bool = False) -> Union[str, List[str], None]`: Get header value
- `get_multi_parts() -> List[MultiPartParser]`: Get all sub-parts
- `get_filename() -> Optional[str]`: Get filename from headers
- `get_content_id() -> Optional[str]`: Get Content-ID header
- `get_part_by_content_type(media_type: str, sub_type: Optional[str] = None) -> Optional[MultiPartParser]`: Find part by content type

## Examples

### Example 1: Basic Email Information

```python
from eml_extractor import EmlReader
from datetime import datetime

def print_email_info(eml_file_path):
    with open(eml_file_path, 'rb') as f:
        reader = EmlReader(f.read())
    
    print(f"Subject: {reader.get_subject()}")
    print(f"From: {reader.get_from()}")
    print(f"To: {reader.get_to()}")
    
    date = reader.get_date()
    if date:
        print(f"Date: {date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"Type: {reader.get_type()}")
    print(f"Attachments: {len(reader.get_attachments())}")
    print(f"Inline Images: {len(reader.get_inline_images())}")

print_email_info('sample.eml')
```

### Example 2: Extract and Save All Attachments

```python
import os
from eml_extractor import EmlReader

def extract_attachments(eml_file_path, output_dir="attachments"):
    with open(eml_file_path, 'rb') as f:
        reader = EmlReader(f.read())
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract regular attachments
    attachments = reader.get_attachments()
    for i, attachment in enumerate(attachments):
        filename = attachment['filename'] or f"attachment_{i+1}"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(attachment['content'])
        
        print(f"Saved: {filepath} ({attachment['filesize']} bytes)")
    
    # Extract inline images
    inline_images = reader.get_inline_images()
    for i, image in enumerate(inline_images):
        filename = image['filename'] or f"inline_image_{i+1}.png"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(image['content'])
            
        print(f"Saved inline image: {filepath} ({image['filesize']} bytes)")

extract_attachments('email_with_attachments.eml')
```

### Example 3: Convert Email to HTML File

```python
from eml_extractor import EmlReader
import os

def email_to_html(eml_file_path, output_html_path, extract_images=True):
    with open(eml_file_path, 'rb') as f:
        reader = EmlReader(f.read())
    
    # Get HTML content with inline images
    if extract_images:
        # Save images to a subdirectory
        images_dir = os.path.splitext(output_html_path)[0] + "_images"
        html_content = reader.get_message_html_with_inline_images(
            save_images_to=images_dir
        )
    else:
        # Embed images as data URLs
        html_content = reader.get_message_html_with_inline_images(
            use_data_urls=True
        )
    
    if not html_content:
        # Fallback to plain text
        text_content = reader.get_message_text()
        if text_content:
            html_content = f"<pre>{text_content}</pre>"
        else:
            html_content = "<p>No content found</p>"
    
    # Create complete HTML document
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{reader.get_subject() or 'Email'}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 10px; margin-bottom: 20px; }}
        .content {{ line-height: 1.6; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>{reader.get_subject() or 'No Subject'}</h2>
        <p><strong>From:</strong> {reader.get_from() or 'Unknown'}</p>
        <p><strong>To:</strong> {reader.get_to() or 'Unknown'}</p>
        <p><strong>Date:</strong> {reader.get_date() or 'Unknown'}</p>
    </div>
    <div class="content">
        {html_content}
    </div>
</body>
</html>"""
    
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"Email converted to HTML: {output_html_path}")

email_to_html('sample.eml', 'output.html')
```

## Error Handling

The library is designed to handle malformed emails gracefully:

```python
from eml_extractor import EmlReader

try:
    with open('potentially_malformed.eml', 'rb') as f:
        reader = EmlReader(f.read())
    
    # The library will attempt to parse even malformed emails
    subject = reader.get_subject()
    if subject:
        print(f"Subject: {subject}")
    else:
        print("No subject found")
        
except Exception as e:
    print(f"Failed to parse email: {e}")
```

## Requirements

- Python 3.7 or higher
- No external dependencies (uses only Python standard library)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0
- Initial release
- Full EML parsing support
- Attachment extraction
- Inline image handling
- HTML and text content extraction
- Pure Python implementation with no dependencies

## Support

If you encounter any issues or have questions, please file an issue on the [GitHub repository](https://github.com/thvroyal/eml-extractor/issues).

## Acknowledgments

This library is a Python port inspired by JavaScript EML parsing libraries, providing the same functionality with Python-native features and typing support. 