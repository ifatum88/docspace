import markdown as md
from enum import Enum
from flask import render_template

class ContentType(Enum):
    MARKDOWN = "markdown"
    PLAINTEXT = "plain-text"
    HTML = "html"

class Content:

    def __init__(self, content:str, content_type:object) -> str:
        self.raw_content = content
        self.content_type = self.__convert_to_contenttype(content_type)
        self.content = self.generate() or "No Content"

    def generate(self):

        if self.raw_content and self.content_type:
            match self.content_type:
                case ContentType.MARKDOWN:
                    return self.__generate_markdown() 
                case ContentType.HTML:
                    return self.__generate_html()
                case ContentType.PLAINTEXT:
                    return self.__generate_plaintext()

    def __convert_to_contenttype(self, _type):
        if isinstance(_type, ContentType):
            return _type
        try:
            return ContentType(_type)
        except:
            ContentType.HTML

    def __generate_markdown(self):
        return render_template (
            'partials/markdown.html',
            content=md.markdown(self.raw_content, extensions=['fenced_code', 'tables'])
        )
    
    def __generate_html(self):
        return self.raw_content  # Просто отдаём html как есть

    def __generate_plaintext(self):
        return f"<pre>{self.raw_content}</pre>"  # Примитивный рендер текста
        