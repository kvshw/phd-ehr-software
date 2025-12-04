"""
Finnish Personal Identity Number (Henkilötunnus) Validator
Validates and processes Finnish personal identification numbers

Format: YYMMDD-XXXX or YYMMDD+XXXX
- YYMMDD: Date of birth (DDMMYY)
- Separator: - (for dates 1900-1999) or + (for dates 1800-1899) or A (for dates 2000-2099)
- XXXX: Individual number + check digit
"""
import re
from datetime import datetime, date
from typing import Optional, Tuple, Dict


class FinnishIDValidator:
    """Validator for Finnish personal identity numbers (henkilötunnus)"""
    
    # Valid format: YYMMDD-XXXX or YYMMDD+XXXX or YYMMDDAXXXX
    PATTERN = re.compile(r'^(\d{6})([-+A])(\d{3})([0-9A-Y])$')
    
    # Check character mapping (for check digit)
    CHECK_CHARS = '0123456789ABCDEFHJKLMNPRSTUVWXY'
    
    @staticmethod
    def validate(henkilotunnus: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Finnish personal identity number
        
        Args:
            henkilotunnus: Finnish ID number (e.g., "120345-1234")
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not henkilotunnus:
            return False, "Henkilötunnus is required"
        
        # Remove whitespace and convert to uppercase
        henkilotunnus = henkilotunnus.strip().upper()
        
        # Check format
        match = FinnishIDValidator.PATTERN.match(henkilotunnus)
        if not match:
            return False, "Invalid format. Expected: YYMMDD-XXXX or YYMMDD+XXXX or YYMMDDAXXXX"
        
        date_part, separator, individual_part, check_char = match.groups()
        
        # Extract date components
        year = int(date_part[4:6])
        month = int(date_part[2:4])
        day = int(date_part[0:2])
        
        # Determine century based on separator
        if separator == '+':
            century = 1800
        elif separator == 'A':
            century = 2000
        else:  # separator == '-'
            century = 1900
        
        full_year = century + year
        
        # Validate date
        try:
            birth_date = date(full_year, month, day)
        except ValueError:
            return False, f"Invalid date: {day:02d}.{month:02d}.{full_year}"
        
        # Validate check digit
        id_number = date_part + individual_part
        check_digit = FinnishIDValidator._calculate_check_digit(id_number)
        
        if check_char != check_digit:
            return False, f"Invalid check digit. Expected: {check_digit}, Got: {check_char}"
        
        return True, None
    
    @staticmethod
    def _calculate_check_digit(id_number: str) -> str:
        """
        Calculate check digit for Finnish ID
        
        Args:
            id_number: 9-digit number (YYMMDD + individual number)
            
        Returns:
            Check character
        """
        # Convert to integer
        num = int(id_number)
        
        # Calculate remainder when divided by 31
        remainder = num % 31
        
        # Map to check character
        return FinnishIDValidator.CHECK_CHARS[remainder]
    
    @staticmethod
    def extract_info(henkilotunnus: str) -> Optional[Dict]:
        """
        Extract information from Finnish ID
        
        Args:
            henkilotunnus: Valid Finnish ID number
            
        Returns:
            Dictionary with birth_date, gender, age, or None if invalid
        """
        is_valid, error = FinnishIDValidator.validate(henkilotunnus)
        if not is_valid:
            return None
        
        # Parse the ID
        match = FinnishIDValidator.PATTERN.match(henkilotunnus.strip().upper())
        if not match:
            return None
        
        date_part, separator, individual_part, _ = match.groups()
        
        # Extract date
        year = int(date_part[4:6])
        month = int(date_part[2:4])
        day = int(date_part[0:2])
        
        # Determine century
        if separator == '+':
            century = 1800
        elif separator == 'A':
            century = 2000
        else:
            century = 1900
        
        full_year = century + year
        birth_date = date(full_year, month, day)
        
        # Determine gender (odd individual number = male, even = female)
        individual_num = int(individual_part)
        gender = 'M' if individual_num % 2 == 1 else 'F'
        
        # Calculate age
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        return {
            'birth_date': birth_date,
            'gender': gender,
            'age': age,
            'full_year': full_year,
            'individual_number': individual_num
        }
    
    @staticmethod
    def format_henkilotunnus(henkilotunnus: str) -> str:
        """
        Format henkilötunnus to standard format (YYMMDD-XXXX)
        
        Args:
            henkilotunnus: Finnish ID in any valid format
            
        Returns:
            Formatted ID or original if invalid
        """
        is_valid, _ = FinnishIDValidator.validate(henkilotunnus)
        if not is_valid:
            return henkilotunnus
        
        # Remove separator and reformat
        cleaned = henkilotunnus.replace('-', '').replace('+', '').replace('A', '')
        if len(cleaned) == 10:
            return f"{cleaned[:6]}-{cleaned[6:]}"
        
        return henkilotunnus


# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_ids = [
        "120345-1234",  # Valid format
        "120345+1234",  # 1800s
        "120345A1234",  # 2000s
        "120345-1235",  # Invalid check digit
        "321234-1234",  # Invalid date
    ]
    
    print("Finnish ID Validator Test")
    print("=" * 50)
    
    for test_id in test_ids:
        is_valid, error = FinnishIDValidator.validate(test_id)
        if is_valid:
            info = FinnishIDValidator.extract_info(test_id)
            print(f"[VALID] {test_id}: Valid")
            if info:
                print(f"   Birth Date: {info['birth_date']}")
                print(f"   Gender: {info['gender']}")
                print(f"   Age: {info['age']}")
        else:
            print(f"[INVALID] {test_id}: {error}")

