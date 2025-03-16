# middlewares.py

import logging
from datetime import datetime
import json
import io

logger = logging.getLogger("django")

class LogRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Obtener los headers de la petición
        headers = {key: value for key, value in request.META.items() if key.startswith('HTTP_')}
        
        # Leer y restaurar el body de la petición
        body = None
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                request_body = request.body
                request._body = request_body  # Copia para evitar perderlo
                request._stream = io.BytesIO(request_body)  # Restaurar stream
            
                body = json.loads(request_body.decode('utf-8')) if request_body else {}
              
            except json.JSONDecodeError:
                body = request_body.decode('utf-8')  # Si no es JSON, lo guarda como texto

        # Log de la petición
        try:

            logger.info(f"[{datetime.now()}] {request.method} {request.path} - IP: {request.META.get('REMOTE_ADDR')}")
            logger.info(f"Headers: {headers}")
            logger.info(f"Request Body: {body}")

        except Exception as e:
            logger.error(f"Error en la respuesta: {str(e)}")
            raise  # Re-lanzamos el error para que Django lo maneje    


        # Obtener la respuesta llamando al siguiente middleware o vista
        response = self.get_response(request)

        # Leer y loguear la respuesta
        response_body = response.content
        try:
            response_data = json.loads(response_body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            response_data = response_body.decode('utf-8', errors='ignore')

        logger.info(f"[{datetime.now()}] Respuesta {request.method} {request.path} - Status: {response.status_code}")
        logger.info(f"Response Body: {response_data}")

        return response



class AddCOOPHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        origin = request.headers.get("Origin")
        # Agregar el encabezado COOP
        response['Cross-Origin-Opener-Policy'] = 'unsafe-none'  # Puedes cambiar a 'unsafe-none' si es necesario
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-CSRFToken"
        return response
    

import re 
from django.utils.deprecation import MiddlewareMixin

class DynamicCORSHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        origin = request.headers.get("Origin")
        allowed_pattern = re.compile(r"^http://localhost(:\d+)?$")
        
        if origin and allowed_pattern.match(origin):
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-CSRFToken"

        return response
    
