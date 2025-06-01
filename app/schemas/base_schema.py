from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BaseSchema(BaseModel):
    class Config:
        # orm_mode = True # Linha antiga # Permite que o Pydantic leia dados de modelos ORM (SQLAlchemy)
        from_attributes = True # Nova linha para Pydantic V2+

class TunedModel(BaseModel): # Para respostas, permite orm_mode e formatação de alias
    class Config:
        # orm_mode = True
        # Se você quiser usar alias nos seus modelos Pydantic para os nomes dos campos na API
        # def alias_generator(string: str) -> str:
        #     return ''.join(word.capitalize() for word in string.split('_'))
        # allow_population_by_field_name = True
        from_attributes = True # Nova linha para Pydantic V2+