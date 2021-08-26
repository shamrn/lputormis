from api.connect_db import connect_db


class LgotRegistr(connect_db.ConnectDb):
    """
    Выгрузка данных льготника
    """

    def get_data(self, lgot_pid):
        """
        Получение данных с базы данных
        """
        data_lgot = self.cursor.execute(self._query_lgot_registr(lgot_pid))
        data_lgot = self._dictfetchall(data_lgot)

        return dict(*data_lgot)

    def _query_lgot_registr(self, lgot_pid):
        """
        SQL запрос на получение данных льготника
        """
        return f"""
                SELECT
                    DISTINCT p.pid,
                    lt.LPU_ID AS MCOD,
                    p.SNILS,
                    p.SNAME AS FAM,
                    p.FNAME AS IMA,
                    p.MNAME AS OTC,
                    CASE 
                        WHEN p.POL = 'М' THEN 
                            '1'
                        ELSE '2'
                    END AS SEX,
                    p.DATE_B AS DR,
                    pd.SER AS SERDOC,
                    pd.NUM AS NOMDOC,
                    pd.VDK AS TIPDOC,
                    pd.DATE_V AS DATE_DOC,
                    pd.KEM AS FROM_DOC,
                    pd.ADDRESS_REGISTRATION AS ADRPREG,
                    pd.ADDRESS_RESIDENTIAL AS DADRPREG,
                    pol.ENP,
                    l.PROG_LLO AS RegistrType,
                    CASE
                        WHEN lt.LLO_ATT = '1' THEN
                            CASE WHEN pau.DATE_UNP IS NULL THEN pau.DATE_ATT ELSE pau.DATE_UNP END 
                        ELSE gs.DATE_V
                    END AS DATA,
                    1 AS NPP,
                    l.KOD_PF AS KAT,
                    g.DATE_S AS DATABEG,
                    g.DATE_E AS DATAEND,
                    g.DATE_E AS DATADOCEND,
                    4 AS TIPDOCKAT,
                    CASE
                        WHEN lt.LLO_ATT = '1' THEN 
                            CASE WHEN pau.DATE_UNP IS NULL THEN '1' ELSE '2' END 
                        ELSE '3'
                    END AS TYPEPRLPU 
                FROM
                    LPU.PASPORT p
                INNER JOIN LPU.P_DOCUM pd ON p.PID = pd.PID 
                LEFT JOIN RECEPT.GSPDOC g ON g.PID = p.PID 
                INNER JOIN RECEPT.KATLGOT l ON g.LGID = l.LGID
                INNER JOIN LPU.TUNE lt ON pd.LID = lt.LID 
                INNER JOIN LPU.P_ATT_UCH pau ON p.PID = pau.PID
                LEFT JOIN RECEPT.GSPCARD gs ON gs.PID = p.PID
                INNER JOIN LPU.POLICY pol ON p.pid = pol.PID
                WHERE l.PROG_LLO = '5' AND p.PID = {lgot_pid}
        """
