# API Pisantes Store

Este projeto é um **trabalho acadêmico** desenvolvido para fins de aprendizado e representa o projeto da avaliação A3 de Sistemas distribuídos e mobile do primeiro semestre de 2026 da FASEH.

## Sobre o projeto

API REST para e-commerce de tênis, desenvolvida com Django e Django REST Framework. Oferece funcionalidades completas de autenticação, gerenciamento de produtos, carrinho de compras, checkout e relatórios de vendas.

---

## Tecnologias

- Python 3.11+
- Django 5.x
- Django REST Framework
- SQLite

---

## Pré-requisitos

- Python 3.11 ou superior instalado
- `pip` atualizado

---

## Como rodar o projeto

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd <nome-da-pasta>
```

### 2. Crie e ative o ambiente virtual

```bash
# Criar
python -m venv venv

# Ativar — Windows
venv\Scripts\activate

# Ativar — Linux/macOS
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Rode as migrations

```bash
python manage.py migrate
```

### 5. Crie um superusuário (administrador)

```bash
python manage.py createsuperuser
```

> Informe e-mail, nome, CPF e senha. Esse usuário terá acesso ao Django Admin e aos endpoints restritos a staff.

### 6. Inicie o servidor

```bash
python manage.py runserver
```

A API estará disponível em `http://127.0.0.1:8000/`.

---

## Autenticação

A API utiliza autenticação por **Token**. Após o login, inclua o token no header de todas as requisições autenticadas:

```
Authorization: Token <seu_token>
```

---

## Endpoints

### Autenticação

| Método | Endpoint              | Descrição                     | Autenticação |
| ------ | --------------------- | ----------------------------- | ------------ |
| `POST` | `/api/auth/registro/` | Cadastro de novo usuário      | Não          |
| `POST` | `/api/auth/login/`    | Login e obtenção do token     | Não          |
| `POST` | `/api/auth/logout/`   | Logout e invalidação do token | Sim          |
| `GET`  | `/api/auth/perfil/`   | Dados do usuário logado       | Sim          |

### Endereços

| Método      | Endpoint               | Descrição                  | Autenticação |
| ----------- | ---------------------- | -------------------------- | ------------ |
| `GET`       | `/api/enderecos/`      | Lista endereços do usuário | Sim          |
| `POST`      | `/api/enderecos/`      | Cadastra novo endereço     | Sim          |
| `GET`       | `/api/enderecos/{id}/` | Detalha um endereço        | Sim          |
| `PUT/PATCH` | `/api/enderecos/{id}/` | Atualiza um endereço       | Sim          |
| `DELETE`    | `/api/enderecos/{id}/` | Remove um endereço         | Sim          |

### Cartões de Crédito

| Método      | Endpoint             | Descrição                | Autenticação |
| ----------- | -------------------- | ------------------------ | ------------ |
| `GET`       | `/api/cartoes/`      | Lista cartões do usuário | Sim          |
| `POST`      | `/api/cartoes/`      | Cadastra novo cartão     | Sim          |
| `GET`       | `/api/cartoes/{id}/` | Detalha um cartão        | Sim          |
| `PUT/PATCH` | `/api/cartoes/{id}/` | Atualiza um cartão       | Sim          |
| `DELETE`    | `/api/cartoes/{id}/` | Remove um cartão         | Sim          |

> **Nota:** Apenas bandeira, últimos 4 dígitos e nome do titular são armazenados. Número completo e CVV nunca são salvos.

### Produtos

| Método      | Endpoint              | Descrição                      | Autenticação |
| ----------- | --------------------- | ------------------------------ | ------------ |
| `GET`       | `/api/produtos/`      | Lista todos os produtos        | Não          |
| `GET`       | `/api/produtos/{id}/` | Detalha um produto com estoque | Não          |
| `POST`      | `/api/produtos/`      | Cadastra novo produto          | Staff        |
| `PUT/PATCH` | `/api/produtos/{id}/` | Atualiza um produto            | Staff        |
| `DELETE`    | `/api/produtos/{id}/` | Remove um produto              | Staff        |

### Estoque

| Método      | Endpoint              | Descrição                      | Autenticação |
| ----------- | --------------------- | ------------------------------ | ------------ |
| `GET`       | `/api/estoques/`      | Lista todos os estoques        | Não          |
| `POST`      | `/api/estoques/`      | Cadastra estoque de um produto | Staff        |
| `PUT/PATCH` | `/api/estoques/{id}/` | Atualiza quantidade/tamanho    | Staff        |
| `DELETE`    | `/api/estoques/{id}/` | Remove um estoque              | Staff        |

### Carrinho

| Método   | Endpoint                    | Descrição                      | Autenticação |
| -------- | --------------------------- | ------------------------------ | ------------ |
| `GET`    | `/api/carrinho/`            | Exibe o carrinho do usuário    | Sim          |
| `GET`    | `/api/carrinho/itens/`      | Lista itens do carrinho        | Sim          |
| `POST`   | `/api/carrinho/itens/`      | Adiciona item ao carrinho      | Sim          |
| `PATCH`  | `/api/carrinho/itens/{id}/` | Atualiza quantidade de um item | Sim          |
| `DELETE` | `/api/carrinho/itens/{id}/` | Remove item do carrinho        | Sim          |

### Pedidos

| Método | Endpoint             | Descrição                    | Autenticação |
| ------ | -------------------- | ---------------------------- | ------------ |
| `GET`  | `/api/pedidos/`      | Lista pedidos do usuário     | Sim          |
| `POST` | `/api/pedidos/`      | Realiza checkout do carrinho | Sim          |
| `GET`  | `/api/pedidos/{id}/` | Detalha um pedido            | Sim          |

### Relatórios

| Método | Endpoint                  | Descrição                       | Autenticação |
| ------ | ------------------------- | ------------------------------- | ------------ |
| `GET`  | `/api/relatorios/vendas/` | Relatório de vendas por período | Staff        |

**Query params do relatório:**

```
/api/relatorios/vendas/?data_inicio=2026-06-01&data_fim=2026-06-30
```

---

## Fluxo de compra

1. **Cadastro/Login** — obter token
2. **Cadastrar endereço** — pelo menos um endereço de entrega
3. **Cadastrar cartão** — pelo menos um cartão de crédito
4. **Adicionar itens ao carrinho** — informar `estoque` (id) e `quantidade`
5. **Checkout** — `POST /api/pedidos/` com `endereco_id` e `cartao_id`
6. **Pedido criado** — carrinho é esvaziado e estoque é baixado automaticamente

### Exemplo de body para checkout

```json
{
  "endereco_id": 1,
  "cartao_id": 2
}
```

---

## Django Admin

O painel administrativo está disponível em `http://127.0.0.1:8000/admin/`.

Funcionalidades disponíveis:

- Gerenciar usuários, endereços e cartões
- Cadastrar e editar produtos com estoques inline
- Visualizar carrinhos e pedidos com seus itens

---

## Estrutura do projeto

```
├── app/
│   ├── models.py        # Modelos: Usuario, Endereco, CartaoCredito, Produto, Estoque, Carrinho, Pedido...
│   ├── serializers.py   # Serializers para cada endpoint
│   ├── views.py         # Views e ViewSets
│   ├── admin.py         # Configuração do Django Admin
│   └── urls.py          # Rotas da aplicação
├── core/
│   └── settings.py      # Configurações do projeto
├── manage.py
└── requirements.txt
```

---

## Observações

- O projeto não possui integração com gateway de pagamento. Pedidos são criados diretamente com `status='pago'` para fins ilustrativos.
- Cada usuário possui um único carrinho criado automaticamente no primeiro acesso.
- Cada usuário pode ter apenas um endereço e um cartão marcados como `principal`.

## Aviso

Este projeto é de caráter educacional e foi desenvolvido como um trabalho acadêmico para a entrega A3 da disciplina de Sistemas distribuídos e mobile do primeiro semestre de 2026 na FASEH. O mesmo não deve ser utilizado sem devidas adaptações e validações de segurança.

### Integrantes

- Carlos ([carlosmrd](https://github.com/carlosmrd))
- Lucas ([lucas-avv](https://github.com/lucas-avv))
