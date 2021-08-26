from django.conf import settings
from zeep import Client
from datetime import datetime
import uuid
from api.connect_db.get_revision import GetRevision


class SoapRequest:
    """
    Отправка данных soap протоколом
    data: данные талона, врача, пациента с базы данных
    """

    def __init__(self, data):
        self.data = data
        self.wsdl = settings.WSDL

    def soap_request_recipes(self):
        """
        Формирование данных рецепта
        """

        data = {'Recipe': self.data}
        method = 'sendLpuRecipes'
        response = self._send(method, RecipeList=data)

        return response

    def soap_request_pharm_mol(self):
        """
        Формирование данных на молочное питание
        """

        self._change_data_pharm_mol()
        data = {'PHARMACYMOLRECIPEtypePHARMACYRECIPE': {'PHARMACYRECIPE_TITLE': self.data}}
        method = 'sendPharmMolRecipes'
        response = self._send(method, PHARMACYRECIPE=data)

        return response

    def soap_request_prof_registr(self):
        """
        Формирование данных врача
        """

        static_data = {
            'FORMAT_GUID': '{B619D0B6-7430-4840-9E35-C15BC1EF0E3D}',
            'PROTOCOL': 'REGISTER_REESTR',
            'VER': '1.0',
            'CREATE_BY': 'МАП льгота',
            'APP_BUILD': 'ПК Здравоохранение Build: 145268',
            'CREATE_TIME': datetime.now(),
            'TITLE': 'Региональный регистр ЛПУ'
        }
        data = {**static_data, 'DATAMAIN': {'DOCUMENTS': {'DOCTOR_DOC': {'DOCTOR': self.data}}}}
        method = 'sendProfessionalRegistr'
        response = self._send(method, data)

        return response

    def soap_request_lgot_registr(self):
        """
        Формирование данных льготника
        """

        revision = GetRevision().get_data()
        guid = uuid.uuid1()
        static_data = {
            'FORMAT_GUID': f'{guid}',
            'PROTOCOL': 'REGISTER_REESTR',
            'VER': '1.0',
            'CREATE_BY': 'МАП льгота',
            'APP_BUILD': f'ПК Здравоохранение Build: {revision}',
            'CREATE_TIME': datetime.now(),
            'TITLE': 'Региональный регистр ЛПУ'
        }

        self._change_data_lgot_registr()
        data = {**static_data, 'DATAMAIN': {'DOCUMENTS': {
            'PERSON_REG_REGISTR': {'PERSON_DOC': {'PERSON_DATA': self.data}}}}}
        method = 'sendRegistr'
        response = self._send(method, MAINFORM=data)

        return response

    def _send(self, method, *args, **kwargs):
        """
        Отправка данных soap запросом
        method: wsdl метод для отправки запроса
        """
        response = {}
        client = Client(wsdl=self.wsdl)

        try:
            response_soap = getattr(client.service, method)(*args, **kwargs)
            error_code = response_soap['ErrorCode']
            response['error_code'] = error_code
            if error_code != 0:
                response['error_text'] = ''.join([text['RecordErrorText'] for text in
                                                  response_soap['ErrorList']['RecordError']])

        except Exception as exc:
            response['error_code'] = -1
            response['error_text'] = exc

        return response


    def _change_data_pharm_mol(self):
        """
        Корректируем полученные данные по молочному питанию
        """
        del self.data['ID_DOCUMENT']
        for key, values in self.data.items():
            if key in ('RDATE', 'DATE_OBR', 'DATE_OTP') and values != None:
                self.data[key] = datetime.strptime(values, '%d.%m.%Y').date()

    def _change_data_lgot_registr(self):
        """
        Корректируем полученные данные по льготнику
        """

        info_data = {}
        lpu_data = {'TYPELPU_DATA': {}, 'KAT_DATA': {}, 'LPU': self.data['MCOD']}

        for key, value in self.data.items():
            if key not in ('NPP', 'KAT', 'DATABEG', 'DATAEND', 'DATADOCEND', 'TYPEPRLPU', 'TIPDOCKAT'):
                info_data[key] = value
            elif key == 'TYPEPRLPU':
                lpu_data['TYPELPU_DATA'].update({key: value, 'DATA': self.data['DATA']})
            else:
                lpu_data['KAT_DATA'].update({key: value})

        info_data['RegistrType'] = info_data.pop('REGISTRTYPE')
        self.data = {'INFO_DATA': info_data, 'LPU_DATA': lpu_data}
