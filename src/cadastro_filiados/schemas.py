from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class EnderecoBase(BaseModel):
    cep: str
    bairro: str
    rua: str
    numero: str
    complemento: Optional[str] = None


class EnderecoCreate(EnderecoBase):
    pass


class EnderecoResponse(EnderecoBase):
    endereco_id: int

    model_config = ConfigDict(from_attributes=True)


class AtividadeBase(BaseModel):
    canal: str
    descricao: str


class AtividadeCreate(AtividadeBase):
    pass


class AtividadeResponse(AtividadeBase):
    atividade_id: int
    usuario_id: int

    model_config = ConfigDict(from_attributes=True)


class UsuarioBase(BaseModel):
    nome_completo: str
    data_nascimento: date
    telefone: str
    is_active: bool = True


class UsuarioCreate(UsuarioBase):
    endereco: Optional[EnderecoCreate] = None
    atividades: List[AtividadeCreate] = []


class UsuarioResponse(UsuarioBase):
    usuario_id: int
    created_at: datetime
    endereco: Optional[EnderecoResponse] = None
    atividades: List[AtividadeResponse] = []

    model_config = ConfigDict(from_attributes=True)