"""
Input Sanitization Service
Protects against XSS, NoSQL injection, and other input-based attacks
"""

import re
import html
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger("mediconnect")


class InputSanitizer:
    """
    Comprehensive input sanitization for security.
    
    Protects against:
    - XSS (Cross-Site Scripting)
    - NoSQL injection
    - SQL injection
    - Directory traversal
    - Script injection
    """
    
    # Dangerous patterns to detect
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe',
        r'<object',
        r'<embed',
        r'<applet',
    ]
    
    # MongoDB operators that could be dangerous
    MONGO_OPERATORS = [
        '$where', '$regex', '$expr', '$function',
        '$accumulator', '$addFields', '$bucket',
    ]
    
    # SQL keywords
    SQL_KEYWORDS = [
        'DROP', 'DELETE', 'INSERT', 'UPDATE', 'EXEC',
        'UNION', 'SELECT', '--', ';--', '/*', '*/',
    ]
    
    def __init__(self):
        self.xss_pattern = re.compile('|'.join(self.XSS_PATTERNS), re.IGNORECASE)
    
    def sanitize_string(
        self,
        value: str,
        max_length: Optional[int] = None,
        allow_html: bool = False
    ) -> str:
        """
        Sanitize a string input.
        
        Args:
            value: String to sanitize
            max_length: Maximum allowed length
            allow_html: Whether to allow HTML (escaped)
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return str(value)
        
        # Trim whitespace
        value = value.strip()
        
        # Enforce max length
        if max_length and len(value) > max_length:
            value = value[:max_length]
            logger.warning(f"String truncated to {max_length} characters")
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # HTML escape if not allowing HTML
        if not allow_html:
            value = html.escape(value)
        
        # Check for XSS patterns
        if self.xss_pattern.search(value):
            logger.warning(f"XSS pattern detected in input: {value[:50]}...")
            # Remove dangerous patterns
            value = self.xss_pattern.sub('', value)
        
        return value
    
    def sanitize_email(self, email: str) -> str:
        """
        Sanitize and validate email address.
        
        Args:
            email: Email to sanitize
            
        Returns:
            Sanitized email in lowercase
        """
        if not isinstance(email, str):
            return ""
        
        # Convert to lowercase
        email = email.lower().strip()
        
        # Remove dangerous characters
        email = re.sub(r'[<>"\']', '', email)
        
        # Basic email validation
        email_pattern = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
        if not re.match(email_pattern, email):
            logger.warning(f"Invalid email format: {email}")
        
        return email
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal.
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Safe filename
        """
        if not isinstance(filename, str):
            return "file"
        
        # Remove path separators
        filename = filename.replace('/', '').replace('\\', '')
        
        # Remove parent directory references
        filename = filename.replace('..', '')
        
        # Remove null bytes
        filename = filename.replace('\x00', '')
        
        # Keep only safe characters
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Ensure it's not empty
        if not filename:
            filename = "file"
        
        return filename
    
    def sanitize_dict(
        self,
        data: Dict[str, Any],
        max_string_length: int = 10000
    ) -> Dict[str, Any]:
        """
        Recursively sanitize all strings in a dictionary.
        
        Args:
            data: Dictionary to sanitize
            max_string_length: Max length for strings
            
        Returns:
            Sanitized dictionary
        """
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            # Sanitize key
            safe_key = self.sanitize_string(str(key), max_length=100)
            
            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[safe_key] = self.sanitize_string(
                    value,
                    max_length=max_string_length
                )
            elif isinstance(value, dict):
                sanitized[safe_key] = self.sanitize_dict(value, max_string_length)
            elif isinstance(value, list):
                sanitized[safe_key] = self.sanitize_list(value, max_string_length)
            else:
                sanitized[safe_key] = value
        
        return sanitized
    
    def sanitize_list(
        self,
        data: List[Any],
        max_string_length: int = 10000
    ) -> List[Any]:
        """
        Recursively sanitize all strings in a list.
        
        Args:
            data: List to sanitize
            max_string_length: Max length for strings
            
        Returns:
            Sanitized list
        """
        if not isinstance(data, list):
            return data
        
        sanitized = []
        for item in data:
            if isinstance(item, str):
                sanitized.append(self.sanitize_string(
                    item,
                    max_length=max_string_length
                ))
            elif isinstance(item, dict):
                sanitized.append(self.sanitize_dict(item, max_string_length))
            elif isinstance(item, list):
                sanitized.append(self.sanitize_list(item, max_string_length))
            else:
                sanitized.append(item)
        
        return sanitized
    
    def validate_mongo_query(self, query: Dict[str, Any]) -> bool:
        """
        Validate MongoDB query for dangerous operators.
        
        Args:
            query: MongoDB query to validate
            
        Returns:
            True if safe, False if dangerous
        """
        if not isinstance(query, dict):
            return True
        
        # Check for dangerous operators
        query_str = str(query).lower()
        for operator in self.MONGO_OPERATORS:
            if operator.lower() in query_str:
                logger.warning(f"Dangerous MongoDB operator detected: {operator}")
                return False
        
        # Recursively check nested queries
        for key, value in query.items():
            if isinstance(value, dict):
                if not self.validate_mongo_query(value):
                    return False
        
        return True
    
    def check_sql_injection(self, value: str) -> bool:
        """
        Check if string contains SQL injection patterns.
        
        Args:
            value: String to check
            
        Returns:
            True if SQL injection detected, False otherwise
        """
        if not isinstance(value, str):
            return False
        
        value_upper = value.upper()
        for keyword in self.SQL_KEYWORDS:
            if keyword in value_upper:
                logger.warning(f"SQL injection pattern detected: {keyword}")
                return True
        
        return False
    
    def sanitize_phone(self, phone: str) -> str:
        """
        Sanitize phone number.
        
        Args:
            phone: Phone number to sanitize
            
        Returns:
            Sanitized phone (digits only)
        """
        if not isinstance(phone, str):
            return ""
        
        # Keep only digits and +
        phone = re.sub(r'[^0-9+]', '', phone)
        
        return phone
    
    def sanitize_url(self, url: str) -> str:
        """
        Sanitize URL to prevent injection.
        
        Args:
            url: URL to sanitize
            
        Returns:
            Sanitized URL
        """
        if not isinstance(url, str):
            return ""
        
        # Remove dangerous protocols
        dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:']
        url_lower = url.lower()
        
        for protocol in dangerous_protocols:
            if url_lower.startswith(protocol):
                logger.warning(f"Dangerous URL protocol detected: {protocol}")
                return ""
        
        # Basic URL validation
        if not url.startswith(('http://', 'https://', '/')):
            logger.warning(f"Invalid URL format: {url}")
            return ""
        
        return url


# Global sanitizer instance
sanitizer = InputSanitizer()


def sanitize_input(data: Any, max_length: int = 10000) -> Any:
    """
    Convenience function to sanitize any input.
    
    Args:
        data: Data to sanitize
        max_length: Max string length
        
    Returns:
        Sanitized data
    """
    if isinstance(data, str):
        return sanitizer.sanitize_string(data, max_length=max_length)
    elif isinstance(data, dict):
        return sanitizer.sanitize_dict(data, max_string_length=max_length)
    elif isinstance(data, list):
        return sanitizer.sanitize_list(data, max_string_length=max_length)
    else:
        return data
