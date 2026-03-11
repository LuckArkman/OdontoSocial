import logging
import os

from alembic.config import Config

from alembic import command

logger = logging.getLogger(__name__)


class MigrationManager:
    """
    Gerenciador programático de migrações do Alembic.
    Permite rodar upgrades de forma automatizada (ex: no startup da API).
    """

    def __init__(self, ini_path: str = "alembic.ini"):
        # Garante o path absoluto para o arquivo .ini
        if not os.path.isabs(ini_path):
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.ini_path = os.path.join(current_dir, ini_path)
        else:
            self.ini_path = ini_path

        self.alembic_cfg = Config(self.ini_path)

    def run_upgrade(self, revision: str = "head"):
        """Executa a atualização para a revisão especificada."""
        try:
            logger.info(f"Iniciando migração do banco para: {revision}")
            command.upgrade(self.alembic_cfg, revision)
            logger.info("Migração concluída com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao executar migração: {e}")
            raise e

    def get_current_revision(self):
        """Retorna a revisão atual do banco (se possível)."""
        # Implementação opcional para healthchecks mais profundos
        pass
