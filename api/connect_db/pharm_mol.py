from api.connect_db import connect_db


class PharmMol(connect_db.ConnectDb):
    """
    Выгрузка обслуженных талонов на молочное питание
    """

    def get_data(self):
        """
        Получение данных с базы данных
        """
        # Получаем список словарей, отпущенных рецептов по молочной кухне
        data_pharm_mol = self.cursor.execute(self._query_send_pharm_mol())
        data_pharm_mol = self._dictfetchall(data_pharm_mol)

        return data_pharm_mol

    def _query_send_pharm_mol(self):
        """
        Sql запрос на получение данных талонов на молочное питание
        """
        return """

            with inst as (select * 
              from (select i.rid, i.user_creator, i.date_upd, lower(f.field_synonym) as field_synonym, d.instance_value        
                    from lpu.instance i, lpu.template t, lpu.instance_fields f, lpu.instance_data d
                    where t.rid = i.rid_template and f.instance_rid = i.rid and d.template_fields_rid = f.fld_rid and d.rid_instance = i.rid
                      and i.rid_template = 'C101867D9F4C4768994B7FC127A2622D'
                      and lower(f.field_synonym) in ('snils', 'receptdate', 'ser', 'num', 'lgid', 'doc_guid'))
              pivot (max(instance_value) for field_synonym in ('snils' as snils,
                                                               'receptdate' as receptdate,
                                                               'ser' as ser,
                                                               'num' as num,
                                                               'lgid' as lgid,
                                                               'doc_guid' as doc_guid))
              order by rid)  
            select
              ie.id_document,
              i.rid,
              tu.lpu_id as A_COD,
              i.snils as SNILS,
              ka.kod_pf as CATEGORYCODE,
              i.receptdate as RDATE,
              2 as C_FINL,
              i.ser as RSERIES,
              i.num as RNUMBER,
              1 as PERCENT,
              tu.fed_oid as OID,
              substr(us.recept_doctor, -5, 5) as PCOD,
              tu.ogrn as V_C_OGRN,
              i.receptdate as DATE_OBR,
              ie.date_in as DATE_OTP,
              decode(ie.approve, 1, 0, 1) as DELAYED_SERVICE,
              doc_guid as RECIPEGUID,
              5 as CATEGORYTYPE
            from
              inst i
              left join lpu.doctor do on do.doctor = i.user_creator
              left join lpu.users us on us.id_user = do.id_user
              left join lpu.tune tu on tu.lid = do.lid
              left join lpu_apteka.apt_recipe ar on ar.recipe_ser = i.ser and ar.recipe_num = i.num
              left join lpu_apteka.income_expenditure ie on ie.id_document = ar.rinex
              left join recept.katlgot ka on ka.lgid = i.lgid
              left join lpu.iemk_documents ik on ik.rid_instance = i.rid
                                                 and ik.log_object_type = 5
                                                 and ik.unload_rid = 84
                                                 and ik.srv_rid = 37
            where
              i.snils is not null
              and (ik.error_code is null or ik.error_code = 2
                   or ik.date_upd < i.date_upd) and rownum <= 1

        """

    def query_pharmacyrecipe_data(self, id_document):
        """
        SQL запрос на получение информации об отпущенном препарате,
        добавляется к талону при DELAYED_SERVICE != 1
        """
        query = f"""
            select
              ls.rls_id as LID,
              ex.kolotp as KO_ALL,
              ex.price as PRICE,
              ie.numdog as ID_GK,
              ex.seria as SERIA
            from
              lpu_apteka.income_expenditure ie
              left join lpu_apteka.expenditure ex on ex.rinex = ie.id_document
              left join lpu_apteka.lekar_spr ls on ls.rid = ex.rlekar
            where
              ie.id_document = {id_document}
        """
        data_pharm_rec = self.cursor.execute(query)
        data_pharm_rec = self._dictfetchall(data_pharm_rec)

        return dict(*data_pharm_rec)
