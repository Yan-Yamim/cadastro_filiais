from datetime import date, datetime

from sqlalchemy import Boolean, Date, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


@table_registry.mapped_as_dataclass
class Endereco:
    __tablename__ = 'enderecos'

    endereco_id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True
    )
    cep: Mapped[str] = mapped_column(String(10), nullable=False)
    bairro: Mapped[str] = mapped_column(String(100), nullable=False)
    rua: Mapped[str] = mapped_column(String(150), nullable=False)
    numero: Mapped[str] = mapped_column(String(20), nullable=False)
    complemento: Mapped[str | None] = mapped_column(
        String(100), nullable=True, default=None
    )

    usuarios: Mapped[list['Usuario']] = relationship(
        'Usuario', 
        back_populates='endereco', 
        init=False, 
        default_factory=list,
        lazy='selectin'
    )


@table_registry.mapped_as_dataclass
class Usuario:
    __tablename__ = 'usuarios'

    usuario_id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True
    )
    nome_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    
    endereco_id: Mapped[int | None] = mapped_column(
        ForeignKey('enderecos.endereco_id', ondelete='SET NULL'),
        nullable=True,
        default=None,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    endereco: Mapped['Endereco | None'] = relationship(
        'Endereco', back_populates='usuarios', init=False, default=None
    )
    atividades: Mapped[list['Atividade']] = relationship(
        'Atividade',
        back_populates='usuario',
        cascade='all, delete-orphan',
        init=False,
        default_factory=list,
        lazy='selectin'
    )


@table_registry.mapped_as_dataclass
class Atividade:
    __tablename__ = 'atividades'

    atividade_id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True
    )
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey('usuarios.usuario_id', ondelete='CASCADE'), nullable=False
    )
    canal: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)

    usuario: Mapped['Usuario'] = relationship(
        'Usuario', 
        back_populates='atividades', 
        init=False,
        lazy='selectin'
    )