"""
Password Policy Enforcement
Ensures strong password requirements for security
"""

import re
from typing import Tuple, List
import logging

logger = logging.getLogger("mediconnect")


class PasswordPolicy:
    """
    Enforces password security requirements.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    - No common passwords
    - No user information in password
    """
    
    # Common weak passwords to reject
    COMMON_PASSWORDS = {
        'password', 'password123', '12345678', 'qwerty', 'abc123',
        'monkey', '1234567890', 'letmein', 'trustno1', 'dragon',
        'baseball', 'iloveyou', 'master', 'sunshine', 'ashley',
        'bailey', 'passw0rd', 'shadow', '123123', '654321',
        'superman', 'qazwsx', 'michael', 'football', 'welcome',
        'jesus', 'ninja', 'mustang', 'password1', 'admin',
        'administrator', 'root', 'toor', 'pass', 'test'
    }
    
    def __init__(
        self,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digit: bool = True,
        require_special: bool = True,
        max_length: int = 128
    ):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special
        self.max_length = max_length
    
    def validate(
        self,
        password: str,
        user_email: str = None,
        user_name: str = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate password against policy.
        
        Args:
            password: Password to validate
            user_email: User's email (to prevent using email in password)
            user_name: User's name (to prevent using name in password)
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check if password is provided
        if not password:
            errors.append("Password is required")
            return False, errors
        
        # Check length
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")
        
        if len(password) > self.max_length:
            errors.append(f"Password must not exceed {self.max_length} characters")
        
        # Check for uppercase
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        # Check for lowercase
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        # Check for digit
        if self.require_digit and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        # Check for special character
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)")
        
        # Check against common passwords
        if password.lower() in self.COMMON_PASSWORDS:
            errors.append("Password is too common. Please choose a stronger password")
        
        # Check if password contains user information
        if user_email:
            email_parts = user_email.lower().split('@')[0].split('.')
            for part in email_parts:
                if len(part) >= 3 and part in password.lower():
                    errors.append("Password should not contain parts of your email")
                    break
        
        if user_name:
            name_parts = user_name.lower().split()
            for part in name_parts:
                if len(part) >= 3 and part in password.lower():
                    errors.append("Password should not contain parts of your name")
                    break
        
        # Check for sequential characters
        if self._has_sequential_chars(password):
            errors.append("Password should not contain sequential characters (e.g., 123, abc)")
        
        # Check for repeated characters
        if self._has_repeated_chars(password):
            errors.append("Password should not contain too many repeated characters")
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            logger.warning(f"Password validation failed: {', '.join(errors)}")
        
        return is_valid, errors
    
    def _has_sequential_chars(self, password: str, length: int = 3) -> bool:
        """Check for sequential characters like 123 or abc."""
        password_lower = password.lower()
        
        # Check for sequential numbers
        for i in range(len(password_lower) - length + 1):
            substr = password_lower[i:i + length]
            if substr.isdigit():
                digits = [int(d) for d in substr]
                if all(digits[j] + 1 == digits[j + 1] for j in range(len(digits) - 1)):
                    return True
                if all(digits[j] - 1 == digits[j + 1] for j in range(len(digits) - 1)):
                    return True
        
        # Check for sequential letters
        for i in range(len(password_lower) - length + 1):
            substr = password_lower[i:i + length]
            if substr.isalpha():
                chars = [ord(c) for c in substr]
                if all(chars[j] + 1 == chars[j + 1] for j in range(len(chars) - 1)):
                    return True
                if all(chars[j] - 1 == chars[j + 1] for j in range(len(chars) - 1)):
                    return True
        
        return False
    
    def _has_repeated_chars(self, password: str, max_repeat: int = 3) -> bool:
        """Check for repeated characters like 'aaa' or '111'."""
        for i in range(len(password) - max_repeat + 1):
            if len(set(password[i:i + max_repeat])) == 1:
                return True
        return False
    
    def get_strength_score(self, password: str) -> int:
        """
        Calculate password strength score (0-100).
        
        Args:
            password: Password to evaluate
            
        Returns:
            Strength score from 0 (weak) to 100 (strong)
        """
        score = 0
        
        # Length score (up to 30 points)
        if len(password) >= 8:
            score += 10
        if len(password) >= 12:
            score += 10
        if len(password) >= 16:
            score += 10
        
        # Character variety (up to 40 points)
        if re.search(r'[a-z]', password):
            score += 10
        if re.search(r'[A-Z]', password):
            score += 10
        if re.search(r'\d', password):
            score += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 10
        
        # Complexity bonus (up to 30 points)
        unique_chars = len(set(password))
        if unique_chars >= 8:
            score += 10
        if unique_chars >= 12:
            score += 10
        if unique_chars >= 16:
            score += 10
        
        # Penalties
        if password.lower() in self.COMMON_PASSWORDS:
            score -= 30
        if self._has_sequential_chars(password):
            score -= 10
        if self._has_repeated_chars(password):
            score -= 10
        
        return max(0, min(100, score))
    
    def get_strength_label(self, score: int) -> str:
        """
        Get human-readable strength label.
        
        Args:
            score: Strength score (0-100)
            
        Returns:
            Strength label
        """
        if score >= 80:
            return "Strong"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        elif score >= 20:
            return "Weak"
        else:
            return "Very Weak"
    
    def generate_requirements_message(self) -> str:
        """Generate a message describing password requirements."""
        requirements = [
            f"At least {self.min_length} characters long"
        ]
        
        if self.require_uppercase:
            requirements.append("At least one uppercase letter")
        if self.require_lowercase:
            requirements.append("At least one lowercase letter")
        if self.require_digit:
            requirements.append("At least one digit")
        if self.require_special:
            requirements.append("At least one special character (!@#$%^&*(),.?\":{}|<>)")
        
        requirements.append("Not a common password")
        requirements.append("Should not contain your email or name")
        
        return "Password must meet the following requirements:\n- " + "\n- ".join(requirements)


# Global password policy instance
password_policy = PasswordPolicy()
