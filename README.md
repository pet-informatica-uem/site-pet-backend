# petBack API
## TO-DO

## Instalando

Você precisa ter [poetry](https://python-poetry.org) instalado.

Abra um terminal na pasta-raiz do projeto e digite o comando:

```sh
    poetry install
```

## Executando

Após instalar, abra um terminal na pasta-raiz do projeto e digite o comando:

```sh
    poetry run uvicorn main:petBack --reload
```
O servidor poderá ser acessado em http://localhost:8000/

## Executar testes
Abra um terminal na pasta-raiz do projeto e digite o comando
```sh
 poetry run pytest teste/usuario.py
 ```

## Documentação

Execute o comando acima e navegue para http://localhost:8000/docs

## Arquitetura & Estrutura de Arquivos

### App

Funcionalidade geral da API.
- **controllers**: Controladores para entidades do domínio
- **models**: Modelos para tabelas do banco de dados
- **schemas**: Classes pydantic para validação de dados

### API

Interface da API para o cliente.

### Core

Funcionalidades básicas, como acesso ao banco de dados e segurança.
