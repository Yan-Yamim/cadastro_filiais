from typing import List
from fastapi import FastAPI, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from cadastro_filiados import models, schemas
from cadastro_filiados.database import get_session

app = FastAPI()


@app.post(
    "/cadastro/",
    response_model=schemas.UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Usuários"],
)
async def criar_usuario(
    usuario_in: schemas.UsuarioCreate,
    db: AsyncSession = Depends(get_session),
):
    """
    Cria um novo usuário cadastrando simultaneamente seu endereço e suas atividades (Assíncrono).
    """
    db_endereco = None
    if usuario_in.endereco:
        db_endereco = models.Endereco(**usuario_in.endereco.model_dump())
        db.add(db_endereco)
        await db.flush() 

    lista_atividades = [
        models.Atividade(**atividade.model_dump())
        for atividade in usuario_in.atividades
    ]

    db_usuario = models.Usuario(
        nome_completo=usuario_in.nome_completo,
        data_nascimento=usuario_in.data_nascimento,
        telefone=usuario_in.telefone,
        is_active=usuario_in.is_active,
        endereco_id=db_endereco.endereco_id if db_endereco else None,
        atividades=lista_atividades,
    )

    db.add(db_usuario)
    await db.commit()
    await db.refresh(db_usuario)

    return db_usuario


@app.get(
    "/usuarios/", 
    response_model=List[schemas.UsuarioResponse], 
    tags=["Usuários"]
)
async def listar_usuarios(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_session)
):
    """Lista todos os usuários cadastrados."""
    return await db.query(models.Usuario).offset(skip).limit(limit).all()

