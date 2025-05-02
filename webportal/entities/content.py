import markdown as md
from enum import Enum
from flask import render_template

class ContentType(Enum):
    MARKDOWN = "markdown"
    PLAINTEXT = "plain-text"
    HTML = "html"

class Content:

    __content = "No content"

    def __init__(self, content:str, content_type:object):
        self.raw_content = content
        self.content_type = self.__convert_to_contenttype(content_type)

    @property
    def content(self):
        return self.generate() or self.__content

    def generate(self):

        generators = {
            ContentType.MARKDOWN: self.__generate_markdown,
            ContentType.HTML: self.__generate_html,
            ContentType.PLAINTEXT: self.__generate_plaintext
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
            return ContentType.HTML

    def __generate_markdown(self):
        return render_template (
            'partials/markdown.html',
            content=md.markdown(self.raw_content, extensions=['fenced_code', 'tables'])
        )
    
    def __generate_html(self):
        return self.raw_content  # Просто отдаём html как есть

    def __generate_plaintext(self):
        return f"<pre>{self.raw_content}</pre>"  # Примитивный рендер текста
        