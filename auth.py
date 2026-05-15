"""
Arquivo responsável pela autenticação JWT.

JWT significa JSON Web Token.

Fluxo básico:
1. O usuário envia email e senha para /login.
2. Se estiver correto, a API gera um token.
3. O cliente copia esse token.
4. Nas próximas requisições protegidas, o cliente envia o token no cabeçalho:

   Authorization: Bearer TOKEN_AQUI

Neste projeto:
- GET funciona sem token, mas mostra menos informações.
- GET com token mostra mais informações.
- POST, PUT e DELETE exigem token.
"""

import os
from datetime import datetime, timedelta, timezone

import jwt
from flask import request, jsonify


# A chave secreta deve ficar em variável de ambiente no Render.
#
# No Render, crie uma variável chamada:
# JWT_SECRET_KEY
#
# Exemplo de valor:
# minha-chave-super-secreta-123456
#
# A chave abaixo é apenas fallback para testes locais.
# Em produção, não é boa prática deixar segredo fixo no código.
JWT_SECRET_KEY = os.environ.get(
    "JWT_SECRET_KEY",
    "chave-local-apenas-para-desenvolvimento"
)


ALGORITMO_JWT = "HS256"


USUARIOS_TESTE = [
    {
        "id": 1,
        "nome": "Administrador",
        "email": "admin@teste.com",
        "senha": "123456",
        "perfil": "admin"
    },
    {
        "id": 2,
        "nome": "Professor",
        "email": "professor@teste.com",
        "senha": "123456",
        "perfil": "professor"
    }
]


def autenticar_usuario(email, senha):
    """
    Verifica se existe um usuário com o email e senha informados.

    Para fins didáticos, a senha está em texto puro.
    Em sistema real, nunca fazemos isso.
    Em sistema real, senhas devem ser armazenadas com hash seguro.
    """

    for usuario in USUARIOS_TESTE:
        if usuario["email"] == email and usuario["senha"] == senha:
            return usuario

    return None


def gerar_token(usuario):
    """
    Gera um token JWT para o usuário autenticado.

    O payload é o conteúdo interno do token.
    Ele guarda informações simples sobre o usuário.

    exp significa expiration.
    É a data/hora em que o token deixa de ser válido.
    """

    payload = {
        "sub": str(usuario["id"]),
        "nome": usuario["nome"],
        "email": usuario["email"],
        "perfil": usuario["perfil"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=2)
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITMO_JWT)

    return token


def extrair_token_da_requisicao():
    """
    Lê o cabeçalho Authorization da requisição.

    O formato esperado é:
        Authorization: Bearer TOKEN_AQUI

    Esta função retorna apenas o token.
    Se o cabeçalho não existir ou estiver em formato errado, retorna None.
    """

    cabecalho = request.headers.get("Authorization")

    if not cabecalho:
        return None

    partes = cabecalho.split()

    if len(partes) != 2:
        return None

    tipo = partes[0]
    token = partes[1]

    if tipo.lower() != "bearer":
        return None

    return token


def decodificar_token(token):
    """
    Tenta decodificar e validar o token JWT.

    Se o token estiver correto, retorna o payload.
    Se estiver inválido ou expirado, retorna None.
    """

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[ALGORITMO_JWT]
        )

        return payload

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None


def obter_payload_token_opcional():
    """
    Usada nas rotas GET.

    A rota GET pode funcionar sem token.
    Porém, se o token for enviado e for válido, podemos mostrar mais dados.

    Retorna:
    - payload, se houver token válido;
    - None, se não houver token ou se ele for inválido.
    """

    token = extrair_token_da_requisicao()

    if token is None:
        return None

    payload = decodificar_token(token)

    return payload


def obter_payload_token_obrigatorio():
    """
    Usada nas rotas POST, PUT e DELETE.

    Essas rotas exigem token.

    Retorna dois valores:
    1. payload do token, se estiver correto;
    2. resposta de erro, se houver problema.

    Exemplo de uso nas rotas:

        payload, erro = obter_payload_token_obrigatorio()

        if erro is not None:
            return erro
    """

    token = extrair_token_da_requisicao()

    if token is None:
        return None, (jsonify({
            "erro": "Token JWT não enviado",
            "orientacao": "Envie o cabeçalho Authorization: Bearer TOKEN"
        }), 401)

    payload = decodificar_token(token)

    if payload is None:
        return None, (jsonify({
            "erro": "Token JWT inválido ou expirado"
        }), 401)

    return payload, None