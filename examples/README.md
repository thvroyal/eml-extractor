# EML Extractor Examples

This directory contains example scripts demonstrating various features of the EML Extractor library.

## Available Examples

### 1. basic_usage.py

Demonstrates basic email parsing functionality including:
- Reading email headers (subject, from, to, date, etc.)
- Extracting text and HTML content
- Detecting attachments and inline images
- Displaying email metadata

**Usage:**
```bash
python basic_usage.py email.eml
```

### 2. extract_attachments.py

Shows how to extract and save all attachments and inline images from an email:
- Saves regular attachments to the output directory
- Saves inline images to a subdirectory
- Handles filename conflicts automatically
- Provides detailed information about extracted files

**Usage:**
```bash
python extract_attachments.py email.eml [output_directory]
```

### 3. email_to_html.py

Converts an EML file to a standalone HTML file:
- Creates a complete HTML document with styling
- Handles inline images (embed as data URLs or save as files)
- Includes email headers in a formatted header section
- Lists attachments in the HTML output

**Usage:**
```bash
python email_to_html.py email.eml [output.html] [--embed-images]
```

## Sample Email Files

The directory also contains sample .eml files for testing:
- `email.eml` - Basic email example
- `email-2.eml` - Additional email example

## Running the Examples

Make sure you have the EML Extractor library installed or available in your Python path. If running from the source directory, the examples will automatically add the parent directory to the path.

All example scripts include help text when run without arguments or with invalid parameters. 