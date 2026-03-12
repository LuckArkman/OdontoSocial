import re
from typing import Any, Dict, Optional, Tuple

from pydantic import ValidationError

from src.schemas.lead import LeadCreate


from src.services.lead_cleaner import LeadCleaner

class LeadValidator:
    """
    Consolida as validações de dados brutos para novos leads.
    """

    @staticmethod
    def clean_phone(phone: str) -> Optional[str]:
        return LeadCleaner.normalize_phone(phone)

    @staticmethod
    def validate_one(
        data: Dict[str, Any],
    ) -> Tuple[bool, Optional[LeadCreate], Optional[str]]:
        """
        Valida um dicionário de dados brutos e retorna uma instância de LeadCreate se válido.
        """
        try:
            # 1. Normalização de Telefone
            if "phone" in data:
                phone_normalized = LeadValidator.clean_phone(str(data["phone"]))
                if not phone_normalized:
                    return False, None, "Telefone inválido para a região informada."
                data["phone"] = phone_normalized
            
            # 2. Normalização de E-mail
            if "email" in data:
                data["email"] = LeadCleaner.clean_email(data["email"])
                
            # 3. Limpeza de Nome
            if "name" in data:
                data["name"] = LeadCleaner.clean_name(data["name"])

            # Validação Pydantic
            lead_in = LeadCreate(**data)
            return True, lead_in, None
        except ValidationError as e:
            return False, None, str(e)
        except Exception as e:
            return False, None, str(e)
