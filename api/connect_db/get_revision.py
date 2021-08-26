from api.connect_db import connect_db


class GetRevision(connect_db.ConnectDb):

    def get_data(self):
        """
        Выгрузка данных о ревизии здрава
        """
        data_revision = self.cursor.execute(self._query_revision)
        data_revision = self._dictfetchall(data_revision)
        return data_revision[0]['REVISION']

    def _query_revision(self):
        """
        SQL запрос на получение данных о ревизии здрава
        """
        return """
            SELECT
                revision
            FROM 
                lpu.update_pk 
            WHERE 
              upper(file_name) = 'PROJECT_ZDRAVOOHRANENIE.EXE'
        """
