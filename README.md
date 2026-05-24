# bling-jwt-auth-python

[![PyPI](https://img.shields.io/pypi/v/bling-jwt-auth.svg)](https://pypi.org/project/bling-jwt-auth/)
[![Python](https://img.shields.io/pypi/pyversions/bling-jwt-auth.svg)](https://pypi.org/project/bling-jwt-auth/)
[![CI](https://github.com/tempont/bling-jwt-auth-python/actions/workflows/ci.yml/badge.svg)](https://github.com/tempont/bling-jwt-auth-python/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/github/license/tempont/bling-jwt-auth-python.svg)](LICENSE)
[![README English](https://img.shields.io/badge/README-English-blue)](docs/README.en.md)
[![GitHub](https://img.shields.io/badge/GitHub-tempont%2Fbling--jwt--auth--python-181717?logo=github)](https://github.com/tempont/bling-jwt-auth-python)

Biblioteca Python para autenticação OAuth 2.0 na **API v3 do Bling**, com suporte ao modo JWT exigido pelos endpoints atuais da plataforma.

Use este pacote quando sua aplicação precisa obter, persistir e renovar tokens do Bling sem reimplementar o fluxo OAuth. Ele cobre o caminho mais comum de integração:

- gerar a URL de autorização para o usuário conectar a conta Bling;
- trocar o `code` do callback por `access_token` e `refresh_token`;
- salvar o token localmente em SQLite ou JSON;
- renovar automaticamente o `access_token` antes da expiração;
- montar os headers necessários para chamadas autenticadas à API v3.
- fazer chamadas autenticadas com `connect()`, `BlingClient` ou `BlingAuth`
  sem montar manualmente cliente OAuth, store, manager e headers.

## Requisitos

- Python 3.14 ou superior
- Uma aplicação OAuth cadastrada no Bling
- `client_id`, `client_secret` e `redirect_uri` da aplicação OAuth

## Estrutura

```text
├── 📁 docs
│   └── 📝 README.en.md
├── 📁 examples
│   ├── 🐍 __init__.py
│   ├── 🐍 authenticated_request.py
│   ├── 🐍 client_request.py
│   ├── 🐍 httpx_auth_request.py
│   └── 🐍 oauth_flow.py
├── 📁 scripts
│   ├── 🐍 __init__.py
│   ├── 📄 check.sh
│   └── 🐍 package_version.py
├── 📁 src
│   └── 📁 bling_jwt_auth
│       ├── 📁 models
│       │   ├── 🐍 __init__.py
│       │   └── 🐍 token.py
│       ├── 📁 oauth
│       │   ├── 🐍 __init__.py
│       │   └── 🐍 client.py
│       ├── 📁 storage
│       │   ├── 🐍 __init__.py
│       │   ├── 🐍 base.py
│       │   ├── 🐍 factory.py
│       │   ├── 🐍 file.py
│       │   └── 🐍 sqlite.py
│       ├── 🐍 __init__.py
│       ├── 🐍 auth.py
│       ├── 🐍 client.py
│       ├── 🐍 config.py
│       ├── 🐍 constants.py
│       ├── 🐍 exceptions.py
│       ├── 🐍 headers.py
│       ├── 🐍 manager.py
│       └── 📄 py.typed
├── 📁 tests
│   ├── 🐍 __init__.py
│   ├── 🐍 conftest.py
│   ├── 🐍 test_auth.py
│   ├── 🐍 test_client.py
│   ├── 🐍 test_headers.py
│   ├── 🐍 test_oauth_client.py
│   ├── 🐍 test_storage_factory.py
│   ├── 🐍 test_storage_file.py
│   ├── 🐍 test_storage_sqlite.py
│   ├── 🐍 test_token_manager.py
│   └── 🐍 url_utils.py
├── ⚙️ .env.example
├── ⚙️ .gitignore
├── ⚙️ .pre-commit-config.yaml
├── 📄 LICENSE
├── 📄 Makefile
├── 📝 README.md
├── ⚙️ pyproject.toml
└── 📄 uv.lock
```

## Instalação

```bash
pip install bling-jwt-auth
```

Instalação direta do repositório:

```bash
pip install "git+https://github.com/tempont/bling-jwt-auth-python.git"
```

## Configuração

Copie o arquivo de exemplo e preencha as credenciais da sua aplicação no Bling:

```bash
cp .env.example .env
```

```env
BLING_CLIENT_ID=seu_client_id
BLING_CLIENT_SECRET=seu_client_secret
BLING_REDIRECT_URI=https://seu-dominio.com/oauth/callback
```

Por padrão, os tokens são salvos em SQLite em `~/.config/bling_jwt_auth/tokens.db`.

Para salvar em um arquivo JSON:

```env
BLING_TOKEN_STORE=file
BLING_TOKEN_STORE_PATH=./token.json
```

Para salvar SQLite em um caminho específico:

```env
BLING_TOKEN_STORE=sqlite
BLING_TOKEN_STORE_PATH=./bling-tokens.db
```

## Fluxo OAuth

### 1. Gere a URL de autorização

```python
from bling_jwt_auth import BlingAuthSettings, OAuthClient

settings = BlingAuthSettings.load()

with OAuthClient(settings) as oauth:
    url = oauth.build_authorization_url(state="valor-aleatorio-seguro")
    print(url)
```

Abra a URL no navegador, autorize a aplicação no Bling e capture o parâmetro `code` recebido no callback configurado em `BLING_REDIRECT_URI`.

### 2. Troque o code por tokens e persista

```python
from bling_jwt_auth import BlingAuthSettings, OAuthClient, TokenManager, create_token_store

settings = BlingAuthSettings.load()
store = create_token_store(settings)

with OAuthClient(settings) as oauth:
    manager = TokenManager(oauth, store, settings)
    manager.save_from_code("code-recebido-no-callback")
```

### 3. Faça chamadas autenticadas

```python
from bling_jwt_auth import connect

with connect() as bling:
    response = bling.get("/Api/v3/produtos")

response.raise_for_status()
print(response.json())
```

`connect()` carrega a configuração, abre o token store configurado, injeta os
headers `Authorization`/`enable-jwt` e renova o token automaticamente quando
necessário.

Para um estilo de SDK explícito:

```python
from bling_jwt_auth import BlingClient

with BlingClient.from_env() as bling:
    response = bling.get("/Api/v3/produtos")
```

Para usar seu próprio cliente HTTP:

```python
import httpx

from bling_jwt_auth import BlingAuth

with BlingAuth.from_env() as auth:
    with httpx.Client(auth=auth, base_url="https://api.bling.com.br") as client:
        response = client.get("/Api/v3/produtos")
```

## Exemplos executáveis

Fluxo manual de OAuth:

```bash
uv run python examples/oauth_flow.py
```

O script imprime a URL de autorização. Depois de autorizar no Bling, cole no terminal o `code` recebido no callback.

Para tentar abrir o navegador automaticamente:

```bash
uv run python examples/oauth_flow.py --open
```

Teste de chamada autenticada:

```bash
uv run python examples/authenticated_request.py
```

Esse exemplo usa o mesmo token salvo pelo fluxo OAuth, renova se necessário e chama o endpoint de homologação de produtos do Bling.

As variações da nova API também estão disponíveis:

```bash
uv run python examples/client_request.py
uv run python examples/httpx_auth_request.py
```

## API principal

| Objeto               | Uso                                                                                                           |
| -------------------- | ------------------------------------------------------------------------------------------------------------- |
| `connect`            | Cria um `BlingClient` autenticado usando `BLING_*` e o token store configurado.                               |
| `BlingClient`        | Cliente SDK-style para chamadas autenticadas com métodos `request`, `get`, `post`, `put`, `patch` e `delete`. |
| `BlingAuth`          | Adapter `httpx.Auth` que injeta headers e usa `TokenManager` para refresh automático.                         |
| `BlingAuthSettings`  | Carrega configuração a partir de variáveis `BLING_*` e `.env`.                                                |
| `OAuthClient`        | Cliente síncrono para autorização, troca de code, refresh e revogação.                                        |
| `TokenManager`       | Orquestra `OAuthClient` + `TokenStore` para salvar e renovar tokens.                                          |
| `create_token_store` | Cria o backend de armazenamento configurado (`sqlite` ou `file`).                                             |
| `SQLiteTokenStore`   | Persiste um token em banco SQLite local.                                                                      |
| `FileTokenStore`     | Persiste um token em arquivo JSON local.                                                                      |
| `bling_api_headers`  | Monta `Authorization: Bearer ...` e `enable-jwt: 1`.                                                          |

## Variáveis de ambiente

| Variável                     | Obrigatória | Padrão           | Descrição                                                  |
| ---------------------------- | ----------- | ---------------- | ---------------------------------------------------------- |
| `BLING_CLIENT_ID`            | Sim         | -                | Client ID da aplicação OAuth no Bling.                     |
| `BLING_CLIENT_SECRET`        | Sim         | -                | Client secret da aplicação OAuth.                          |
| `BLING_REDIRECT_URI`         | Sim         | -                | Callback cadastrado no Bling.                              |
| `BLING_ENABLE_JWT`           | Não         | `true`           | Envia o header `enable-jwt: 1` nos endpoints OAuth.        |
| `BLING_AUTHORIZE_URL`        | Não         | endpoint oficial | URL de autorização OAuth.                                  |
| `BLING_TOKEN_URL`            | Não         | endpoint oficial | URL de troca e refresh de token.                           |
| `BLING_REVOKE_URL`           | Não         | endpoint oficial | URL de revogação de token.                                 |
| `BLING_REFRESH_SKEW_SECONDS` | Não         | `60`             | Margem, em segundos, para renovar antes da expiração real. |
| `BLING_TOKEN_STORE`          | Não         | `sqlite`         | Backend de token: `sqlite` ou `file`.                      |
| `BLING_TOKEN_STORE_PATH`     | Não         | `~/.config/...`  | Caminho customizado para o banco ou JSON.                  |

## Tratamento de erros

- `TokenNotFoundError`: nenhum token foi salvo ainda. Execute o fluxo OAuth ou chame `TokenManager.save_from_code()`.
- `OAuthRequestError`: o Bling retornou erro HTTP em troca, refresh ou revogação. A exceção preserva `status_code` e `response_body`.
- `ValueError`: argumentos obrigatórios vazios, como `state`, `code` ou `refresh_token`.

## Segurança

- Não versione `.env`, `token.json` ou bancos SQLite com tokens.
- Use um `state` aleatório e valide-o no callback OAuth da sua aplicação.
- Configure `BLING_REDIRECT_URI` exatamente igual ao callback cadastrado no Bling.
- Em produção, prefira guardar credenciais em variáveis de ambiente ou secret manager.
- O backend JSON aplica permissão `0600` em sistemas POSIX depois da escrita.

## Desenvolvimento

Rodar lint, checagem de tipos e testes:

```bash
make check
```

Ou:

```bash
bash scripts/check.sh
```

Rodar apenas testes:

```bash
uv run --extra dev pytest
```

Gerar artefatos de distribuição local:

```bash
uv run --extra dev python -m build
uv run --extra dev python -m twine check dist/*
```

## Licença

MIT. Veja [LICENSE](LICENSE).
