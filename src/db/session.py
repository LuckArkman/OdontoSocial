from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.core.middlewares.tenant_context import get_tenant_id

engine = create_engine(
    settings.database_url,
    # Configurações para PostgreSQL
    pool_pre_ping=True,
)

@event.listens_for(engine, "checkout")
def set_tenant_on_checkout(dbapi_connection, connection_record, connection_proxy):
    """
    Injeta o tenant_id atual na sessão do PostgreSQL sempre que uma conexão 
    for retirada do pool para uma request. Esse valor pode ser usado por 
    Policies de RLS no banco de dados.
    """
    tenant_id = get_tenant_id()
    cursor = dbapi_connection.cursor()
    if tenant_id:
        # Define a variável local na sessão do Postgres
        cursor.execute(f"SET app.current_tenant = '{tenant_id}';")
    else:
        # Se não houver tenant (ex: superadmin global), reseta a variável
        cursor.execute("RESET app.current_tenant;")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
