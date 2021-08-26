import datetime
from api.connect_db import pharm_mol, prof_registr, lpu_recipes, lgot_registr
from api.soap import SoapRequest


def service_lpu_recipes():
    """
    Выгрузка и отправка рецепта
    """
    connect_db = lpu_recipes.LpuRecipes()
    data_db = connect_db.get_data()

    for recipe in data_db:
        rid = recipe.pop('RID')
        method = 'lpu_recipes'

        # Перед отправкой рецепта отправляем пациента и врача
        service_lgot_registr(recipe.pop('PID'))
        service_prof_registr(recipe.pop('DOCTOR'))

        soap = SoapRequest(recipe)
        response = soap.soap_request_recipes()
        logging(response, method, rid, connect_db)


def service_prof_registr(doctor_pid):
    """
    Выгрузка и отправка данных врача, выписавшего рецепт
    """
    connect_db = prof_registr.ProfRegistr()
    data_doc = connect_db.get_data(doctor_pid=doctor_pid)

    if data_doc:
        rid = data_doc.pop('RID')
        method = 'prof_registr'

        soap = SoapRequest(data_doc)
        response = soap.soap_request_prof_registr()
        logging(response, method, rid, connect_db)


def service_lgot_registr(lgot_pid):
    """
    Выгрузка и отправка данных льготника
    """
    connect_db = lgot_registr.LgotRegistr()
    data_lgot = connect_db.get_data(lgot_pid=lgot_pid)

    if data_lgot:
        rid = data_lgot.pop('PID')
        method = 'lgot_registr'

        soap = SoapRequest(data_lgot)
        response = soap.soap_request_lgot_registr()
        logging(response, method, rid, connect_db)


def service_pharm_mol():
    """
    Выгрузка и отправка обслуженных талонов на молочное питание
    """
    connect_db = pharm_mol.PharmMol()
    data_db = connect_db.get_data()

    for ticket in data_db:

        # Валидация талона
        validation_error = False
        if ticket['DELAYED_SERVICE'] != 1:

            if ticket['ID_DOCUMENT'] == None:
                msg = 'Для получения информации об отпущенном препарате, отсутствует "id_document"'
                validation_error = True
            # При DELAYED_SERVICE != 1, добавляем к основному запросу информацию об отпущенном препарате
            else:
                data_pharm_rec = connect_db.query_pharmacyrecipe_data(ticket['id_document'])
                ticket['PHARMACYRECIPE_DATA'] = data_pharm_rec

        rid = ticket.pop('RID')
        method = 'pharm_mol'

        if validation_error:
            response = {'error_code':-1, 'error_text':msg}
            logging(response, method, rid, connect_db)
        else:
            soap = SoapRequest(ticket)
            response = soap.soap_request_pharm_mol()

            logging(response, method, rid, connect_db)


def logging(response, method, rid, connect_db):
    """
    Запись результата выгрузки
    """
    date_now = datetime.datetime.now()
    msg = {
        'lpu_recipes': 'Выписанный рецепт на молочное питание отправлен в ИСМПЛ',
        'lgot_registr': 'Данные льготника отправлены в ИСМЛП',
        'prof_registr': 'Данные врача отправлены в ИСМПЛ',
        'pharm_mol': 'Данные обслуженного талона молочное питание отправлен в ИСМПЛ'}

    if response['error_code'] == 0:
        tsode_date = date_now
        error_code = 0
        msg = msg[method]
    else:
        tsode_date = 'NULL'
        error_code = 1
        msg = response['error_text']

    connect_db.insert_update_iemk_documents(method=method,
                                            rid_instance=rid,
                                            tsode_date=tsode_date,
                                            error_code=error_code,
                                            msg=msg,
                                            date_upd=date_now,
                                            date_ins=date_now)
