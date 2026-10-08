from unittest.mock import patch
import pytest
from fastapi import status
from sqlalchemy import select
from cadastro_filiados.models import Usuario, Endereco, Atividade


@pytest.mark.asyncio(loop_scope="function")
async def test_criar_usuario_sucesso_201(client, session):
    """
    Cenário 201: Cadastro completo (Usuário, Endereço e Atividades) criado com sucesso.
    """
    payload = {
        "nome_completo": "Ana Souza",
        "data_nascimento": "1998-05-15",
        "telefone": "11912345678",
        "is_active": True,
        "endereco": {
            "cep": "01001-000",
            "bairro": "Centro",
            "rua": "Rua Direita",
            "numero": "100",
            "complemento": "Apto 42",
        },
        "atividades": [
            {
                "canal": "E-mail",
                "descricao": "Envio de relatórios mensais",
            }
        ],
    }

    response = await client.post("/cadastro/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["usuario_id"] is not None
    assert data["nome_completo"] == "Ana Souza"
    assert data["endereco"]["cep"] == "01001-000"
    assert len(data["atividades"]) == 1
    assert data["atividades"][0]["canal"] == "E-mail"

    stmt = select(Usuario).where(Usuario.usuario_id == data["usuario_id"])
    result = await session.execute(stmt)
    usuario_db = result.scalar_one_or_none()

    assert usuario_db is not None
    assert usuario_db.nome_completo == "Ana Souza"


@pytest.mark.asyncio(loop_scope="function")
async def test_criar_usuario_erro_validacao_422(client):
    """
    Cenário de erro na validação dos dados de entrada (Pydantic / Schema).
    Envio de tipo inválido em data_nascimento.
    """
    payload_invalido = {
        "nome_completo": "Carlos Oliveira",
        "data_nascimento": "formato-invalido",
        "telefone": "11988887777",
        "endereco": {
            "cep": "02002-000",
            "bairro": "Santana",
            "rua": "Rua Voluntários da Pátria",
            "numero": "500",
        },
    }

    response = await client.post("/cadastro/", json=payload_invalido)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio(loop_scope="function")
async def test_criar_usuario_erro_interno_500(client):
    """
    Cenário 500: Erro inesperado durante a gravação no banco de dados.
    Simulado injetando uma exceção no momento do db.commit().
    """
    payload = {
        "nome_completo": "Marcos Lima",
        "data_nascimento": "1990-01-01",
        "telefone": "11977776666",
        "endereco": {
            "cep": "03003-000",
            "bairro": "Mooca",
            "rua": "Rua da Mooca",
            "numero": "200",
        },
        "atividades": [],
    }

    with patch(
        "sqlalchemy.ext.asyncio.AsyncSession.commit",
        side_effect=Exception("Falha crítica de banco de dados"),
    ):
        with pytest.raises(Exception):
            await client.post("/cadastro/", json=payload)