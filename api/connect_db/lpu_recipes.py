from api.connect_db import connect_db


class LpuRecipes(connect_db.ConnectDb):
    """
    Выгрузка рецепта на молочное питание, выписанных в медицинской организации.
    """

    def get_data(self):
        """
        Получение данных с базы данных
        """
        # Получаем список словарей, рецептов
        data_recipes = self.cursor.execute(self._query_lpu_recipes)
        data_recipes = self._dictfetchall(data_recipes)

        return data_recipes

    def _query_lpu_recipes(self):
        """
        Sql запрос на получение рецепта
        """
        return """
            
           WITH INST AS (
            SELECT
                *    
            FROM
                (
                SELECT
                    i.rid,					
                    i.USER_CREATOR,         -- Код врача, создавшего документ
                    lower(f.FIELD_SYNONYM) AS field_synonym,
                    d.instance_value,       -- Значение поля шаблона
                    i.date_upd,              -- Дата обновления рецепта 
                    pmh.pid AS user_pid
                FROM
                    lpu.INSTANCE i,			-- Список экземпляров шаблонов
                    lpu.template t,         -- Шаблоны текстовых форм
                    lpu.instance_fields f,
                    lpu.instance_data d,     -- Хранит данные экземпляра
                    lpu.p_medical_history pmh -- PID пациента
                WHERE t.rid = i.RID_TEMPLATE
                AND pmh.instance_rid = i.rid 
                AND f.INSTANCE_RID = i.RID
                AND d.TEMPLATE_FIELDS_RID = f.FLD_RID
                AND d.rid_instance = i.rid
                AND i.RID_TEMPLATE = 'C101867D9F4C4768994B7FC127A2622D'
                AND lower(f.FIELD_SYNONYM) IN ('snils', 'receptdate', 'ser', 'num', 'lgid', 'doc_guid', 'product_id','kolvo'))
                pivot (max(instance_value) FOR FIELD_SYNONYM IN ('snils' as snils,
                                                                  'receptdate' as receptdate,
                                                                  'ser' as ser,
                                                                  'num' as num,
                                                                  'lgid' as lgid,
                                                                  'doc_guid' as doc_guid,
                                                                  'product_id' AS product_id,
                                                                  'kolvo' AS kolvo))
               ORDER BY rid)
        SELECT
            DISTINCT p.pid,
            i.rid,
            i.USER_CREATOR AS doctor,
            tu.LPU_ID AS IDMU,
            substr(us.RECEPT_DOCTOR , 15, 5) AS PCOD,
            i.ser AS RSERIES,
            i.NUM AS RNUMBER,
            i.RECEPTDATE AS RDATE,
            i.SNILS AS SNILS,
            p.DATE_B AS DATEBIRTH,
            CASE
                WHEN p.POL = 'М' THEN
                    '1'
                ELSE '2'
            END AS GENDER,
            pd.SER AS PSERIES,
            pd.NUM AS PNUMBER,
            (
                SELECT k.ocatd
                FROM adm_glb.kladr_kladr k
                WHERE k.code(+) = substr(p.kladr_adrespas, 1, 11) || '00' AND k.socr(+) NOT IN ('Р-Н','АО','ОКРУГ', 'ОБЛ','КРАЙ','АОБЛ','РЕСП','ТЕР','У')
                AND p.pid = i.user_pid
            ) AS OKATO,
            ka.PROG_LLO AS CATEGORYTYPE,
            ka.KOD_PF AS CATEGORYCODE,
            2 AS FINSOURCECODE,
            CASE
                WHEN ka.PERCENT = 1 THEN
                    '50'
                ELSE '100'
            END AS PERCENT,
            st.C_LSFO AS TRNCODE,
            st.C_MNN AS MNNCODE,
            0 AS DRUGFORMCODE,
            st.V_LF AS DOSAGE,
            (i.kolvo - st.V_LF) AS QUANTITY,
            30 AS VALIDITY,
            0 as VK
        FROM 
            inst i
        JOIN lpu.doctor do on do.doctor = i.user_creator
        JOIN lpu.users us on us.id_user = do.id_user
        JOIN lpu.tune tu on tu.lid = do.lid
        JOIN RECEPT.SP_TOV_MILK stm ON stm.C_LSFO = i.product_id
        JOIN RECEPT.SP_TOV st ON st.C_LSFO = stm.C_LSFO
        JOIN recept.katlgot ka on ka.lgid = i.lgid
        JOIN LPU.PASPORT p ON p.PID = i.user_pid
        JOIN LPU.P_DOCUM pd ON p.PID = pd.PID  
        LEFT JOIN lpu.iemk_documents ik on ik.rid_instance = i.rid
                            and ik.log_object_type = 5
                            and ik.unload_rid = 85
                            and ik.srv_rid = 37
        WHERE i.snils is not null
                and (ik.error_code is null or ik.error_code = 2
                or ik.date_upd < i.date_upd)
        """
