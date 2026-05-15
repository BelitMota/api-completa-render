"""
Rotas de clientes.

Regras:
- GET /clientes e GET /clientes/1 funcionam sem token.
- Se o token for enviado no GET, mostramos mais informações.
- POST, PUT e DELETE exigem token JWT.
"""

import sqlite3

from flask import Blueprint, request, jsonify

from database import conectar
from auth import obter_payload_token_opcional, obter_payload_token_obrigatorio


clientes_bp = Blueprint("clientes", __name__)


def formatar_cliente(linha, autenticado):
    """
    Converte uma linha do banco em dicionário.

    Se autenticado for False:
    - mostra poucos dados.

    Se autenticado for True:
    - mostra mais dados.
    """

    cliente = {
        "id": linha["id"],
        "nome": linha["nome"]
    }

    if autenticado:
        cliente["email"] = linha["email"]
        cliente["telefone"] = linha["telefone"]
        cliente["documento"] = linha["documento"]

    return cliente


@clientes_bp.route("/clientes", methods=["GET"])
def listar_clientes():
    payload = obter_payload_token_opcional()
    autenticado = payload is not None

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, email, telefone, documento
        FROM clientes
        ORDER BY id
    """)

    clientes = []

    for linha in cursor.fetchall():
        clientes.append(formatar_cliente(linha, autenticado))

    conexao.close()

    return jsonify(clientes)


@clientes_bp.route("/clientes/<int:id>", methods=["GET"])
def buscar_cliente(id):
    payload = obter_payload_token_opcional()
    autenticado = payload is not None

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, email, telefone, documento
        FROM clientes
        WHERE id = ?
    """, (id,))

    linha = cursor.fetchone()

    conexao.close()

    if linha is None:
        return jsonify({
            "erro": "Cliente não encontrado"
        }), 404

    return jsonify(formatar_cliente(linha, autenticado))


@clientes_bp.route("/clientes", methods=["POST"])
def criar_cliente():
    payload, erro = obter_payload_token_obrigatorio()

    if erro is not None:
        return erro

    dados = request.get_json()

    if dados is None:
        return jsonify({
            "erro": "JSON não enviado"
        }), 400

    nome = dados.get("nome")
    email = dados.get("email")
    telefone = dados.get("telefone")
    documento = dados.get("documento")

    if not nome or not email:
        return jsonify({
            "erro": "Campos obrigatórios: nome e email"
        }), 400

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO clientes (nome, email, telefone, documento)
        VALUES (?, ?, ?, ?)
    """, (nome, email, telefone, documento))

    conexao.commit()

    novo_id = cursor.lastrowid

    conexao.close()

    return jsonify({
        "mensagem": "Cliente criado com sucesso",
        "cliente": {
            "id": novo_id,
            "nome": nome,
            "email": email,
            "telefone": telefone,
            "documento": documento
        }
    }), 201


@clientes_bp.route("/clientes/<int:id>", methods=["PUT"])
def atualizar_cliente(id):
    payload, erro = obter_payload_token_obrigatorio()

    if erro is not None:
        return erro

    dados = request.get_json()

    if dados is None:
        return jsonify({
            "erro": "JSON não enviado"
        }), 400

    nome = dados.get("nome")
    email = dados.get("email")
    telefone = dados.get("telefone")
    documento = dados.get("documento")

    if not nome or not email:
        return jsonify({
            "erro": "Campos obrigatórios: nome e email"
        }), 400

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE clientes
        SET nome = ?, email = ?, telefone = ?, documento = ?
        WHERE id = ?
    """, (nome, email, telefone, documento, id))

    conexao.commit()

    linhas_afetadas = cursor.rowcount

    conexao.close()

    if linhas_afetadas == 0:
        return jsonify({
            "erro": "Cliente não encontrado"
        }), 404

    return jsonify({
        "mensagem": "Cliente atualizado com sucesso"
    })


@clientes_bp.route("/clientes/<int:id>", methods=["DELETE"])
def remover_cliente(id):
    payload, erro = obter_payload_token_obrigatorio()

    if erro is not None:
        return erro

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            DELETE FROM clientes
            WHERE id = ?
        """, (id,))

        conexao.commit()

        linhas_afetadas = cursor.rowcount

    except sqlite3.IntegrityError:
        conexao.close()

        return jsonify({
            "erro": "Não é possível remover este cliente",
            "motivo": "Existem notas fiscais vinculadas a ele"
        }), 409

    conexao.close()

    if linhas_afetadas == 0:
        return jsonify({
            "erro": "Cliente não encontrado"
        }), 404

    return jsonify({
        "mensagem": "Cliente removido com sucesso"
    })