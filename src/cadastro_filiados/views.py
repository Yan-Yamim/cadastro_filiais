from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from cadastro_filiados import models, schemas
from cadastro_filiados.database import get_session

router = APIRouter()


@router.post(
    "/cadastro",
    response_model=schemas.UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Usuários"],
)
async def criar_usuario(
    usuario_in: schemas.UsuarioCreate,
    db: AsyncSession = Depends(get_session),
):
    db_endereco = None
    if usuario_in.endereco:
        db_endereco = models.Endereco(**usuario_in.endereco.model_dump())
        db.add(db_endereco)
        await db.flush()

    db_usuario = models.Usuario(
        nome_completo=usuario_in.nome_completo,
        data_nascimento=usuario_in.data_nascimento,
        telefone=usuario_in.telefone,
        is_active=usuario_in.is_active,
        endereco_id=db_endereco.endereco_id if db_endereco else None,
    )
    db.add(db_usuario)
    await db.flush()  

    if usuario_in.atividades:
        lista_atividades = [
            models.Atividade(
                **atividade.model_dump(),
                usuario_id=db_usuario.usuario_id,  
            )
            for atividade in usuario_in.atividades
        ]
        db.add_all(lista_atividades)

    await db.commit()
    await db.refresh(db_usuario, attribute_names=["endereco", "atividades"])

    return db_usuario


@router.get(
    "/usuarios", 
    response_model=List[schemas.UsuarioResponse], 
    tags=["Usuários"]
)
async def listar_usuarios(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_session)
):
    """Lista todos os usuários cadastrados."""
    query = (
        select(models.Usuario)
        .options(
            selectinload(models.Usuario.endereco),
            selectinload(models.Usuario.atividades),
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()

