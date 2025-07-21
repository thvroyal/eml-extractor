# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### Added
- Initial release of EML Extractor
- Full EML file parsing support
- Email header extraction (From, To, Subject, Date, etc.)
- Email body extraction (plain text and HTML)
- Attachment extraction and saving
- Inline image extraction and handling
- Support for various character encodings
- Content transfer encoding support (base64, quoted-printable)
- Type hints for better IDE support
- Comprehensive test suite
- Example scripts for common use cases
- GitHub Actions workflows for automated testing and publishing

### Features
- **Pure Python**: No external dependencies, uses only Python standard library
- **Multi-format Support**: Handles multipart emails, attachments, and inline images
- **Encoding Support**: Automatic handling of various text encodings and transfer encodings
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Python 3.7+**: Compatible with Python 3.7 through 3.12

### Documentation
- Comprehensive README with examples and API reference
- Example scripts demonstrating core functionality
- Setup instructions for automated publishing
- Issue and pull request templates 