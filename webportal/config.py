class Config:
    APP_VESION = "0.1.0"
    APP_NAME = "DocSpace"

    BASE_DIR = "/Users/dgich/Yandex.Disk.localized/Проекты/corp-docs-project/webportal"
    LOG_DIR = "logs"
    
    MONGO_URL = "mongodb://localhost:27017"
    MONGO_DATABASE_NAME = "docspace"

    MARKDOWN_MODE = "server-side" #server-side or remote-server
    MARKDOWN_URL = None

    PLANTUML_MODE = "server-side" #server-side or remote-server
    PLANTUML_URL = None
    PLANTUML_JAR_FILE_NAME = "plantuml-mit-1.2025.2.jar"