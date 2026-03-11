import re
from typing import Any, Dict, Optional, Tuple

from pydantic import ValidationError

from src.schemas.lead import LeadCreate


class LeadValidator:
    """
    Consolida as validações de dados brutos para novos leads.
    """

    @staticmethod
    def clean_phone(phone: str) -> str:
        """
        Normaliza telefones: remove caracteres não numéricos.
        Se não começar com '+', assume-se o código do país do Brasil (+55).
        """
        digits = re.sub(r"\D", "", phone)

        if not phone.startswith("+"):
            return f"+55{digits}"
        return f"+{digits}"

    @staticmethod
    def validate_one(
        data: Dict[str, Any],
    ) -> Tuple[bool, Optional[LeadCreate], Optional[str]]:
        """
        Valida um dicionário de dados brutos e retorna uma instância de LeadCreate se válido.
        """
        try:
            # Normalização preliminar do telefone
            if "phone" in data:
                data["phone"] = LeadValidator.clean_phone(str(data["phone"]))

            # Validação Pydantic
            lead_in = LeadCreate(**data)
            return True, lead_in, None
        except ValidationError as e:
            return False, None, str(e)
        except Exception as e:
            return False, None, str(e)
