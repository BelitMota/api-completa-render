"""
Rotas de autenticação.

Neste arquivo fica o endpoint /login.
"""

from flask import Blueprint, request, jsonify

from auth import autenticar_usuario, gerar_token


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Endpoint de login.

    Espera receber um JSON no formato:

    {
        "email": "admin@teste.com",
        "senha": "123456"
    }

    Se os dados estiverem corretos, retorna um token JWT.
    """

    dados = request.get_json()

    if dados is None:
        return jsonify({
            "erro": "JSON não enviado"
        }), 400

    email = dados.get("email")
    senha = dados.get("senha")

    if not email or not senha:
        return jsonify({
            "erro": "Email e senha são obrigatórios"
        }), 400

    usuario = autenticar_usuario(email, senha)

    if usuario is None:
        return jsonify({
            "erro": "Email ou senha inválidos"
        }), 401

    token = gerar_token(usuario)

    return jsonify({
        "mensagem": "Login realizado com sucesso",
        "token": token,
        "tipo": "Bearer",
        "expira_em": "2 horas",
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
            "perfil": usuario["perfil"]
        }
    })