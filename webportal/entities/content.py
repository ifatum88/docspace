import os
import subprocess

from enum import Enum
from flask import render_template
from typing import Any
from functools import wraps
from requests import RequestException

from config import Config
from services import DrawIO 

class ContentType(Enum):
    MARKDOWN = "markdown"
    PLAINTEXT = "plain-text"
    HTML = "html"
    RAW = "raw"
    PLANTUML = "plantuml"
    DRAWIO = "draw.io"

class ContentGenerationMode(Enum):
    SERVER_SIDE = "server-side"
    REMOTE_SERVER = "remote-server"

def generate_fallback(content_type: ContentType, error_message: str = "Ошибка при генерации контента"):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            if isinstance(result, RequestException):
                return self._content_error(f"[{content_type.value}] {error_message}", exeption=result)
            return result
        return wrapper
    return decorator

class Content:

    __content = "No content"

    def __init__(self, content:str, content_type:object, *args, **kwargs):
        self.raw_content = content
        self.content_type = self.__convert_to_contenttype(content_type)
        self.args = args
        self.kwargs = kwargs

    @property
    def content(self):
        return self.generate() or self.__content
    
    def generate(self):

        generators = {
            ContentType.MARKDOWN: self.__generate_markdown,
            ContentType.HTML: self.__generate_html,
            ContentType.PLAINTEXT: self.__generate_plaintext,
            ContentType.RAW: self.__generate_raw,
            ContentType.PLANTUML: self.__generate_plantum,
            ContentType.DRAWIO: self.__generate_drawio
        }

        if not self.raw_content or not self.content_type:
            return None
        
        content = generators.get(self.content_type)()

        return content

    def _content_error(self, error_text:str, exeption:RequestException):
        return render_template(
            'content/error.html',
            error_text=error_text,
            exeption=exeption,
            **self.kwargs
        )

    def __content_success(self, content:Any, template:str):
        return render_template(
            template,
            content=content,
            **self.kwargs
        )

    def __convert_to_contenttype(self, _type):
        if isinstance(_type, ContentType):
            return _type
        try:
            return ContentType(_type)
        except:
            return ContentType.RAW

    def __generate_markdown(self):
        
        import markdown as md

        return render_template (
            'content/markdown.html',
            content=md.markdown(self.raw_content, extensions=['fenced_code', 'tables']),
            **self.kwargs
        )
    
    def __generate_html(self):
        return render_template (
            'content/html.html',
            content=self.raw_content,
            **self.kwargs
        )
    
    def __generate_plaintext(self):
        return render_template (
            'content/plaintext.html',
            content=self.raw_content,
            **self.kwargs
        )
    
    def __generate_raw(self):
        return render_template (
            'content/raw.html',
            content=self.raw_content,
            **self.kwargs
        )
    
    @generate_fallback(ContentType.PLANTUML, error_message="Не смог сгенерировать схему")
    def __generate_plantum(self):
        jar_path = os.path.join(Config.BASE_DIR, "tools", Config.PLANTUML_JAR_FILE_NAME)

        result = None

        try:
            result = subprocess.run(
                ["java", "-jar", jar_path, "-tsvg", "-pipe"],
                input=self.raw_content.encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            ).stdout.decode("utf-8")

            if not result.strip():
                result = "PlantUML-схема не сгенерирована. Проверьте исходный текст"

        except subprocess.CalledProcessError as e:
             error_msg = e.stderr.decode("utf-8") if e.stderr else str(e)
             result = f"Ошибка генерации PlantUML:\n{error_msg}"

        return render_template(
            'content/plantuml.html',
            content=result,
            **self.kwargs
        )
    
    @generate_fallback(ContentType.DRAWIO, error_message="Не смог сгенерировать схему")
    def __generate_drawio(self):
        drawio_client = DrawIO()
        content = drawio_client.render_png(self.raw_content)

        if isinstance(content, RequestException):
            return content

        if content:
            return self.__content_success(content, 'content/drawio.html')
        