"""
Arquivo principal da aplicação Flask.

Este arquivo é responsável por:
1. Criar a aplicação Flask.
2. Inicializar o banco de dados SQLite.
3. Registrar os Blueprints, que são conjuntos de rotas separados por assunto.
4. Criar uma rota inicial apenas para mostrar que a API está funcionando.

Observação importante para a aula:
- No desenvolvimento local, podemos rodar com: python app.py
- No Render, normalmente usamos: gunicorn app:app

Na expressão gunicorn app:app:
- o primeiro "app" é o nome deste arquivo: app.py
- o segundo "app" é a variável Flask criada abaixo: app = Flask(__name__)
"""

from flask import Flask, jsonify

from database import iniciar_banco
from routes.auth_routes import auth_bp
from routes.clientes_routes import clientes_bp
from routes.produtos_routes import produtos_bp
from routes.notas_routes import notas_bp


app = Flask(__name__)


# Inicializa o banco de dados.
# Se as tabelas ainda não existirem, elas serão criadas.
# Se os dados iniciais ainda não existirem, eles serão inseridos.
iniciar_banco()


# Registro dos Blueprints.
# Blueprint é uma forma simples de separar as rotas em arquivos diferentes.
# Isso evita deixar todo o projeto dentro de um único app.py gigante.
app.register_blueprint(auth_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(produtos_bp)
app.register_blueprint(notas_bp)


@app.route("/", methods=["GET"])
def home():
    """
    Rota inicial da API.

    Esta rota serve apenas para documentação rápida.
    Ela mostra quais endpoints existem no projeto.

    Importante:
    - Aqui eu evitei usar "<id>" na resposta, porque alguns serializadores
      exibem isso como \\u003Cid\\u003E.
    - Por isso, nos exemplos, usei diretamente "/clientes/1", "/produtos/1" etc.
    """

    return jsonify({
        "mensagem": "API de clientes, produtos e notas fiscais funcionando",
        "autenticacao": {
            "login": "POST /login",
            "usuario_teste": {
                "email": "admin@teste.com",
                "senha": "123456"
            }
        },
        "regras_de_acesso": {
            "GET_sem_token": "Funciona, mas mostra poucos dados",
            "GET_com_token": "Funciona e mostra mais detalhes",
            "POST_PUT_DELETE": "Exigem token JWT"
        },
        "endpoints": {
            "clientes": [
                "GET /clientes",
                "GET /clientes/1",
                "POST /clientes",
                "PUT /clientes/1",
                "DELETE /clientes/1"
            ],
            "produtos": [
                "GET /produtos",
                "GET /produtos/1",
                "POST /produtos",
                "PUT /produtos/1",
                "DELETE /produtos/1"
            ],
            "notas_fiscais": [
                "GET /notas",
                "GET /notas/1",
                "POST /notas",
                "PUT /notas/1",
                "DELETE /notas/1"
            ]
        }
    })


if __name__ == "__main__":
    # Este bloco só é usado quando rodamos localmente com:
    # python app.py
    #
    # No Render, quem executa a aplicação é o Gunicorn.
    app.run(debug=True)