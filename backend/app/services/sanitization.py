"""
Input Sanitization Service
Sanitizes user input to prevent injection attacks
"""

import re
import html
from typing import Any, Dict, List, Union
import logging

logger = logging.getLogger("mediconnect")


class InputSanitizer:
    """
    Service to sanitize user input.
    
    Best Practices:
    - Prevent XSS attacks
    - Prevent SQL/NoSQL injection
    - Validate and sanitize all user input
    - Use whitelist approach when possible
    """
    
    # Dangerous patterns to detect
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',                 # JavaScript protocol
        r'on\w+\s*=',                  # Event handlers
        r'<iframe[^>]*>',              # Iframes
        r'<object[^>]*>',              # Objects
        r'<embed[^>]*>',               # Embeds
        r'\$where',                    # MongoDB injection
        r'\$ne',                       # MongoDB injection
        r'\$gt',                       # MongoDB injection
        r'\$lt',                       # MongoDB injection
    ]
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = None) -> str:
        """
        Sanitize a string value.
        
        Args:
            value: String to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return str(value)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Trim whitespace
        value = value.strip()
        
        # Limit length
        if max_length and len(value) > max_length:
            value = value[:max_length]
            logger.warning(f"String truncated to {max_length} characters")
        
        # HTML escape
        value = html.escape(value)
        
        # Check for dangerous patterns
        for pattern in InputSanitizer.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected: {pattern}")
                value = re.sub(pattern, '', value, flags=re.IGNORECASE)
        
        return value
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """
        Sanitize and validate email address.
        
        Args:
            email: Email address
            
        Returns:
            Sanitized email
        """
        if not isinstance(email, str):
            raise ValueError("Email must be a string")
        
        # Convert to lowercase
        email = email.lower().strip()
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        
        return email
    
    @staticmethod
    def sanitize_phone(phone: str) -> str:
        """
        Sanitize phone number.
        
        Args:
            phone: Phone number
            
        Returns:
            Sanitized phone number
        """
        if not isinstance(phone, str):
            return str(phone)
        
        # Remove all non-digit characters except +
        phone = re.sub(r'[^\d+]', '', phone)
        
        return phone
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any], max_string_length: int = 1000) -> Dict[str, Any]:
        """
        Recursively sanitize dictionary values.
        
        Args:
            data: Dictionary to sanitize
            max_string_length: Maximum string length
            
        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        
        for key, value in data.items():
            # Sanitize key
            safe_key = InputSanitizer.sanitize_string(str(key), max_length=100)
            
            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[safe_key] = InputSanitizer.sanitize_string(value, max_string_length)
            elif isinstance(value, dict):
                sanitized[safe_key] = InputSanitizer.sanitize_dict(value, max_string_length)
            elif isinstance(value, list):
                sanitized[safe_key] = InputSanitizer.sanitize_list(value, max_string_length)
            else:
                sanitized[safe_key] = value
        
        return sanitized
    
    @staticmethod
    def sanitize_list(data: List[Any], max_string_length: int = 1000) -> List[Any]:
        """
        Recursively sanitize list values.
        
        Args:
            data: List to sanitize
            max_string_length: Maximum string length
            
        Returns:
            Sanitized list
        """
        sanitized = []
        
        for value in data:
            if isinstance(value, str):
                sanitized.append(InputSanitizer.sanitize_string(value, max_string_length))
            elif isinstance(value, dict):
                sanitized.append(InputSanitizer.sanitize_dict(value, max_string_length))
            elif isinstance(value, list):
                sanitized.append(InputSanitizer.sanitize_list(value, max_string_length))
            else:
                sanitized.append(value)
        
        return sanitized
    
    @staticmethod
    def validate_mongo_query(query: Dict[str, Any]) -> bool:
        """
        Validate MongoDB query for injection attempts.
        
        Args:
            query: MongoDB query
            
        Returns:
            True if safe, False otherwise
        """
        query_str = str(query)
        
        # Check for dangerous operators
        dangerous_operators = ['$where', '$function', '$accumulator', '$expr']
        for op in dangerous_operators:
            if op in query_str:
                logger.warning(f"Dangerous MongoDB operator detected: {op}")
                return False
        
        return True
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal.
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename
        """
        if not isinstance(filename, str):
            raise ValueError("Filename must be a string")
        
        # Remove path separators
        filename = filename.replace('/', '').replace('\\', '')
        
        # Remove parent directory references
        filename = filename.replace('..', '')
        
        # Remove null bytes
        filename = filename.replace('\x00', '')
        
        # Allow only alphanumeric, dash, underscore, and dot
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        
        return filename


# Global sanitizer instance
sanitizer = InputSanitizer()
