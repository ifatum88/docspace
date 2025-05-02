from enum import Enum
from dataclasses import dataclass, field
from typing import Union, List, Optional

class ModelFieldTypes(Enum):
    STRING = "string"
    INT = "integer"
    OBJECTID = "objectId"
    BOOLEAN = "boolean"
    NUMBER = "number"
    ARRAY = "array"
    DATE = "date"

    def __str__(self):
        return self.value
    
@dataclass(frozen=True)
class ModelFieldSources(Enum):
    MODEL = "model"
    MONGO = "mongo"

@dataclass(frozen=True)
class ModelField:
    type: Union['ModelFieldTypes', List['ModelFieldTypes']]
    source: ModelFieldSources = ModelFieldSources.MODEL
    name: Optional[str] = None
    default_val: Optional[any] = None
    is_required: bool = False
    validation_rules: dict = field(default_factory=dict)

    def __repr__(self):
        return f"<{self.__class__.__name__}. Name={self.name}, Type={self.type}, Val={self.default_val}>"

    def __str__(self):
        return f"<{self.__class__.__name__}. Name={self.name}, Type={self.type}, Val={self.default_val}>"
    
    def __eq__(self, other):
        return isinstance(other, ModelField) and self.name == other.name and self.type == other.type

    def __hash__(self):
        return hash((self.name, str(self.type)))

    def __post_init__(self):
        if not isinstance(self.type, (ModelFieldTypes, list)):
            raise TypeError(f"Invalid type: {self.type}")
