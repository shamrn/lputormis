from api.connect_db import connect_db


class ProfRegistr(connect_db.ConnectDb):
    """
    Выгрузка данных врача, выписавшего рецепт
    """

    def get_data(self, doctor_pid):
        """
        Получение данных с базы данных
        """
        data_registr = self.cursor.execute(self._query_prof_registr(doctor_pid))
        data_registr = self._dictfetchall(data_registr)

        return dict(*data_registr)

    def _query_prof_registr(self, doctor_pid):
        """
        SQL запрос на получение данных врача
        """
        return f"""
              SELECT
                d.DOCTOR AS rid,
                u.SNAME AS FAM_V,
                u.FNAME AS IM_V,
                u.MNAME AS OT_V,
                u.RDATE_S AS DATE_B,
                u.RDATE_E AS DATE_E,
                u.SNILS AS SNILS,
                substr(u.RECEPT_DOCTOR , 15, 5) AS PCOD,
                u.DATE_BEG AS D_PRIK,
                u.CAT AS KV_KAT,
                fp.id as PRVD,
                Substr(u.recept_doctor, 1, 13) C_OGRN,
                d.date_srt AS D_SER,
                0 AS DESTROYED,
                l.lpu_id AS MCOD,
                l.OGRN AS C_OGRN,
                l.OKATO TF_OKATO,
                (
                select listagg(t.PP_SPEC_CODE)
                    within group (order by t.PP_SPEC_CODE) PRVS from 
                           (select distinct sp.PP_SPEC_CODE from adm_glb.medspec sp, lpu.doctor d where 
                            sp.rid = d.speccode and d.id_user in (select id_user from lpu.doctor where doctor = {doctor_pid} )) t
                            ) AS PRVS
            FROM
                LPU.DOCTOR d
            INNER JOIN lpu.users u ON u.id_user = d.id_user
            INNER JOIN adm_glb.medspec ms ON ms.rid = d.speccode
            LEFT JOIN nsi.fed_post fp ON fp.id = coalesce(d.frmr_post_id, ms.fed_00365_tsod)
            INNER JOIN LPU.tune l ON l.LID = u.LID
            WHERE d.ID_USER = u.ID_USER and u.TSOD_LLO is not NULL and d.doctor = {doctor_pid}
        """
