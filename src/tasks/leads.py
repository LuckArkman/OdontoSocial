import os

import pandas as pd

from src.core.celery_app import celery_app
from src.core.logging_config import logger
from src.db.session import SessionLocal
from src.models.import_job import BulkImportJob, ImportStatus
from src.models.lead import Lead
from src.services.lead_validator import LeadValidator


@celery_app.task(name="src.tasks.leads.process_bulk_import")
def process_bulk_import(job_id: int, file_path: str, tenant_id: int):
    """
    Tarefa de background para processar a importação de CSV/Excel.
    """
    db = SessionLocal()
    job = db.query(BulkImportJob).filter(BulkImportJob.id == job_id).first()

    if not job:
        logger.error(f"Job {job_id} não encontrado.")
        return False

    try:
        # 1. Update status to processing
        job.status = ImportStatus.PROCESSING
        db.add(job)
        db.commit()

        # 2. Read file
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # 3. Process rows
        total_rows = len(df)
        job.total_leads = total_rows
        db.add(job)
        db.commit()

        processed_count = 0
        for index, row in df.iterrows():
            # Converter row do pandas para dict
            row_dict = row.to_dict()

            # Validação
            is_valid, lead_in, error = LeadValidator.validate_one(row_dict)

            if is_valid and lead_in:
                # Salvar no banco
                db_lead = Lead(**lead_in.model_dump(), tenant_id=tenant_id)
                db.add(db_lead)
                processed_count += 1

                # Commit parcial a cada 50 leads ou final
                if processed_count % 50 == 0:
                    db.commit()
                    # Atualizar o job progress no DB
                    job.processed_leads = processed_count
                    db.add(job)
                    db.commit()

        # Final commit and status
        db.commit()
        job.processed_leads = processed_count
        job.status = ImportStatus.COMPLETED
        db.add(job)
        db.commit()

        logger.info(
            f"Importação {job_id} finalizada com sucesso. {processed_count} leads processados."
        )

    except Exception as e:
        logger.error(f"Erro ao processar importação {job_id}: {str(e)}")
        job.status = ImportStatus.FAILED
        job.error_message = str(e)[:500]
        db.add(job)
        db.commit()
    finally:
        db.close()
        # Limpar o arquivo temporário
        if os.path.exists(file_path):
            os.remove(file_path)

    return True
