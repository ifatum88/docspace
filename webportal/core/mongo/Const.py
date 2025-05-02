# Соответствие bsonType -> type
BSON_TO_JSON_TYPE = {
    "objectId": "objectId",
    "string": "string",
    "int": "integer",
    "long": "integer",
    "double": "number",
    "bool": "boolean",
    "date": "date", 
    "array": "array",
    "object": "object"
}

JSON_VALIDATION_RULES = [
    "pattern", 
    "minLength", 
    "maxLength", 
    "minItems", 
    "format", 
    "minimum"
]
