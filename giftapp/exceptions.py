from rest_framework.exceptions import APIException
from django.http import JsonResponse
from rest_framework.response import Response

class Noe(APIException):
    def __init__(self, detail=None, code=None):
        status_code = 401
        default_detail = 'You are not currently authorised to perform this action.'
        default_code = 'not_authenticated'
    
    def __str__(self):
        return Response(self.default_detail)
