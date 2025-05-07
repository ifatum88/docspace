import base64

from core.http import HTTPClient
from config import Config
from requests import RequestException

from enum import Enum
from requests import Response
from typing import Union


class DrawioOutputFormats(Enum):
    PNG = "png"
    PDF = "pdf"
    HTML = "html"


class DrawIO:
    
    def __init__(self):
        self.url = Config.DRAWIO_URL
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