import base64

from requests import RequestException

from enum import Enum
from requests import Response
from typing import Union
from flask import current_app
from core.http import HTTPClient

class DrawioOutputFormats(Enum):
    PNG = "png"
    PDF = "pdf"
    HTML = "html"

class DrawIO:
    
    def __init__(self):
        self.url = current_app.config.extention.drawio['url']
        self.http_client = HTTPClient(self.url)

    def __remote_request(self, content: str, format: DrawioOutputFormats) -> Union[Response, RequestException]:

        endpoint = "/export"
        headers = { "Content-Type": "application/x-www-form-urlencoded"}
        data = {
                "format": format.value,
                "xml": content,
                "base64": "false",
                "embedXml": "false"
            }
        
        # Получаем ответ сервера draw.io
        response =  self.http_client.post(endpoint=endpoint, 
                                          headers=headers,
                                          data=data)
    
        return response
    
    def render_png(self, content:str) -> bytes:

        response = self.__remote_request(
            content=content,
            format=DrawioOutputFormats.PNG
        )

        # Если вернулся RequestException то возвращаем его
        if isinstance(response, RequestException):
            return response

        # Если все ок, то возвращаем контент (а другое сюда не должно дойти)
        return base64.b64encode(response.content).decode("utf-8")