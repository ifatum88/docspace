import os
import subprocess

from enum import Enum
from flask import render_template
from config import Config

class ContentType(Enum):
    MARKDOWN = "markdown"
    PLAINTEXT = "plain-text"
    HTML = "html"
    RAW = "raw"
    PLANTUML = "plantuml"

class ContentGenerationMode(Enum):
    SERVER_SIDE = "server-side"
    REMOTE_SERVER = "remote-server"

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
            ContentType.PLANTUML: self.__generate_plantum
        }

        if not self.raw_content or not self.content_type:
            return None

        return generators.get(self.content_type)()

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
        