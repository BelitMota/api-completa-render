# API Flask — Clientes, Produtos e Notas Fiscais

Este projeto é uma API REST simples desenvolvida com **Python**, **Flask**, **SQLite** e **JWT**.

A proposta é servir como exemplo didático para uma aula de desenvolvimento backend, abordando:

- criação de uma API REST;
- uso de rotas `GET`, `POST`, `PUT` e `DELETE`;
- organização básica com Blueprints;
- banco de dados SQLite;
- criação automática das tabelas;
- inserção de dados iniciais, também chamados de *seeds*;
- relacionamento entre tabelas;
- autenticação com JWT;
- uso de variável de ambiente no Render;
- deploy simples em uma plataforma online;
- testes com Thunder Client ou Postman.

---

## 1. Objetivo do projeto

A API simula um sistema simples com:

- clientes;
- produtos;
- notas fiscais.

Cada nota fiscal pertence a um cliente e pode possuir vários produtos.

Para representar corretamente essa relação, o projeto usa uma tabela auxiliar chamada `itens_nota_fiscal`.

Essa tabela auxiliar é necessária porque existe uma relação do tipo:

> uma nota fiscal pode ter vários produtos.

Em banco de dados relacional, esse tipo de relação normalmente é representado por uma tabela intermediária.

---

## 2. Estrutura do projeto

```text
api-notas-flask/
│
├── app.py
├── auth.py
├── database.py
├── requirements.txt
│
└── routes/
    ├── __init__.py
    ├── auth_routes.py
    ├── clientes_routes.py
    ├── produtos_routes.py
    └── notas_routes.py
```

---

## 3. Explicação dos arquivos

### 3.1. `app.py`

Arquivo principal da aplicação.

Responsável por:

- criar a aplicação Flask;
- inicializar o banco de dados;
- registrar os Blueprints;
- criar a rota inicial `/`.

---

### 3.2. `database.py`

Arquivo responsável pelo banco SQLite.

Responsável por:

- conectar ao banco;
- criar as tabelas;
- ativar chaves estrangeiras;
- inserir dados iniciais.

---

### 3.3. `auth.py`

Arquivo responsável pela autenticação.

Responsável por:

- validar email e senha;
- gerar token JWT;
- ler o token enviado no cabeçalho da requisição;
- validar token obrigatório;
- validar token opcional.

---

### 3.4. `routes/auth_routes.py`

Contém a rota de login:

```text
POST /login
```

---

### 3.5. `routes/clientes_routes.py`

Contém as rotas de clientes:

```text
GET    /clientes
GET    /clientes/1
POST   /clientes
PUT    /clientes/1
DELETE /clientes/1
```

---

### 3.6. `routes/produtos_routes.py`

Contém as rotas de produtos:

```text
GET    /produtos
GET    /produtos/1
POST   /produtos
PUT    /produtos/1
DELETE /produtos/1
```

---

### 3.7. `routes/notas_routes.py`

Contém as rotas de notas fiscais:

```text
GET    /notas
GET    /notas/1
POST   /notas
PUT    /notas/1
DELETE /notas/1
```

---

## 4. Modelo de dados

O projeto possui quatro tabelas.

### 4.1. Tabela `clientes`

Armazena os clientes da API.

Campos principais:

```text
id
nome
email
telefone
documento
```

---

### 4.2. Tabela `produtos`

Armazena os produtos disponíveis.

Campos principais:

```text
id
nome
descricao
preco
estoque
codigo_interno
```

---

### 4.3. Tabela `notas_fiscais`

Armazena os dados gerais da nota fiscal.

Campos principais:

```text
id
cliente_id
data_emissao
observacao
```

Cada nota fiscal pertence a um único cliente.

---

### 4.4. Tabela `itens_nota_fiscal`

Armazena os produtos vinculados a cada nota fiscal.

Campos principais:

```text
id
nota_fiscal_id
produto_id
quantidade
preco_unitario
```

Essa tabela existe porque uma nota fiscal pode ter vários produtos.

---

## 5. Regras de autenticação

A API possui dois tipos de comportamento.

---

### 5.1. Rotas `GET`

As rotas `GET` são públicas.

Ou seja, podem ser acessadas sem token JWT.

Porém, quando acessadas sem token, retornam menos informações.

Exemplo:

```text
GET /clientes
```

Sem token, retorna apenas dados básicos:

```json
[
  {
    "id": 1,
    "nome": "Maria Silva"
  }
]
```

Com token JWT, retorna dados completos:

```json
[
  {
    "id": 1,
    "nome": "Maria Silva",
    "email": "maria@email.com",
    "telefone": "1599999-1111",
    "documento": "123.456.789-00"
  }
]
```

---

### 5.2. Rotas `POST`, `PUT` e `DELETE`

As rotas que alteram dados exigem token JWT.

São elas:

```text
POST
PUT
DELETE
```

Se o token não for enviado, a API retorna erro `401`.

---

## 6. Usuários de teste

O projeto possui usuários fixos apenas para fins didáticos.

### 6.1. Usuário administrador

```json
{
  "email": "admin@teste.com",
  "senha": "123456"
}
```

### 6.2. Usuário professor

```json
{
  "email": "professor@teste.com",
  "senha": "123456"
}
```

---

## 7. Instalação local

### 7.1. Clonar o repositório

```bash
git clone URL_DO_REPOSITORIO
cd api-notas-flask
```

---

### 7.2. Criar ambiente virtual

No Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

No Linux, macOS ou WSL:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 7.3. Instalar dependências

```bash
pip install -r requirements.txt
```

---

### 7.4. Executar localmente

```bash
python app.py
```

A API ficará disponível em:

```text
http://127.0.0.1:5000
```

---

## 8. Dependências

O arquivo `requirements.txt` deve conter:

```txt
Flask
PyJWT
gunicorn
```

---

## 9. Rota inicial

### 9.1. Requisição

```text
GET /
```

### 9.2. Resposta esperada

```json
{
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
  }
}
```

---

## 10. Login

### 10.1. Requisição

```text
POST /login
```

### 10.2. Body

```json
{
  "email": "admin@teste.com",
  "senha": "123456"
}
```

### 10.3. Resposta esperada

```json
{
  "mensagem": "Login realizado com sucesso",
  "token": "TOKEN_GERADO_AQUI",
  "tipo": "Bearer",
  "expira_em": "2 horas",
  "usuario": {
    "id": 1,
    "nome": "Administrador",
    "email": "admin@teste.com",
    "perfil": "admin"
  }
}
```

---

## 11. Como enviar o token JWT

Nas rotas protegidas, envie o token no cabeçalho da requisição.

### Header

```text
Authorization: Bearer TOKEN_GERADO_AQUI
```

No Thunder Client ou Postman:

1. vá até a aba de headers;
2. crie um header chamado `Authorization`;
3. no valor, coloque `Bearer` seguido do token.

Exemplo:

```text
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6...
```

---

## 12. Endpoints de clientes

### 12.1. Listar clientes sem token

```text
GET /clientes
```

Retorna dados básicos.

### 12.2. Listar clientes com token

```text
GET /clientes
Authorization: Bearer TOKEN
```

Retorna dados completos.

### 12.3. Buscar cliente por ID

```text
GET /clientes/1
```

Com token:

```text
GET /clientes/1
Authorization: Bearer TOKEN
```

### 12.4. Criar cliente

Exige token.

```text
POST /clientes
```

Header:

```text
Authorization: Bearer TOKEN
```

Body:

```json
{
  "nome": "Carlos Pereira",
  "email": "carlos@email.com",
  "telefone": "1598888-7777",
  "documento": "111.222.333-44"
}
```

### 12.5. Atualizar cliente

Exige token.

```text
PUT /clientes/1
```

Header:

```text
Authorization: Bearer TOKEN
```

Body:

```json
{
  "nome": "Carlos Pereira Atualizado",
  "email": "carlos.novo@email.com",
  "telefone": "1597777-6666",
  "documento": "111.222.333-44"
}
```

### 12.6. Remover cliente

Exige token.

```text
DELETE /clientes/1
```

Header:

```text
Authorization: Bearer TOKEN
```

Observação: se o cliente possuir notas fiscais vinculadas, a API não permitirá a remoção.

---

## 13. Endpoints de produtos

### 13.1. Listar produtos sem token

```text
GET /produtos
```

Retorna dados básicos:

```json
[
  {
    "id": 1,
    "nome": "Mouse",
    "preco": 49.9
  }
]
```

### 13.2. Listar produtos com token

```text
GET /produtos
Authorization: Bearer TOKEN
```

Retorna dados completos:

```json
[
  {
    "id": 1,
    "nome": "Mouse",
    "preco": 49.9,
    "descricao": "Mouse USB simples",
    "estoque": 30,
    "codigo_interno": "PROD-MOUSE-001"
  }
]
```

### 13.3. Buscar produto por ID

```text
GET /produtos/1
```

### 13.4. Criar produto

Exige token.

```text
POST /produtos
```

Header:

```text
Authorization: Bearer TOKEN
```

Body:

```json
{
  "nome": "Webcam",
  "descricao": "Webcam Full HD",
  "preco": 199.90,
  "estoque": 12,
  "codigo_interno": "PROD-WEBCAM-005"
}
```

### 13.5. Atualizar produto

Exige token.

```text
PUT /produtos/1
```

Header:

```text
Authorization: Bearer TOKEN
```

Body:

```json
{
  "nome": "Mouse Gamer",
  "descricao": "Mouse gamer com iluminação RGB",
  "preco": 129.90,
  "estoque": 15,
  "codigo_interno": "PROD-MOUSE-001"
}
```

### 13.6. Remover produto

Exige token.

```text
DELETE /produtos/1
```

Header:

```text
Authorization: Bearer TOKEN
```

Observação: se o produto estiver vinculado a uma nota fiscal, a API não permitirá a remoção.

---

## 14. Endpoints de notas fiscais

### 14.1. Listar notas fiscais sem token

```text
GET /notas
```

Retorna informações básicas:

```json
[
  {
    "id": 1,
    "data_emissao": "2026-05-13 20:30:00",
    "cliente": {
      "id": 1,
      "nome": "Maria Silva"
    },
    "valor_total": 189.7
  }
]
```

### 14.2. Listar notas fiscais com token

```text
GET /notas
Authorization: Bearer TOKEN
```

Retorna informações completas, incluindo cliente completo e itens da nota.

### 14.3. Buscar nota fiscal por ID

```text
GET /notas/1
```

Com token:

```text
GET /notas/1
Authorization: Bearer TOKEN
```

### 14.4. Criar nota fiscal

Exige token.

```text
POST /notas
```

Header:

```text
Authorization: Bearer TOKEN
```

Body:

```json
{
  "cliente_id": 1,
  "observacao": "Venda realizada em aula prática",
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
}
```

A API busca automaticamente o preço atual do produto e grava esse valor no item da nota.

Isso é importante porque o preço do produto pode mudar futuramente, mas a nota fiscal precisa manter o preço do momento da venda.

### 14.5. Atualizar nota fiscal

Exige token.

```text
PUT /notas/1
```

Header:

```text
Authorization: Bearer TOKEN
```

Body:

```json
{
  "cliente_id": 2,
  "observacao": "Nota fiscal atualizada",
  "itens": [
    {
      "produto_id": 2,
      "quantidade": 1
    },
    {
      "produto_id": 4,
      "quantidade": 1
    }
  ]
}
```

Na atualização da nota, a API remove os itens anteriores e insere os novos itens enviados.

Essa estratégia foi escolhida para manter o código mais simples e didático.

### 14.6. Remover nota fiscal

Exige token.

```text
DELETE /notas/1
```

Header:

```text
Authorization: Bearer TOKEN
```

Ao remover uma nota fiscal, seus itens também são removidos automaticamente por causa da configuração `ON DELETE CASCADE`.

---

## 15. Testes sugeridos no Thunder Client ou Postman

### 15.1. Testar API no ar

```text
GET /
```

### 15.2. Listar clientes sem token

```text
GET /clientes
```

A resposta deve mostrar poucos dados.

### 15.3. Fazer login

```text
POST /login
```

Body:

```json
{
  "email": "admin@teste.com",
  "senha": "123456"
}
```

Copie o token retornado.

### 15.4. Listar clientes com token

```text
GET /clientes
```

Header:

```text
Authorization: Bearer TOKEN
```

Agora a resposta deve mostrar mais dados.

### 15.5. Tentar criar produto sem token

```text
POST /produtos
```

Body:

```json
{
  "nome": "Webcam",
  "descricao": "Webcam Full HD",
  "preco": 199.90,
  "estoque": 12,
  "codigo_interno": "PROD-WEBCAM-005"
}
```

A API deve retornar erro `401`.

### 15.6. Criar produto com token

Repita a requisição anterior, mas agora envie o header:

```text
Authorization: Bearer TOKEN
```

A API deve criar o produto.

### 15.7. Criar nota fiscal

```text
POST /notas
```

Header:

```text
Authorization: Bearer TOKEN
```

Body:

```json
{
  "cliente_id": 1,
  "observacao": "Venda realizada durante a aula",
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
}
```

---

## 16. Deploy no Render

### 16.1. Subir o projeto no GitHub

Crie um repositório no GitHub e envie os arquivos do projeto.

### 16.2. Criar serviço no Render

No Render:

1. clique em `New`;
2. selecione `Web Service`;
3. conecte o repositório do GitHub;
4. selecione o projeto;
5. configure o serviço.

### 16.3. Configurações principais

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
gunicorn app:app
```

### 16.4. Variável de ambiente JWT

No Render, acesse a área de Environment Variables e crie:

```text
JWT_SECRET_KEY=minha-chave-super-secreta-para-aula
```

Essa variável será usada para assinar e validar os tokens JWT.

---

## 17. Sobre o comando `gunicorn app:app`

O comando:

```bash
gunicorn app:app
```

significa:

```text
gunicorn arquivo:variavel
```

No projeto:

- `app.py` é o arquivo;
- `app = Flask(__name__)` é a variável da aplicação Flask.

Portanto:

```text
app:app
```

significa:

```text
arquivo app.py : variável app
```

---

## 18. Observação sobre SQLite no Render

Este projeto usa SQLite por simplicidade didática.

No plano gratuito do Render, o arquivo SQLite pode não ser persistente. Isso significa que os dados podem ser perdidos em situações como:

- novo deploy;
- reinício do serviço;
- recriação do ambiente;
- inatividade do serviço gratuito.

Para uma aplicação real, o ideal seria usar um banco externo persistente, como PostgreSQL.

Para esta aula, o SQLite é suficiente porque o foco está em:

- API REST;
- rotas;
- autenticação;
- deploy;
- testes com Postman ou Thunder Client.

---

## 19. Ordem sugerida para a aula

1. Mostrar a estrutura do projeto.
2. Explicar o `app.py`.
3. Explicar o `database.py`.
4. Mostrar as tabelas criadas.
5. Explicar `clientes`, `produtos`, `notas_fiscais` e `itens_nota_fiscal`.
6. Rodar a API localmente.
7. Testar `GET /` sem token.
8. Testar `GET /clientes` sem token.
9. Fazer login em `POST /login`.
10. Copiar o token JWT.
11. Testar `GET /clientes` com token.
12. Comparar resposta pública e resposta autenticada.
13. Tentar `POST /produtos` sem token.
14. Fazer `POST /produtos` com token.
15. Criar uma nota fiscal com vários itens.
16. Explicar o relacionamento entre nota fiscal e produtos.
17. Subir o projeto no GitHub.
18. Fazer deploy no Render.
19. Configurar `JWT_SECRET_KEY` no Render.
20. Testar a API online pelo Thunder Client ou Postman.

---

## 20. Conceitos abordados

Este projeto permite trabalhar os seguintes conceitos:

- API REST;
- métodos HTTP;
- JSON;
- SQLite;
- relacionamento entre tabelas;
- chave primária;
- chave estrangeira;
- tabela auxiliar;
- autenticação com JWT;
- rotas públicas;
- rotas protegidas;
- variável de ambiente;
- deploy no Render;
- uso de Gunicorn;
- testes com Postman ou Thunder Client.

---

## 21. Aviso didático

Este projeto foi feito para fins educacionais.

Ele evita bibliotecas e estruturas mais avançadas, como:

- SQLAlchemy;
- Flask-JWT-Extended;
- Flask-Migrate;
- Marshmallow;
- Pydantic;
- arquitetura em camadas complexa.

A ideia é manter o código simples o suficiente para que os alunos consigam enxergar claramente:

- onde a rota começa;
- onde o banco é acessado;
- onde o token é validado;
- onde os dados são inseridos;
- onde os relacionamentos aparecem.

Em projetos profissionais, várias melhorias seriam recomendadas, como:

- senhas com hash;
- usuários salvos no banco;
- refresh token;
- validação mais robusta de dados;
- migrations;
- logs;
- testes automatizados;
- banco persistente externo;
- separação mais forte entre controllers, services e repositories.
