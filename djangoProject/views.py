from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests

BASE_URL = 'http://192.168.20.20:3000/'


@api_view(['GET'])
def get_Personne(request):
    if request.method == 'GET':
        get_request = requests.get(f"{BASE_URL}personne/")
        result = get_request.json()
        return Response(result)

