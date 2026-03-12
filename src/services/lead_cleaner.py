import phonenumbers
from phonenumbers import PhoneNumberFormat, NumberParseException
import re
from typing import Optional

class LeadCleaner:
    """
    Serviço especializado em limpeza e padronização de dados de leads.
    """
    
    @staticmethod
    def normalize_phone(phone: str, default_region: str = "BR") -> Optional[str]:
        """
        Usa a biblioteca phonenumbers para validar e formatar o número no padrão E.164.
        """
        try:
            # Limpeza básica de strings como "N/A", "celular:", etc.
            phone_cleaned = re.sub(r"[^\d+]", "", phone)
            
            # Tenta fazer o parse
            parsed_number = phonenumbers.parse(phone_cleaned, default_region)
            
            if phonenumbers.is_valid_number(parsed_number):
                return phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164)
            return None
        except NumberParseException:
            return None

    @staticmethod
    def clean_name(name: str) -> str:
        """
        Remove espaços extras e capitaliza corretamente.
        """
        if not name:
            return ""
        return " ".join(name.split()).title()

    @staticmethod
    def clean_email(email: Optional[str]) -> Optional[str]:
        """
        Normaliza e valida formato básico de e-mail.
        """
        if not email:
            return None
        email = email.strip().lower()
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return email
        return None
