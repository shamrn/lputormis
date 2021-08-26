from django.db import connections
from django.conf import settings


class ConnectDb:
    """
    Работа с базой данных
    """

    def __init__(self):
        name_db = settings.NAME_DB
        self.cursor = connections[name_db].cursor()

    def _dictfetchall(self, cursor):
        """
        Результат полученных данных, преобразуем в словарь
        """
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    def insert_update_iemk_documents(self, method, rid_instance, tsode_date, error_code, msg, date_upd, date_ins):
        """
        Записываем результат выгрузки, если запись уже имеется в базе, обновляем её
        """
        tsode_date = f"TIMESTAMP '{tsode_date}'" if tsode_date != 'NULL' else tsode_date
        date_upd = f"TIMESTAMP '{date_upd}'" if date_upd != 'NULL' else date_upd
        date_ins = f"TIMESTAMP '{date_ins}'" if date_ins != 'NULL' else date_ins

        static_data_method = {'pharm_mol': {'LOG_OBJECT_TYPE': 5, 'UNLOAD_RID': 84},
                              'prof_registr': {'LOG_OBJECT_TYPE': 2, 'UNLOAD_RID': 86},
                              'lpu_recipes': {'LOG_OBJECT_TYPE': 5, 'UNLOAD_RID': 85},
                              'lgot_registr': {'LOG_OBJECT_TYPE': 1, 'UNLOAD_RID': 87}}

        static_data = static_data_method[method]

        query = f"""
              BEGIN
                  INSERT INTO
                      LPU.IEMK_DOCUMENTS(RID_INSTANCE, TSODE_GUID, TSODE_DATE, TSODE_ID, LOG_OBJECT_TYPE, 
                                        ERROR_CODE, MSG, DATE_UPD, UNLOAD_RID, DATE_INS, SRV_RID)
                  VALUES
                      ({rid_instance}, 
                      NULL, 
                      {tsode_date}, 
                      NULL, 
                      {static_data['LOG_OBJECT_TYPE']}, 
                      {error_code}, 
                      '{msg}', 
                      {date_upd}, 
                      {static_data['UNLOAD_RID']},
                      {date_ins}, 
                      37);
              EXCEPTION
                  WHEN dup_val_on_index THEN
                      UPDATE
                          LPU.IEMK_DOCUMENTS
                      SET
                          TSODE_DATE={tsode_date},
                          ERROR_CODE={error_code},
                          MSG='{msg}',
                          DATE_UPD={date_upd},
                          DATE_INS={date_ins},
                          UNLOAD_RID={static_data['UNLOAD_RID']},
                          SRV_RID=37
                      WHERE
                          RID_INSTANCE={rid_instance};
              END;
              """
        self.cursor.execute(query)
