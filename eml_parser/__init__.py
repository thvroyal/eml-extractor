"""
EML Parser - A Python library for parsing .eml email files

This library provides a clean API for parsing .eml files, extracting email headers,
body content, attachments, and inline images.

Copyright © 2025
@author  thvroyal, thvroyal@gmail.com
@license MIT
@date    2025-07-21
"""

from .parser import EmlReader, MultiPartParser

__version__ = "1.0.0"
__author__ = "thvroyal"
__email__ = "thvroyal@gmail.com"
__license__ = "MIT"

# Main exports
__all__ = ["EmlReader", "MultiPartParser"] 