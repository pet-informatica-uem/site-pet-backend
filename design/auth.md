# Autenticação e Autorização no Site do PET

O site do PET possui rotas autenticadas e não-autenticadas. Este documento detalha como
a autenticação e autorização funcionam no site.

## O que é autenticação e autorização?

Existem dois conceitos de nomes semelhantes em segurança da informação mas que possuem significados diferentes:

1. **Autenticação** *(Authentication, AuthN)* - verificar se alguém é quem realmente diz ser. Existem três principais modos de realizar isso:

    1. Algo que você sabe (uma senha ou frase secreta; um segredo)
    2. Algo que você tenha (uma chave física; um dispositivo celular; uma *passkey*)
    3. Algo que você é (uma digital; um rosto; uma íris; uma fala)

    Alguns sistemas de autenticação que requerem mais segurança implementam dois ou mais desses fatores, numa técnica chamada de Autenticação Multifator (MFA).
    A autenticação em dois fatores (2FA) é assim chamada pois geralmente implementa dois desses fatores (normalmente algo que você sabe e algo que você tenha).

    O site do PET implementa apenas o fator "algo que você sabe", e os segredos são: a senha da conta e os *tokens* JWT.

2. **Autorização** *(Authorization, AuthZ)* - dado que você sabe quem uma pessoa ou entidade é, determinar se ela tem permissão para realizar uma ação. Uma coisa é confirmar quem uma pessoa é; outra é ela ter permissão! **Não se deve assumir que toda pessoa autenticada (AuthN) é autorizada (AuthZ).**

    No site do PET, atualmente segregamos as rotas em três conjuntos:
  
    1. Rotas que podem ser utilizadas por todos, até usuários não autenticados;
    2. Rotas que podem ser utilizadas apenas por usuários autenticados;
    3. Rotas que podem ser utilizadas apenas por usuários *petianos* autenticados.

Um modo de memorizar essas diferenças é pensar que *autenticação* vem de **autêntico**, uma pessoa autêntica, verdadeira, e que *autorização* vem de **autorizado**, permitido

## Autenticação

### Autenticação de sessões

Um usuário tem a sua sessão autenticada através do fornecimento de uma combinação email-senha que esteja presente e armazenada no banco de dados.

As senhas são armazenadas *hashed* e *salted* no banco de dados, por boa prática de segurança. O texto simples da senha é irrecuperável mesmo para quem tem acesso ao banco de dados.

O fluxo de autenticação funciona da seguinte maneira:

1. O usuário realiza uma requisição ao endpoint `/usuarios/login` do site com o email e senha da sua conta.
2. A conta com aquele email no banco de dados é recuperada.
3. Caso a conta exista e esteja ativada, a senha fornecida pelo usuário passa pelo *hashing* e *salting* e o resultado é comparado com o que está armazenado no banco de dados.
4. Se os dois *hashes* batem, um *token* aleatório é gerado de maneira segura e armazenado no banco de dados, associado ao usuário.
5. O *token* de acesso gerado é retornado ao usuário.

Caso alguma das etapas não tenha sucesso, a autenticação falha.

A partir daí, o usuário deve fornecer o *token* gerado em todas as suas futuras requisições à API, por meio do cabeçalho *Authorization* do HTTP, da seguinte forma:

```http
GET /usuarios/eu HTTP/1.1
...
Authorization: Bearer <token>
...
```

O modo como a conta associada a esse token pode ser recuperada pelos desenvolvedores da API é pelo objeto `tokenAcesso` no arquivo `usuarioRotas.py`.
Este objeto pode ser especificado como dependência de uma rota e passado como parâmetro, e o FastAPI automaticamente preencherá o argumento com o valor do cabeçalho.

Existem duas funções auxiliares no mesmo arquivo que facilitam a autenticação/autorização dos usuários no arquivo. A primeira é `getUsuarioAutenticado`, que obtém o usuário a partir de `tokenAcesso`. Além disso, a função também aborta a solicitação e retorna um erro 401 (Não autorizado) caso o usuário não esteja autenticado. A segunda é `getPetianoAutenticado`, que realiza a mesma função mas também verifica se o usuário é do tipo petiano antes de retornar, gerando um erro 401 caso contrário.

As duas funções podem ser especificadas como dependências. O FastAPI automaticamente irá chamá-las e povoar os parâmetros nessas situações.

Os *tokens* armazenados no banco de dados possuem uma data de validade.

Esse é o padrão definido no esquema de autorização *OAuth2*, o qual é implementado em partes pelo site.



### Autenticação via JWT

O outro processo de autenticação é via JWTs (*JSON Web Tokens*). Um JWT é uma sequência objetos JSON codificados em Base64url, de modo que eles podem ser passados em URLs de modo seguro.

JWTs são *assinados* pelo servidor utilizando uma chave secreta, especificada na variável de ambiente `PET_API_SEGREDO_JWT`, que \*absloutamente\* **nunca deve ser revelada a ninguém, assim como qualquer outra senha do PET-Informática**. Um JWT assinado não pode ser modificado sem que ele seja invalidado. A assinatura previne modificações não autorizadas.

Utilizamos JWTs em dois fluxos de autenticação:

- Na ativação de contas/confirmação de emails;
- Durante a troca de senhas.

Os JWTs são gerados com a biblioteca Python `jose`. Nós usamos JWTs nesses casos pois eles possuem um prazo de validade pré-especificado e podem ser embutidos em URLs sem grandes problemas.

## Autorização

Conforme dito anteriormente, dividimos as rotas em três níveis de autorização: usuários não autenticados, usuários autenticados e petianos autenticados.

O modo como verificamos a permissão dos usuários é por meio das funções `getUsuarioAutenticado` e `getPetianoAutenticado` do arquivo `usuarioRotas.py`. Um exemplo de uso dessas funções pode ser visto abaixo:

```python
@roteador.put(
    "/{id}/foto",
    name="Atualizar foto de perfil",
    description="O usuário petiano é capaz de editar sua foto de perfil",
)
def editarFoto(
    id: str,
    foto: UploadFile,
    usuario: Annotated[Usuario, Depends(getPetianoAutenticado)] = ...,
) -> None:
    if usuario.id == id:
        UsuarioControlador.editarFoto(usuario=usuario, foto=foto)
```

A anotação `Depends` faz com que o FastAPI automaticamente chame essas funções quando a rota é chamada e o parâmetro é populado com uma instância do objeto.

## Aparte: *hashing* e *salting*?

Uma prática comum de segurança é **nunca** armazenar as senhas textualmente ("texto simples") no banco de dados. Se não fizermos isso:

1) Qualquer um com acesso ao banco de dados descobriria a senha dos usuários e poderia acessar as suas contas, e bancos de dados são exfiltrados cotidianamente (até mesmo por membros internos à organização).
2) Como as pessoas reutilizam senhas (isto é fato), um vazamento de banco de dados de um site com senhas em texto simples pode compromoter as contas dos usuários em outros sites.

No lugar de texto simples, armazenamos **hashes**: uma *função hash* mapeia dados digitais para *strings* de tamanho fixo. A *string* (*hash*) é como uma impressão digital dos dados: apenas[^1] os dados originais são capazes de gerar aquela *string*.

Na prática, a transformação é unidrecional e portanto é impossível obter os dados originais a partir do *hash*. O melhor jeito de descobrir os dados originais é testando todos os dados possíveis até que o *hash* desejado seja encontrado.

Por exemplo, a palavra `hello` em ASCII tem um *hash* MD5 `5d41402abc4b2a76b9719d911017c592`. Se observarmos uma mensagem com o mesmo *hash*, é bem provável que a mensagem seja `hello`.[^1] Assim, ao invés de armazenarmos e compararmos senhas no banco de dados, armazenamos apenas os seus *hashes*.

Todavia, apenas *hashing* não basta: um atacante poderia gerar uma tabela com *hashes* para as senhas mais comuns e comparar essa tabela com o banco de dados para obter as senhas originais. Além disso, se o atacante visse o mesmo *hash* em duas aplicações diferentes, ele poderia inferir que o usuário colocou a mesma senha nos dois.

Para resolver este problema, usamos um **salt**: uma *string* aleatória que é armazenada junto com o *hash* da senha. Quando computamos o *hash* da senha, adicionamos o *salt* antes de passá-la para a função *hash*. Deste modo, cada senha em um banco de dados precisaria de uma tabela diferente, o que é impraticável.

É importante usar funções *hash* criptograficamente seguras, que sejam resistentes a ataques criptoanalíticos (que levam tempo para computar e possuam boas propriedades estatísticas) e que sejam projetadas especificamente para senhas.

- Exemplos: Argon2id, scrypt, bcrypt, PBKDF2
- Anti-exemplos: MD5, SHA-1, cifra de César

[^1]: Pode acontecer de duas mensagens diferentes terem o mesmo *hash*, pois o *hash* tem tamanho fixo e a função pode receber uma quantidade infinita de dados; como há muito mais sequências de dados possíveis do que hashes, necessariamente haverá repetições ("colisões"). Na prática, essas colisões são extremamente raras (existem $2^{256}$ hashes SHA256 diferentes, o que é... bastante)


## Referências

[1] Authorization Cheat Sheet - OWASP. Disponível em: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html.

[2] Authentication Cheat Sheet - OWASP. Disponível em: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html

[3] OAuth2. Disponível em https://oauth.net/2/.

[4] JSON Web Tokens - jwt.io. Disponível em https://jwt.io/.