from celery import shared_task
from api.service import service_lpu_recipes, service_pharm_mol


@shared_task
def tasks_send_recipes(db_name, unload_rid, **kwargs):
    service_lpu_recipes()
    service_pharm_mol()
