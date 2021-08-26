from rest_framework.views import APIView
from rest_framework.response import Response
from api.service import service_lpu_recipes, service_pharm_mol


class SendLpuRecipesView(APIView):

    def get(self, request):
        service_lpu_recipes()
        return Response(200)


class SendPharmMolView(APIView):

    def get(self, request):
        service_pharm_mol()
        return Response(200)
