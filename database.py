"""
Arquivo responsável pelo banco de dados SQLite.

Aqui ficam:
1. A conexão com o banco.
2. A criação das tabelas.
3. A inserção dos dados iniciais, também chamados de seed.

Seed significa:
- dados iniciais colocados no banco automaticamente;
- úteis para teste;
- úteis para aula;
- evitam começar o projeto com banco vazio.

Neste exemplo, usamos SQLite porque ele é simples:
- não precisa instalar servidor de banco;
- o banco fica em um arquivo;
- é suficiente para uma aula de API REST.

Atenção:
- No plano gratuito do Render, o arquivo SQLite pode não ser persistente.
- Isso serve bem para demonstração, mas não deve ser tratado como solução final de produção.
"""

import os
import sqlite3


# Caminho do arquivo SQLite.
# O banco será criado na mesma pasta do projeto.
CAMINHO_BANCO = os.path.join(os.path.dirname(__file__), "banco.sqlite3")


def conectar():
    """
    Cria e retorna uma conexão com o banco SQLite.

    row_factory = sqlite3.Row permite acessar os resultados como se fossem dicionários.
    Exemplo:
        linha["nome"]

    Sem isso, o SQLite retornaria tuplas.
    Exemplo:
        linha[0], linha[1], linha[2]
    """

    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row

    # No SQLite, chaves estrangeiras precisam ser ativadas em cada conexão.
    # Isso permite que o banco respeite os relacionamentos entre tabelas.
    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao


def iniciar_banco():
    """
    Cria as tabelas e insere os dados iniciais.

    Esta função é chamada quando a aplicação inicia.
    """

    conexao = conectar()
    cursor = conexao.cursor()

    criar_tabelas(cursor)
    inserir_seeds(cursor)

    conexao.commit()
    conexao.close()


def criar_tabelas(cursor):
    """
    Cria as tabelas do sistema.

    Tabelas principais:
    - clientes
    - produtos
    - notas_fiscais

    Tabela auxiliar:
    - itens_nota_fiscal

    A tabela itens_nota_fiscal existe porque uma nota fiscal pode ter vários produtos.
    Esse é um relacionamento clássico de banco de dados.
    """

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            telefone TEXT,
            documento TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL,
            codigo_interno TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas_fiscais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            data_emissao TEXT NOT NULL,
            observacao TEXT,

            FOREIGN KEY (cliente_id)
                REFERENCES clientes(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_nota_fiscal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nota_fiscal_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,

            FOREIGN KEY (nota_fiscal_id)
                REFERENCES notas_fiscais(id)
                ON DELETE CASCADE,

            FOREIGN KEY (produto_id)
                REFERENCES produtos(id)
        )
    """)


def contar_registros(cursor, nome_tabela):
    """
    Conta quantos registros existem em uma tabela.

    Esta função é usada para saber se devemos ou não inserir os seeds.
    """

    cursor.execute(f"SELECT COUNT(*) AS total FROM {nome_tabela}")
    resultado = cursor.fetchone()

    return resultado["total"]


def inserir_seeds(cursor):
    """
    Insere dados iniciais no banco.

    A lógica é simples:
    - Se a tabela clientes estiver vazia, insere alguns clientes.
    - Se a tabela produtos estiver vazia, insere alguns produtos.
    - Se a tabela notas_fiscais estiver vazia, insere algumas notas e seus itens.

    Isso evita duplicar os dados toda vez que a aplicação iniciar.
    """

    if contar_registros(cursor, "clientes") == 0:
        cursor.executemany("""
            INSERT INTO clientes (nome, email, telefone, documento)
            VALUES (?, ?, ?, ?)
        """, [
            ("Maria Silva", "maria@email.com", "1599999-1111", "123.456.789-00"),
            ("João Souza", "joao@email.com", "1599999-2222", "987.654.321-00"),
            ("Empresa ABC Ltda", "contato@empresaabc.com", "153333-4444", "12.345.678/0001-99")
        ])

    if contar_registros(cursor, "produtos") == 0:
        cursor.executemany("""
            INSERT INTO produtos (nome, descricao, preco, estoque, codigo_interno)
            VALUES (?, ?, ?, ?, ?)
        """, [
            ("Mouse", "Mouse USB simples", 49.90, 30, "PROD-MOUSE-001"),
            ("Teclado", "Teclado ABNT2", 89.90, 20, "PROD-TECLADO-002"),
            ("Monitor", "Monitor LED 24 polegadas", 799.90, 8, "PROD-MONITOR-003"),
            ("Notebook", "Notebook para uso acadêmico", 3499.90, 5, "PROD-NOTE-004")
        ])

    if contar_registros(cursor, "notas_fiscais") == 0:
        cursor.execute("""
            INSERT INTO notas_fiscais (cliente_id, data_emissao, observacao)
            VALUES (?, datetime('now'), ?)
        """, (1, "Primeira nota fiscal de exemplo"))

        nota_1_id = cursor.lastrowid

        cursor.executemany("""
            INSERT INTO itens_nota_fiscal
                (nota_fiscal_id, produto_id, quantidade, preco_unitario)
            VALUES (?, ?, ?, ?)
        """, [
            (nota_1_id, 1, 2, 49.90),
            (nota_1_id, 2, 1, 89.90)
        ])

        cursor.execute("""
            INSERT INTO notas_fiscais (cliente_id, data_emissao, observacao)
            VALUES (?, datetime('now'), ?)
        """, (2, "Segunda nota fiscal de exemplo"))

        nota_2_id = cursor.lastrowid

        cursor.executemany("""
            INSERT INTO itens_nota_fiscal
                (nota_fiscal_id, produto_id, quantidade, preco_unitario)
            VALUES (?, ?, ?, ?)
        """, [
            (nota_2_id, 3, 1, 799.90),
            (nota_2_id, 1, 1, 49.90)
        ])