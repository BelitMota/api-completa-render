"""
Rotas de notas fiscais.

Aqui aparece o relacionamento mais interessante da API:

Uma nota fiscal pertence a UM cliente.
Uma nota fiscal possui N produtos.
Cada produto dentro da nota fica registrado na tabela itens_nota_fiscal.

A tabela itens_nota_fiscal guarda:
- qual é a nota;
- qual é o produto;
- quantidade;
- preço unitário no momento da venda.

Por que guardar o preço unitário no item da nota?

Porque o preço do produto pode mudar depois.
Se o produto custava R$ 50,00 no dia da venda, a nota precisa preservar esse valor,
mesmo que amanhã o produto passe a custar R$ 70,00.
"""

from flask import Blueprint, request, jsonify

from database import conectar
from auth import obter_payload_token_opcional, obter_payload_token_obrigatorio


notas_bp = Blueprint("notas", __name__)


def buscar_itens_da_nota(cursor, nota_fiscal_id, autenticado):
    """
    Busca os produtos vinculados a uma nota fiscal.

    Sem token:
    - podemos omitir os itens na listagem principal.

    Com token:
    - mostramos detalhes dos produtos da nota.
    """

    cursor.execute("""
        SELECT
            itens.id,
            itens.produto_id,
            produtos.nome AS produto_nome,
            produtos.codigo_interno,
            itens.quantidade,
            itens.preco_unitario,
            (itens.quantidade * itens.preco_unitario) AS subtotal
        FROM itens_nota_fiscal AS itens
        INNER JOIN produtos
            ON produtos.id = itens.produto_id
        WHERE itens.nota_fiscal_id = ?
        ORDER BY itens.id
    """, (nota_fiscal_id,))

    itens = []

    for linha in cursor.fetchall():
        item = {
            "id": linha["id"],
            "produto": {
                "id": linha["produto_id"],
                "nome": linha["produto_nome"]
            },
            "quantidade": linha["quantidade"],
            "preco_unitario": linha["preco_unitario"],
            "subtotal": linha["subtotal"]
        }

        if autenticado:
            item["produto"]["codigo_interno"] = linha["codigo_interno"]

        itens.append(item)

    return itens


def formatar_nota(cursor, linha, autenticado):
    """
    Formata uma nota fiscal para resposta JSON.

    Sem token:
    - mostra id, data, nome do cliente e valor total.
    - não mostra documento, email, telefone, observação nem itens.

    Com token:
    - mostra os dados completos.
    """

    nota = {
        "id": linha["id"],
        "data_emissao": linha["data_emissao"],
        "cliente": {
            "id": linha["cliente_id"],
            "nome": linha["cliente_nome"]
        },
        "valor_total": linha["valor_total"]
    }

    if autenticado:
        nota["observacao"] = linha["observacao"]

        nota["cliente"]["email"] = linha["cliente_email"]
        nota["cliente"]["telefone"] = linha["cliente_telefone"]
        nota["cliente"]["documento"] = linha["cliente_documento"]

        nota["itens"] = buscar_itens_da_nota(
            cursor,
            linha["id"],
            autenticado
        )

    return nota


def consultar_notas_base(cursor, where_sql="", parametros=()):
    """
    Consulta notas fiscais com cliente e valor total.

    Essa função evita repetir a mesma consulta SQL em listar e buscar por id.

    O valor total da nota é calculado com:
        SUM(quantidade * preco_unitario)

    COALESCE serve para retornar 0 caso a nota não tenha itens.
    """

    sql = f"""
        SELECT
            notas.id,
            notas.data_emissao,
            notas.observacao,

            clientes.id AS cliente_id,
            clientes.nome AS cliente_nome,
            clientes.email AS cliente_email,
            clientes.telefone AS cliente_telefone,
            clientes.documento AS cliente_documento,

            COALESCE(
                SUM(itens.quantidade * itens.preco_unitario),
                0
            ) AS valor_total

        FROM notas_fiscais AS notas

        INNER JOIN clientes
            ON clientes.id = notas.cliente_id

        LEFT JOIN itens_nota_fiscal AS itens
            ON itens.nota_fiscal_id = notas.id

        {where_sql}

        GROUP BY
            notas.id,
            notas.data_emissao,
            notas.observacao,
            clientes.id,
            clientes.nome,
            clientes.email,
            clientes.telefone,
            clientes.documento

        ORDER BY notas.id
    """

    cursor.execute(sql, parametros)

    return cursor.fetchall()


def inserir_itens_da_nota(cursor, nota_fiscal_id, itens):
    """
    Insere os itens de uma nota fiscal.

    O corpo esperado no JSON é:

    "itens": [
        {
            "produto_id": 1,
            "quantidade": 2
        },
        {
            "produto_id": 3,
            "quantidade": 1
        }
    ]

    O preço unitário é buscado automaticamente na tabela produtos.
    Isso evita o cliente da API inventar um preço na requisição.
    """

    if not isinstance(itens, list) or len(itens) == 0:
        return {
            "erro": "A nota fiscal precisa ter pelo menos um item"
        }

    for item in itens:
        produto_id = item.get("produto_id")
        quantidade = item.get("quantidade")

        if produto_id is None or quantidade is None:
            return {
                "erro": "Cada item precisa ter produto_id e quantidade"
            }

        if quantidade <= 0:
            return {
                "erro": "A quantidade deve ser maior que zero"
            }

        cursor.execute("""
            SELECT id, preco
            FROM produtos
            WHERE id = ?
        """, (produto_id,))

        produto = cursor.fetchone()

        if produto is None:
            return {
                "erro": f"Produto {produto_id} não encontrado"
            }

        preco_unitario = produto["preco"]

        cursor.execute("""
            INSERT INTO itens_nota_fiscal
                (nota_fiscal_id, produto_id, quantidade, preco_unitario)
            VALUES (?, ?, ?, ?)
        """, (
            nota_fiscal_id,
            produto_id,
            quantidade,
            preco_unitario
        ))

    return None


@notas_bp.route("/notas", methods=["GET"])
def listar_notas():
    payload = obter_payload_token_opcional()
    autenticado = payload is not None

    conexao = conectar()
    cursor = conexao.cursor()

    linhas = consultar_notas_base(cursor)

    notas = []

    for linha in linhas:
        notas.append(formatar_nota(cursor, linha, autenticado))

    conexao.close()

    return jsonify(notas)


@notas_bp.route("/notas/<int:id>", methods=["GET"])
def buscar_nota(id):
    payload = obter_payload_token_opcional()
    autenticado = payload is not None

    conexao = conectar()
    cursor = conexao.cursor()

    linhas = consultar_notas_base(
        cursor,
        "WHERE notas.id = ?",
        (id,)
    )

    if len(linhas) == 0:
        conexao.close()

        return jsonify({
            "erro": "Nota fiscal não encontrada"
        }), 404

    nota = formatar_nota(cursor, linhas[0], autenticado)

    conexao.close()

    return jsonify(nota)


@notas_bp.route("/notas", methods=["POST"])
def criar_nota():
    payload, erro = obter_payload_token_obrigatorio()

    if erro is not None:
        return erro

    dados = request.get_json()

    if dados is None:
        return jsonify({
            "erro": "JSON não enviado"
        }), 400

    cliente_id = dados.get("cliente_id")
    observacao = dados.get("observacao")
    itens = dados.get("itens")

    if cliente_id is None:
        return jsonify({
            "erro": "Campo obrigatório: cliente_id"
        }), 400

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id
        FROM clientes
        WHERE id = ?
    """, (cliente_id,))

    cliente = cursor.fetchone()

    if cliente is None:
        conexao.close()

        return jsonify({
            "erro": "Cliente não encontrado"
        }), 404

    cursor.execute("""
        INSERT INTO notas_fiscais (cliente_id, data_emissao, observacao)
        VALUES (?, datetime('now'), ?)
    """, (cliente_id, observacao))

    nota_fiscal_id = cursor.lastrowid

    erro_itens = inserir_itens_da_nota(
        cursor,
        nota_fiscal_id,
        itens
    )

    if erro_itens is not None:
        conexao.rollback()
        conexao.close()

        return jsonify(erro_itens), 400

    conexao.commit()

    linhas = consultar_notas_base(
        cursor,
        "WHERE notas.id = ?",
        (nota_fiscal_id,)
    )

    nota = formatar_nota(cursor, linhas[0], True)

    conexao.close()

    return jsonify({
        "mensagem": "Nota fiscal criada com sucesso",
        "nota_fiscal": nota
    }), 201


@notas_bp.route("/notas/<int:id>", methods=["PUT"])
def atualizar_nota(id):
    payload, erro = obter_payload_token_obrigatorio()

    if erro is not None:
        return erro

    dados = request.get_json()

    if dados is None:
        return jsonify({
            "erro": "JSON não enviado"
        }), 400

    cliente_id = dados.get("cliente_id")
    observacao = dados.get("observacao")
    itens = dados.get("itens")

    if cliente_id is None:
        return jsonify({
            "erro": "Campo obrigatório: cliente_id"
        }), 400

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id
        FROM notas_fiscais
        WHERE id = ?
    """, (id,))

    nota_existente = cursor.fetchone()

    if nota_existente is None:
        conexao.close()

        return jsonify({
            "erro": "Nota fiscal não encontrada"
        }), 404

    cursor.execute("""
        SELECT id
        FROM clientes
        WHERE id = ?
    """, (cliente_id,))

    cliente = cursor.fetchone()

    if cliente is None:
        conexao.close()

        return jsonify({
            "erro": "Cliente não encontrado"
        }), 404

    cursor.execute("""
        UPDATE notas_fiscais
        SET cliente_id = ?, observacao = ?
        WHERE id = ?
    """, (cliente_id, observacao, id))

    # Estratégia simples para atualização dos itens:
    # 1. Remove os itens antigos.
    # 2. Insere os novos itens.
    #
    # Para uma aula introdutória, isso é mais fácil de entender.
    cursor.execute("""
        DELETE FROM itens_nota_fiscal
        WHERE nota_fiscal_id = ?
    """, (id,))

    erro_itens = inserir_itens_da_nota(
        cursor,
        id,
        itens
    )

    if erro_itens is not None:
        conexao.rollback()
        conexao.close()

        return jsonify(erro_itens), 400

    conexao.commit()

    linhas = consultar_notas_base(
        cursor,
        "WHERE notas.id = ?",
        (id,)
    )

    nota = formatar_nota(cursor, linhas[0], True)

    conexao.close()

    return jsonify({
        "mensagem": "Nota fiscal atualizada com sucesso",
        "nota_fiscal": nota
    })


@notas_bp.route("/notas/<int:id>", methods=["DELETE"])
def remover_nota(id):
    payload, erro = obter_payload_token_obrigatorio()

    if erro is not None:
        return erro

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM notas_fiscais
        WHERE id = ?
    """, (id,))

    conexao.commit()

    linhas_afetadas = cursor.rowcount

    conexao.close()

    if linhas_afetadas == 0:
        return jsonify({
            "erro": "Nota fiscal não encontrada"
        }), 404

    return jsonify({
        "mensagem": "Nota fiscal removida com sucesso"
    })