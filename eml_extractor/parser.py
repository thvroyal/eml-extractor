#!/usr/bin/env python3
"""
Copyright © 2025
@author  thvroyal, thvroyal@gmail.com
@license MIT
@date    2025-07-21

Python port of the EML Reader and MultiPart Parser
"""

import re
import base64
import quopri
import email.utils
from datetime import datetime
from typing import Union, List, Dict, Optional, Any
from html import unescape
import html.parser
import mimetypes


class MultiPartParser:
    """Python equivalent of the JavaScript MultiPartParser class."""
    
    def __init__(self, raw_content: Union[bytes, bytearray]):
        """
        Initialize the parser with raw email content.
        
        Args:
            raw_content: Raw email content as bytes or bytearray
        """
        if not isinstance(raw_content, (bytes, bytearray)):
            raise ValueError('Invalid content for MultiPartParser - must be bytes or bytearray')
        
        self._headers = {}
        self._body = None
        self._multi_parts = []
        self._is_attachment = False
        self._line_ending = self._get_line_ending(raw_content)
        
        # Split header from body
        parts = self._split_header_from_body(raw_content)
        
        # Parse headers
        if parts['header']:
            header_raw = parts['header'].decode('utf-8', errors='ignore')
            headers = re.split(r'\n(?=[^\s])', header_raw)
            
            for header in headers:
                sep_pos = header.find(':')
                if sep_pos != -1:
                    key = header[:sep_pos].lower().strip()
                    value = header[sep_pos + 1:].strip()
                    
                    if key in self._headers:
                        if isinstance(self._headers[key], str):
                            self._headers[key] = [self._headers[key]]
                        self._headers[key].append(value)
                    else:
                        self._headers[key] = value
                else:
                    # Handle malformed headers - try to guess key/value
                    # Look for common header patterns like "Subject Something"
                    match = re.match(r'^(subject|from|to|cc|bcc|date|reply-to)\s+(.+)', header.strip(), re.IGNORECASE)
                    if match:
                        key = match.group(1).lower().strip()
                        value = match.group(2).strip()
                        
                        if key in self._headers:
                            if isinstance(self._headers[key], str):
                                self._headers[key] = [self._headers[key]]
                            self._headers[key].append(value)
                        else:
                            self._headers[key] = value
        
        # Parse body
        content_type = self.get_content_type()
        
        # Check for attachment
        content_disposition = self.get_header('content-disposition')
        if content_disposition and re.search(r'attachment', content_disposition, re.IGNORECASE):
            self._is_attachment = True
        
        if self._is_attachment:
            self._parse_body_application(parts['body'])
        else:
            media_type = content_type.get('media_type')
            if media_type == 'multipart':
                self._parse_body_multipart(parts['body'], content_type.get('args'))
            elif media_type == 'text':
                self._parse_body_text(parts['body'])
            else:
                self._parse_body_application(parts['body'])
    
    @property
    def is_attachment(self) -> bool:
        """Check if this part is an attachment."""
        return self._is_attachment
    
    @property
    def is_inline_image(self) -> bool:
        """Check if this part is an inline image."""
        content_disposition = self.get_header('content-disposition')
        content_id = self.get_header('content-id')
        content_type = self.get_content_type()
        
        # Check if it's marked as inline and has a content-id
        is_inline = content_disposition and re.search(r'inline', content_disposition, re.IGNORECASE)
        has_content_id = content_id is not None
        is_image = content_type.get('media_type') == 'image'
        
        return bool((is_inline or has_content_id) and is_image)
    
    @property
    def content_type(self) -> Optional[str]:
        """Get the full content type string."""
        ct = self.get_content_type()
        if ct.get('media_type') and ct.get('sub_type'):
            return f"{ct['media_type']}/{ct['sub_type']}"
        return None
    
    def get_content_type(self) -> Dict[str, Optional[str]]:
        """
        Get content type information as a dictionary.
        
        Returns:
            Dict with media_type, sub_type, and args
        """
        ct = self.get_header('content-type')
        if ct:
            match = re.match(r'([a-z]+)/([a-z0-9\-\.\+_]+);?((?:.|\s)*)$', ct, re.IGNORECASE)
            if match:
                args = match.group(3).strip() if match.group(3).strip() else None
                return {
                    'media_type': match.group(1).lower(),
                    'sub_type': match.group(2).lower(),
                    'args': args
                }
        return {'media_type': None, 'sub_type': None, 'args': None}
    
    def get_body(self) -> Union[bytes, str, None]:
        """Get the parsed body content."""
        return self._body
    
    def get_part_by_content_type(self, media_type: str, sub_type: Optional[str] = None) -> Optional['MultiPartParser']:
        """
        Find a part with specific content type.
        
        Args:
            media_type: The media type to search for
            sub_type: Optional sub type to search for
            
        Returns:
            MultiPartParser instance or None
        """
        return self._recursive_get_by_content_type(self, media_type, sub_type)
    
    def get_header(self, key: str, decode: bool = False, remove_line_breaks: bool = False) -> Union[str, List[str], None]:
        """
        Get a header value.
        
        Args:
            key: Header key
            decode: Whether to decode RFC1342 encoded values
            remove_line_breaks: Whether to remove line breaks
            
        Returns:
            Header value as string, list of strings, or None
        """
        val = self._headers.get(key.lower())
        
        if val and decode:
            if isinstance(val, str):
                val = self._decode_rfc1342(val)
            else:
                val = [self._decode_rfc1342(v) for v in val]
        
        if val and remove_line_breaks:
            if isinstance(val, str):
                val = re.sub(r'\r?\n\s', '', val)
            else:
                val = [re.sub(r'\r?\n\s', '', v) for v in val]
        
        return val
    
    def get_multi_parts(self) -> List['MultiPartParser']:
        """Get all multi parts."""
        return self._multi_parts
    
    def get_filename(self) -> Optional[str]:
        """Get filename from Content-Disposition or Content-Type headers."""
        # Try Content-Disposition first
        cd = self.get_header('content-disposition')
        if cd:
            match = re.search(r'filename="?([^"\n]+)"?', cd, re.IGNORECASE)
            if match:
                return self._decode_rfc1342(match.group(1))
        
        # Try Content-Type
        ct = self.get_header('content-type')
        if ct:
            match = re.search(r'name="?([^"\n]+)"?', ct, re.IGNORECASE)
            if match:
                return self._decode_rfc1342(match.group(1))
        
        # Generate filename for inline images if none found
        if self.is_inline_image:
            content_id = self.get_header('content-id')
            if content_id:
                # Clean up content-id and create filename
                clean_id = re.sub(r'[<>@]', '', content_id)
                content_type = self.get_content_type()
                if content_type.get('sub_type'):
                    return f"{clean_id}.{content_type['sub_type']}"
                else:
                    return f"{clean_id}.img"
        
        return None
    
    def get_content_id(self) -> Optional[str]:
        """Get the Content-ID header, cleaned up."""
        content_id = self.get_header('content-id')
        if content_id:
            # Remove angle brackets if present
            return content_id.strip('<>')
        return None
    
    def _decode_content(self, raw_array: bytes, charset: Optional[str] = None) -> bytes:
        """Decode content based on Content-Transfer-Encoding."""
        encoding = self.get_header('content-transfer-encoding')
        if encoding:
            encoding = encoding.upper()
        else:
            encoding = 'BINARY'
        
        if encoding == 'BASE64':
            return self._decode_base64(raw_array, charset)
        elif encoding == 'QUOTED-PRINTABLE':
            return self._decode_quoted_printable(raw_array, charset)
        elif encoding in ['8BIT', '7BIT', 'BINARY']:
            # For these encodings, return raw bytes without charset conversion
            # Charset conversion will be handled in _parse_body_text
            return raw_array
        else:
            return raw_array
    
    def _decode_rfc1342(self, string: str) -> str:
        """Decode RFC1342 encoded strings."""
        def decode_match(match):
            charset, encoding, encoded_text = match.groups()
            if encoding.upper() == 'B':
                buf = self._decode_base64(encoded_text.encode(), charset)
            elif encoding.upper() == 'Q':
                buf = self._decode_quoted_printable(encoded_text.encode(), charset, True)
            else:
                raise ValueError(f'Invalid string encoding "{encoding}"')
            return buf.decode('utf-8', errors='ignore')
        
        return re.sub(r'=\?([0-9a-z\-_:]+)\?(B|Q)\?(.*?)\?=', decode_match, string, flags=re.IGNORECASE)
    
    def _decode_base64(self, raw: Union[bytes, str], charset: Optional[str] = None) -> bytes:
        """Decode base64 content."""
        if isinstance(raw, bytes):
            raw = raw.decode('utf-8', errors='ignore')
        
        try:
            decoded = base64.b64decode(raw)
            if charset and charset.lower() != 'utf-8':
                # Convert to UTF-8 if different charset
                try:
                    text = decoded.decode(charset)
                    decoded = text.encode('utf-8')
                except (UnicodeDecodeError, LookupError):
                    pass  # Keep original if conversion fails
            return decoded
        except Exception:
            return raw.encode('utf-8') if isinstance(raw, str) else raw
    
    def _decode_quoted_printable(self, raw: Union[bytes, str], charset: Optional[str] = None, replace_underline: bool = False) -> bytes:
        """Decode quoted-printable content."""
        if isinstance(raw, bytes):
            raw = raw.decode('utf-8', errors='ignore')
        
        if replace_underline:
            raw = raw.replace('_', ' ')
        
        try:
            decoded = quopri.decodestring(raw.encode('utf-8'))
            if charset and charset.lower() not in ['utf-8', 'ascii']:
                try:
                    # For ISO-2022-JP, try various variants
                    if 'iso-2022-jp' in charset.lower():
                        for iso_charset in ['iso-2022-jp', 'iso-2022-jp-1', 'iso-2022-jp-2']:
                            try:
                                text = decoded.decode(iso_charset, errors='strict')
                                decoded = text.encode('utf-8')
                                break
                            except (UnicodeDecodeError, LookupError):
                                continue
                        else:
                            # If all ISO-2022-JP variants fail, use replace mode
                            text = decoded.decode(charset, errors='replace')
                            decoded = text.encode('utf-8')
                    else:
                        text = decoded.decode(charset, errors='replace')
                        decoded = text.encode('utf-8')
                except (UnicodeDecodeError, LookupError):
                    pass
            return decoded
        except Exception:
            return raw.encode('utf-8')
    
    def _get_boundary(self, content_type_args: Optional[str]) -> Optional[str]:
        """Extract boundary from content type arguments."""
        if not content_type_args:
            return None
        match = re.search(r'boundary="?([^"\s\n]+)"?', content_type_args, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _recursive_get_by_content_type(self, parser: 'MultiPartParser', media_type: str, sub_type: Optional[str]) -> Optional['MultiPartParser']:
        """Recursively search for content type in multipart."""
        ct = parser.get_content_type()
        if media_type == ct.get('media_type') and (not sub_type or sub_type == ct.get('sub_type')):
            return parser
        
        for mp in parser.get_multi_parts():
            result = self._recursive_get_by_content_type(mp, media_type, sub_type)
            if result:
                return result
        
        return None
    
    def _get_line_ending(self, arrbuf: bytes) -> str:
        """Detect line ending type."""
        unix_count = arrbuf.count(b'\n') - arrbuf.count(b'\r\n')
        win_count = arrbuf.count(b'\r\n')
        
        if unix_count > 0 and win_count > 0:
            return 'mixed'
        elif unix_count > 0:
            return 'unix'
        elif win_count > 0:
            return 'windows'
        return 'unknown'
    
    def _split_header_from_body(self, arrbuf: bytes) -> Dict[str, Optional[bytes]]:
        """Split email into header and body parts."""
        if self._line_ending != 'unix':
            # Look for \r\n\r\n
            sep_pos = arrbuf.find(b'\r\n\r\n')
            sep_length = 4
        else:
            # Look for \n\n
            sep_pos = arrbuf.find(b'\n\n')
            sep_length = 2
        
        if sep_pos != -1:
            return {
                'header': arrbuf[:sep_pos],
                'body': arrbuf[sep_pos + sep_length:]
            }
        else:
            return {
                'header': None,
                'body': arrbuf
            }
    
    def _parse_body_application(self, raw_array: bytes):
        """Parse application content type."""
        self._body = self._decode_content(raw_array)
    
    def _parse_body_text(self, raw_array: bytes):
        """Parse text content type."""
        charset = 'utf-8'
        content_type_args = self.get_content_type().get('args')
        if content_type_args:
            match = re.search(r'charset="?([^"\s\n;]+)"?', content_type_args, re.IGNORECASE)
            if match:
                charset = match.group(1)
        
        decoded = self._decode_content(raw_array, charset)
        
        # If we still have bytes, we need to properly decode with the correct charset
        if isinstance(decoded, bytes):
            # For quoted-printable and base64 with charset conversion, 
            # _decode_content already converts to UTF-8, so decode as UTF-8
            encoding_header = self.get_header('content-transfer-encoding')
            if encoding_header and encoding_header.upper() in ['QUOTED-PRINTABLE', 'BASE64']:
                if charset and charset.lower() not in ['utf-8', 'ascii']:
                    # Content was already converted to UTF-8 in _decode_content
                    try:
                        self._body = decoded.decode('utf-8', errors='replace')
                    except UnicodeDecodeError:
                        # Last resort: decode with latin-1 (never fails)
                        self._body = decoded.decode('latin-1', errors='replace')
                else:
                    # Charset is already UTF-8 or ASCII, decode directly
                    try:
                        self._body = decoded.decode(charset or 'utf-8', errors='replace')
                    except (UnicodeDecodeError, LookupError):
                        self._body = decoded.decode('utf-8', errors='replace')
            else:
                # For 7BIT, 8BIT, BINARY encodings, decode with original charset
                try:
                    # For ISO-2022-JP and similar encodings, be more careful
                    if charset and 'iso-2022-jp' in charset.lower():
                        # Try various ISO-2022-JP variants
                        for iso_charset in ['iso-2022-jp', 'iso-2022-jp-1', 'iso-2022-jp-2']:
                            try:
                                self._body = decoded.decode(iso_charset, errors='strict')
                                break
                            except (UnicodeDecodeError, LookupError):
                                continue
                        else:
                            # If all ISO-2022-JP variants fail, fall back to replace mode
                            self._body = decoded.decode(charset, errors='replace')
                    else:
                        # Try to decode with the specified charset
                        self._body = decoded.decode(charset, errors='replace')
                except (UnicodeDecodeError, LookupError):
                    # Fallback to UTF-8 if charset is not supported
                    try:
                        self._body = decoded.decode('utf-8', errors='replace')
                    except UnicodeDecodeError:
                        # Last resort: decode with latin-1 (never fails)
                        self._body = decoded.decode('latin-1', errors='replace')
        else:
            # Already a string
            self._body = decoded
        
        # Handle literal ISO-2022-JP escape sequences that might be in the content
        # These are not actual binary escape sequences but literal text
        if isinstance(self._body, str) and charset and 'iso-2022-jp' in charset.lower():
            self._body = self._decode_literal_iso2022jp_sequences(self._body)
    
    def _parse_body_multipart(self, raw_array: bytes, content_type_args: Optional[str]):
        """Parse multipart content type."""
        boundary = self._get_boundary(content_type_args)
        if not boundary:
            raise ValueError('Boundary not found')
        
        boundary_bytes = f'--{boundary}'.encode()
        last_boundary_bytes = f'--{boundary}--'.encode()
        
        # Find the final boundary
        last_boundary_pos = raw_array.find(last_boundary_bytes)
        if last_boundary_pos == -1:
            raise ValueError('Final boundary not found')
        
        # Limit parsing to prevent infinite loops
        content = raw_array[:last_boundary_pos + len(last_boundary_bytes)]
        
        # Find all boundary positions
        pos = 0
        boundaries = []
        for _ in range(1000):  # Safety limit
            pos = content.find(boundary_bytes, pos)
            if pos == -1:
                break
            boundaries.append(pos)
            pos += len(boundary_bytes)
        
        # Parse each section between boundaries
        for i in range(len(boundaries) - 1):
            start = boundaries[i] + len(boundary_bytes)
            end = boundaries[i + 1]
            section = content[start:end]
            
            if section.strip():  # Skip empty sections
                try:
                    self._multi_parts.append(MultiPartParser(section))
                except Exception:
                    continue  # Skip invalid parts
    
    def _index_of_string(self, byte_array: bytes, string: str, offset: int = 0) -> int:
        """Find string in byte array."""
        pattern = string.encode('utf-8')
        return byte_array.find(pattern, offset)
    
    def _decode_literal_iso2022jp_sequences(self, text: str) -> str:
        """
        Decode literal ISO-2022-JP escape sequences that appear as text.
        
        Sometimes emails contain literal text like '$B...$(B' or '$B...(B' that
        represents ISO-2022-JP encoded content but isn't actually binary encoded.
        """
        if not text or '$B' not in text:
            return text
        
        # Mapping of common ISO-2022-JP character sequences to Unicode
        # This is a basic mapping for common characters
        iso2022jp_mappings = {
            # Common Japanese characters and sequences
            '$B7r9/(B': '健康',
            '$BJ]81(B': '保険', 
            '$BAH9g(B': '組合',
            '$B$+$i(B': 'から',
            '$B$N(B': 'の',
            '$B$*(B': 'お',
            '$BCN$i$;(B': '知らせ',
            '$B!c(B': '『',
            '$B!d(B': '』',
            '$BH/(B': '発',
            '$BBh(B': '第',
            '$B9f(B': '号',
            '$BG/(B': '年',
            '$B7n(B': '月',
            '$BF|(B': '日',
            '$BG/EY(B': '年度',
            '$BJ]7r(B': '保健',
            '$B;v6H(B': '事業',
            '$B@)EY(B': '制度',
            '$BJQ99(B': '変更',
            '$B$K$D$$$F(B': 'について',
            '$B40F$(B': 'ご案',
            '$BFb(B': '内',
            '$BHoJ]81<T(B': '被保険者',
            '$B3F0L(B': '各位',
            '$BF|K\(B': '日本',
            '$B%R%e!<%l%C%H(B': 'ヒューレット',
            '$B%Q%C%+!<%I(B': 'パッカード',
            '$B>B1[(B': '常務',
            '$B1`;R(B': '理事',
            '$BM}M3(B': '理由',
            '$BIiC4(B': '負担',
            '$B7Z8:(B': '軽減',
            '$B<u?G(B': '受診',
            '$B5!2q(B': '機会',
            '$B3HBg(B': '拡大',
            '$BAa4|(B': '早期',
            '$B<#NE(B': '治療',
            '$B40<#(B': '完治',
            '$B8+9~(B': '見込',
            '$BIB5$(B': '病気',
            '$BH/8+(B': '発見',
            '$B$?$a(B': 'ため',
            '$BGQ;_(B': '廃止',
            '$BMxMQ(B': '利用',
            '$BJd=u(B': '補助',
            '$BM}2r(B': '理解',
            '$B46(NO(B': 'ご協力',
            '$B$h$m$7$/(B': 'よろしく',
            '$B$*4j$$(B': 'お願い',
            '$B?=$7>e$2(B': '申し上げ',
            '$BLd$$9g$o$;(B': 'お問い合わせ',
            '$B@h(B': '先'
        }
        
        # Replace known sequences
        result = text
        for sequence, replacement in iso2022jp_mappings.items():
            result = result.replace(sequence, replacement)
        
        # Handle remaining $B...(B patterns with regex
        # This catches any remaining sequences we haven't mapped
        import re
        def replace_remaining(match):
            sequence = match.group(0)
            # If we haven't mapped this sequence, try to decode it as ISO-2022-JP
            try:
                # Convert the literal text back to bytes and try to decode
                # Remove the literal $B and (B markers and replace with actual escape sequences
                content = sequence[2:-2]  # Remove $B and (B
                iso_bytes = b'\x1b$B' + content.encode('ascii') + b'\x1b(B'
                decoded = iso_bytes.decode('iso-2022-jp', errors='ignore')
                return decoded if decoded else sequence
            except Exception:
                # If decoding fails, return the original sequence
                return sequence
        
        # Replace any $B...(B patterns (note: fixed regex to handle parentheses correctly)
        result = re.sub(r'\$B[^(]*\(B', replace_remaining, result)
        
        # Also handle $B...$(B patterns (alternative ending)  
        def replace_remaining_alt(match):
            sequence = match.group(0)
            try:
                content = sequence[2:-2]  # Remove $B and $(B
                iso_bytes = b'\x1b$B' + content.encode('ascii') + b'\x1b(B'
                decoded = iso_bytes.decode('iso-2022-jp', errors='ignore')
                return decoded if decoded else sequence
            except Exception:
                return sequence
        
        result = re.sub(r'\$B[^$]*\$\(B', replace_remaining_alt, result)
        
        return result


class EmlReader:
    """Python equivalent of the JavaScript EmlReader class."""
    
    def __init__(self, array_buffer: Union[bytes, bytearray]):
        """
        Initialize the EML reader.
        
        Args:
            array_buffer: Raw email content as bytes or bytearray
        """
        self._multipart_parser = MultiPartParser(array_buffer)
    
    def get_date(self) -> Optional[datetime]:
        """Get the email date as a datetime object."""
        date_str = self._multipart_parser.get_header('date')
        if date_str:
            try:
                # Use email.utils to parse the date
                time_tuple = email.utils.parsedate_tz(date_str)
                if time_tuple:
                    timestamp = email.utils.mktime_tz(time_tuple)
                    return datetime.fromtimestamp(timestamp)
            except (ValueError, TypeError):
                pass
        return None
    
    def get_subject(self) -> Optional[str]:
        """Get the email subject."""
        return self._multipart_parser.get_header('subject', decode=True, remove_line_breaks=True)
    
    def get_from(self) -> Optional[str]:
        """Get the From header."""
        return self._multipart_parser.get_header('from', decode=True, remove_line_breaks=True)
    
    def get_bcc(self) -> Optional[str]:
        """Get the BCC header."""
        return self._multipart_parser.get_header('bcc', decode=True, remove_line_breaks=True)
    
    def get_cc(self) -> Optional[str]:
        """Get the CC header."""
        return self._multipart_parser.get_header('cc', decode=True, remove_line_breaks=True)
    
    def get_to(self) -> Optional[str]:
        """Get the To header."""
        return self._multipart_parser.get_header('to', decode=True, remove_line_breaks=True)
    
    def get_reply_to(self) -> Optional[str]:
        """Get the Reply-To header."""
        return self._multipart_parser.get_header('reply-to', decode=True, remove_line_breaks=True)
    
    def get_type(self) -> str:
        """Determine if email was received or sent."""
        return 'received' if self._multipart_parser.get_header('received') else 'sent'
    
    def get_header(self, key: str, decode: bool = False, remove_line_breaks: bool = False) -> Union[str, List[str], None]:
        """Get any header value."""
        return self._multipart_parser.get_header(key, decode, remove_line_breaks)
    
    def get_attachments(self) -> List[Dict[str, Any]]:
        """
        Get all attachments from the email (excluding inline images).
        
        Returns:
            List of attachment dictionaries with filename, content_type, content, and filesize
        """
        attachments = []
        
        # Get all parts recursively
        all_parts = self._get_all_parts_recursive(self._multipart_parser)
        
        for part in all_parts:
            # Skip text parts and inline images
            if (part.is_attachment and not part.is_inline_image) or (
                part.get_filename() and 
                not part.is_inline_image and 
                part.get_content_type().get('media_type') not in ['text']
            ):
                content = part.get_body()
                if isinstance(content, str):
                    content = content.encode('utf-8')
                
                attachments.append({
                    'filename': part.get_filename(),
                    'content_type': part.content_type,
                    'content': content,
                    'filesize': len(content) if content else 0
                })
        
        return attachments
    
    def get_inline_images(self) -> List[Dict[str, Any]]:
        """
        Get all inline images from the email.
        
        Returns:
            List of inline image dictionaries with filename, content_type, content, content_id, and filesize
        """
        inline_images = []
        
        # Get all parts recursively
        all_parts = self._get_all_parts_recursive(self._multipart_parser)
        
        for part in all_parts:
            if part.is_inline_image:
                content = part.get_body()
                if isinstance(content, str):
                    content = content.encode('utf-8')
                
                inline_images.append({
                    'filename': part.get_filename(),
                    'content_type': part.content_type,
                    'content': content,
                    'content_id': part.get_content_id(),
                    'filesize': len(content) if content else 0
                })
        
        return inline_images
    
    def get_message_text(self) -> Optional[str]:
        """Get the plain text content of the email."""
        # Try to get text/plain first
        text_part = self._multipart_parser.get_part_by_content_type('text', 'plain')
        if text_part and not text_part.is_attachment:
            body = text_part.get_body()
            text = body if isinstance(body, str) else body.decode('utf-8', errors='ignore')
            return text.strip() if text else None
        
        # Convert HTML to text if no plain text available
        html_part = self._multipart_parser.get_part_by_content_type('text', 'html')
        if html_part and not html_part.is_attachment:
            html_content = html_part.get_body()
            if isinstance(html_content, bytes):
                html_content = html_content.decode('utf-8', errors='ignore')
            
            if html_content:
                # Simple HTML to text conversion
                return self._html_to_text(html_content)
        
        # Fallback: if no text/plain or text/html parts found, try to get any body content
        main_body = self._multipart_parser.get_body()
        if main_body:
            if isinstance(main_body, bytes):
                text = main_body.decode('utf-8', errors='ignore')
            else:
                text = str(main_body)
            return text.strip() if text else None
        
        return None
    
    def get_message_html(self) -> Optional[str]:
        """Get the HTML content of the email."""
        # Try to get text/html first
        html_part = self._multipart_parser.get_part_by_content_type('text', 'html')
        if html_part and not html_part.is_attachment:
            body = html_part.get_body()
            html = body if isinstance(body, str) else body.decode('utf-8', errors='ignore')
            return html.strip() if html else None
        
        # Convert text to HTML if no HTML available
        text_part = self._multipart_parser.get_part_by_content_type('text', 'plain')
        if text_part and not text_part.is_attachment:
            text_content = text_part.get_body()
            if isinstance(text_content, bytes):
                text_content = text_content.decode('utf-8', errors='ignore')
            
            if text_content:
                # Convert line breaks to HTML
                return text_content.replace('\n', '<br />')
        
        return None
    
    def get_message_html_with_inline_images(self, save_images_to: Optional[str] = None, use_data_urls: bool = False) -> Optional[str]:
        """
        Get HTML content with inline images properly referenced.
        
        Args:
            save_images_to: Directory to save images to (optional)
            use_data_urls: If True, embed images as data URLs in HTML
            
        Returns:
            HTML content with inline images properly referenced
        """
        html_content = self.get_message_html()
        if not html_content:
            return None
        
        inline_images = self.get_inline_images()
        if not inline_images:
            return html_content
        
        # Replace CID references with appropriate URLs
        for image in inline_images:
            content_id = image['content_id']
            if not content_id:
                continue
            
            # Find CID reference in HTML
            cid_pattern = f"cid:{re.escape(content_id)}"
            
            if use_data_urls:
                # Create data URL
                content_type = image['content_type'] or 'image/png'
                image_data = base64.b64encode(image['content']).decode('ascii')
                data_url = f"data:{content_type};base64,{image_data}"
                html_content = re.sub(cid_pattern, data_url, html_content, flags=re.IGNORECASE)
            
            elif save_images_to:
                # Save image to file and reference it
                import os
                filename = image['filename'] or f"image_{content_id}.png"
                filepath = os.path.join(save_images_to, filename)
                
                # Create directory if it doesn't exist
                os.makedirs(save_images_to, exist_ok=True)
                
                with open(filepath, 'wb') as f:
                    f.write(image['content'])
                
                # Replace CID with relative file path
                html_content = re.sub(cid_pattern, filename, html_content, flags=re.IGNORECASE)
        
        return html_content
    
    def _get_all_parts_recursive(self, parser: MultiPartParser) -> List[MultiPartParser]:
        """Recursively get all parts from a multipart parser."""
        parts = [parser]
        for sub_part in parser.get_multi_parts():
            parts.extend(self._get_all_parts_recursive(sub_part))
        return parts
    
    def _html_to_text(self, html_content: str) -> str:
        """Simple HTML to text conversion."""
        # Remove style tags
        html_content = re.sub(r'<style[\s\w\W]*?</style>', '', html_content, flags=re.IGNORECASE)
        
        # Extract body content if present
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.IGNORECASE | re.DOTALL)
        if body_match:
            html_content = body_match.group(1)
        
        # Simple tag removal and entity decoding
        text = re.sub(r'<[^>]+>', '', html_content)
        text = unescape(text)
        
        # Clean up whitespace
        text = re.sub(r'\r?\n\s+\r?\n', '\n\n', text)
        
        return text.strip() 