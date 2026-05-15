"""
Rotas de produtos.

Regras:
- GET funciona sem token, mas mostra menos informações.
- GET com token mostra mais informações.
- POST, PUT e DELETE exigem token JWT.
"""

import sqlite3

from flask import Blueprint, request, jsonify

from database import conectar
from auth import obter_payload_token_opcional, obter_payload_token_obrigatorio


produtos_bp = Blueprint("produtos", __name__)


def formatar_produto(linha, autenticado):
    """
    Converte uma linha do banco em dicionário.

    Sem token:
    - mostra dados básicos de catálogo.

    Com token:
    - mostra também estoque, descrição e código interno.
    """

    produto = {
        "id": linha["id"],
        "nome": linha["nome"],
        "preco": linha["preco"]
    }

    if autenticado:
        produto["descricao"] = linha["descricao"]
        produto["estoque"] = linha["estoque"]
        produto["codigo_interno"] = linha["codigo_interno"]

    return produto


@produtos_bp.route("/produtos", methods=["GET"])
def listar_produtos():
    payload = obter_payload_token_opcional()
    autenticado = payload is not None

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, descricao, preco, estoque, codigo_interno
        FROM produtos
        ORDER BY id
    """)

    produtos = []

    for linha in cursor.fetchall():
        produtos.append(formatar_produto(linha, autenticado))

    conexao.close()

    return jsonify(produtos)


@produtos_bp.route("/produtos/<int:id>", methods=["GET"])
def buscar_produto(id):
    payload = obter_payload_token_opcional()
    autenticado = payload is not None

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, descricao, preco, estoque, codigo_interno
        FROM produtos
        WHERE id = ?
    """, (id,))

    linha = cursor.fetchone()

    conexao.close()

    if linha is None:
        return jsonify({
            "erro": "Produto não encontrado"
        }), 404

    return jsonify(formatar_produto(linha, autenticado))


@produtos_bp.route("/produtos", methods=["POST"])
def criar_produto():
    payload, erro = obter_payload_token_obrigatorio()

    if erro is not None:
        return erro

    dados = request.get_json()

    if dados is None:
        return jsonify({
            "erro": "JSON não enviado"
        }), 400

    nome = dados.get("nome")
    descricao = dados.get("descricao")
    preco = dados.get("preco")
    estoque = dados.get("estoque")
    codigo_interno = dados.get("codigo_interno")

    if not nome or preco is None or estoque is None:
        return jsonify({
            "erro": "Campos obrigatórios: nome, preco e estoque"
        }), 400

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO produtos (nome, descricao, preco, estoque, codigo_interno)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, descricao, preco, estoque, codigo_interno))

    conexao.commit()

    novo_id = cursor.lastrowid

    conexao.close()

    return jsonify({
        "mensagem": "Produto criado com sucesso",
        "produto": {
            "id": novo_id,
            "nome": nome,
            "descricao": descricao,
            "preco": preco,
            "estoque": estoque,
            "codigo_interno": codigo_interno
        }
    }), 201


@produtos_bp.route("/produtos/<int:id>", methods=["PUT"])
def atualizar_produto(id):
    payload, erro = obter_payload_token_obrigatorio()

    if erro is not None:
        return erro

    dados = request.get_json()

    if dados is None:
        return jsonify({
            "erro": "JSON não enviado"
        }), 400

    nome = dados.get("nome")
    descricao = dados.get("descricao")
    preco = dados.get("preco")
    estoque = dados.get("estoque")
    codigo_interno = dados.get("codigo_interno")

    if not nome or preco is None or estoque is None:
        return jsonify({
            "erro": "Campos obrigatórios: nome, preco e estoque"
        }), 400

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE produtos
        SET nome = ?, descricao = ?, preco = ?, estoque = ?, codigo_interno = ?
        WHERE id = ?
    """, (nome, descricao, preco, estoque, codigo_interno, id))

    conexao.commit()

    linhas_afetadas = cursor.rowcount

    conexao.close()

    if linhas_afetadas == 0:
        return jsonify({
            "erro": "Produto não encontrado"
        }), 404

    return jsonify({
        "mensagem": "Produto atualizado com sucesso"
    })


@produtos_bp.route("/produtos/<int:id>", methods=["DELETE"])
def remover_produto(id):
    payload, erro = obter_payload_token_obrigatorio()

    if erro is not None:
        return erro

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            DELETE FROM produtos
            WHERE id = ?
        """, (id,))

        conexao.commit()

        linhas_afetadas = cursor.rowcount

    except sqlite3.IntegrityError:
        conexao.close()

        return jsonify({
            "erro": "Não é possível remover este produto",
            "motivo": "Existem notas fiscais com este produto"
        }), 409

    conexao.close()

    if linhas_afetadas == 0:
        return jsonify({
            "erro": "Produto não encontrado"
        }), 404

    return jsonify({
        "mensagem": "Produto removido com sucesso"
    })