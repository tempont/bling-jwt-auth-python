# bling-jwt-auth-python

Biblioteca Python simples para autenticar na **API v3 do Bling** usando OAuth 2.0 e tokens JWT.

Ela ajuda a:

- gerar a URL de autorizacao do Bling;
- trocar o `code` recebido por tokens;
- salvar os tokens em arquivo ou SQLite;
- renovar o access token automaticamente quando necessario;
- montar os headers corretos para chamar a API do Bling.

Versao em ingles: [docs/README.en.md](docs/README.en.md)

## Requisitos

- Python 3.14 ou superior
- Uma aplicacao OAuth cadastrada no Bling

## Instalacao

Instale pelo `pip`:

```bash
pip install bling-jwt-auth-python
```

Ou instale direto do GitHub:

```bash
pip install "git+https://github.com/mercanatu/bling-jwt-auth-python.git"
```

Para desenvolvimento local neste repositorio, use:

```bash
uv sync --extra dev
```

## Configuracao

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Edite o `.env` com os dados da sua aplicacao no Bling:

```env
BLING_CLIENT_ID=seu_client_id
BLING_CLIENT_SECRET=seu_client_secret
BLING_REDIRECT_URI=https://seu-dominio.com/oauth/callback
```

Por padrao, os tokens sao salvos em SQLite. Se quiser salvar em JSON:

```env
BLING_TOKEN_STORE=file
BLING_TOKEN_STORE_PATH=./token.json
```

## Como usar

### 1. Autorizar a conta Bling

Rode o exemplo de OAuth:

```bash
uv run python examples/oauth_flow.py
```

O script vai mostrar uma URL. Abra essa URL no navegador, autorize o acesso no Bling e cole no terminal o `code` recebido no callback.

Se quiser que o script tente abrir o navegador automaticamente:

```bash
uv run python examples/oauth_flow.py --open
```

### 2. Testar uma chamada autenticada

Depois de salvar o token, rode:

```bash
uv run python examples/authenticated_request.py
```

Esse exemplo usa o token salvo, renova se necessario e chama um endpoint de homologacao do Bling.

### 3. Usar no seu codigo

```python
import httpx
from bling_jwt_auth import (
    BlingAuthSettings,
    OAuthClient,
    TokenManager,
    bling_api_headers,
    create_token_store,
)

settings = BlingAuthSettings()
store = create_token_store(settings)

with OAuthClient(settings) as oauth:
    manager = TokenManager(oauth, store, settings)
    access_token = manager.get_access_token()

headers = bling_api_headers(access_token)

response = httpx.get(
    "https://api.bling.com.br/Api/v3/produtos",
    headers=headers,
)
response.raise_for_status()
print(response.json())
```

## Comandos uteis para desenvolvimento

Rodar lint, checagem de tipos e testes:

```bash
make check
```

Ou:

```bash
bash scripts/check.sh
```

Rodar apenas os testes:

```bash
uv run --extra dev pytest
```

## Licenca

MIT. Veja [LICENSE](LICENSE).
