# Middlewares do site do PET

O *back-end* do site do PET utiliza o **FastAPI**, que é um *framework* para o desenvolvimento de APIs Web em Python.
O FastAPI adiciona vários recursos úteis à construção de APIs em cima de um outro framework, o **Starlette**.

Embora pareça complexo, todo o funcionamento do Starlette pode ser explicado através de,
e está organizado em, uma arquitetura em camadas:

1. Primeiro, o API recebe uma solicitação HTTP bruta do usuário, em texto plano.
1. A solicitação vai passando por uma série de camadas, começando da mais externa até
    chegar à mais interna.
    Cada vez que ela passa por uma camada, ela é transformada para uma representação
    mais rica em detalhes e informações.
1. Quando a solicitação chega à camada mais interna, ela está completa e possui todos os
    dados necessários para o seu processamento e geração de uma resposta.
1. Uma resposta é gerada na camada mais interna, e ela começa a fazer o caminho de volta
    através das camadas.
1. Para cada camada que ela passa, começando da mais interna até a mais externa, a
    resposta vai sendo modificada, agregando informações úteis ao usuário da resposta
    final.
1. Quando a resposta chega ao nível mais externo, ela está totalmente convertida para um
    formato textual apropriado e é devolvida para o usuário.

A figura 1 abaixo ilustra essa conversão.
Note que toda vez que a solicitação muda de camada, ocorre uma transformação.

```
   ┌───────────┐                ┌──────────┐   
   │Solicitação│                │ Resposta │   
   │   HTTP    │                │   HTTP   │   
   └─────┬─────┘                └────▲─────┘   
         │                           │         
┌────────O───────────────────────────X────────┐
│        │       Middleware 1        │        │
│┌───────O───────────────────────────X───────┐│
││       │           ...             │       ││
││┌──────O───────────────────────────X──────┐││
│││      │      Middleware N-1       │      │││
│││┌─────O───────────────────────────X─────┐│││
││││     │       Middleware N        │     ││││
││││     │        ┌────────┐         │     ││││
││││ O───▼─────O  │        │  X──────┴───X ││││
││││ │ objeto  ┼──► ROUTER ┼──► objeto   │ ││││
││││ │ Request │  │        │  │ Response │ ││││
││││ O─────────O  │        │  X──────────X ││││
││││              └────────┘               ││││
│││└───────────────────────────────────────┘│││
││└─────────────────────────────────────────┘││
│└───────────────────────────────────────────┘│
└─────────────────────────────────────────────┘

  Fig. 1 - Conversões realizadas nas camadas.
```

Essas "camadas" são, em essência, os *middlewares*. Existem *frameworks* como o express.js
onde **tudo** são *middlewares*, e cabe a você implementar até as coisas mais básicas.
Note que, no diagrama, até os Routers poderiam ser considerados *middlewares*.

O poder do *FastAPI* é que ele combina os *middlewares* básicos do Starlette junto com
os seus, como os que fazem a validação dos dados com o Pydantic ou os roteadores (também
*middlewares*).

Um *middleware* pode fazer o seguinte:

- Modificar uma solicitação vindo de uma camada superior;
- Interromper/bloquear uma solicitação segundo algum critério e retornar uma resposta;
- Passar a solicitação, original ou modificada, para a próxima camada;
- Alterar uma resposta vindo de uma camada inferior;
- Descartar uma resposta vindo de uma camada inferior e gerar uma nova;
- Capturar exceções lançadas pelo Python e convertê-los em uma resposta;
- ...

## Como eu faço o meu *middleware*?

Existem dois principais modos de se definir um *middleware*, e o site utiliza os dois 
padrões.

### 1. BaseHTTPMiddleware

O BaseHTTPMiddleware é uma classe fornecida pelo Starlette, e é o mais simples de usar,
embora não possa fazer tudo que o *middleware* ASGI pode.
Para declarar-se um novo *middleware*, pode-se fazer uma subclasse de *BaseHTTPMiddleware*.

Um exemplo é o seguinte:

```python
class MeuMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, meuParametro):
        super().__init__(app)
        self.meuParametro = meuParametro

    async def dispatch(self, request: Request, call_next):
        # Modifica o request como desejar...
        response = await call_next(request)
        # Modifica a response como desejar...
        return response
```

O construtor deve chamar o construtor da superclasse, passando o argumento `app`.
O *middleware* pode possuir campos adicionais, como é o exemplo do campo `meuParametro`.
É importante que a instância da classe em si não possua estado adicional.

A função principal é a função assíncrona *dispatch*.
Essa função é chamada quando a camada recebe uma solicitação vinda de uma camada
superior.
A solicitação é passada como parâmetro, junto com uma função *call_next* que deve
ser chamada com a solicitação, no caso em que o *middleware* decida que a solicitação
deve continuar descendo nas camadas.

A função *call_next* vai passando a solicitação através das camadas e por fim retorna
a resposta gerada pelo *middleware* inferior a este. Esta resposta pode ser modificada
e deve ser retornada ao fim da função.

Para instanciar esse middleware, faz-se assim:

```python
app = FastAPI()

app.add_middleware(MeuMiddleware, meuParametro="oi")
# outros middlewares...

# rotas e Routers...
```

### 2. Aplicação ASGI

O ASGI (*Asynchronous Server Gateway Interface*) é uma especificação Python que permite
a intercomunicação entre aplicações e servidores Python de maneira modular, possibilitando
a composição e reutilização de componentes ASGI através de uma interface comum. Em resumo, 
é um acordo sobre como uma aplicação de rede em Python deve ser escrita, para que 
componentes de rede possam ser combinados entre si.

O Starlette é um *framework* com suporte ao ASGI e permite que aplicações ASGI sejam
adicionadas como *middlewares* na sua pilha.

O funcionamento de uma aplicação ASGI é bem semelhante a de um *middleware*: ela recebe
mensagens de uma aplicação mais externa, as processa, e as passa para uma aplicação 
mais interna; ela também recebe mensagens de aplicações mais internas, as processa, e as
passa para uma aplicação mais externa.

A especificação ASGI é bem mais liberal e nós conseguimos fazer mais coisas escrevendo-se
um *middleware* no padrão ASGI.

Um exemplo de um *middleware* escrito como aplicação ASGI é o seguinte:

```python
from starlette.types import ASGIApp, Message, Receive, Scope, Send

class TamanhoLimiteMiddleware:
    def __init__(self, app: ASGIApp, *, meuParametro) -> None:
        self.app = app
        self.meuParametro = meuParametro

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def meuReceive() -> Message:
            msg = await receive()
            # modifica a mensagem...
            return msg
        
        # dá pra modificar o send para alterar uma resposta.
        # vide documentação em:
        # https://asgi.readthedocs.io/en/latest/index.html

        await self.app(scope, meuReceive, send)
```

A diferença entre o BaseHTTPMiddleware e uma aplicação ASGI é que no BaseHTTPMiddleware
as mensagens e respostas são obtidas por parâmetros e retornos, enquanto numa aplicação
ASGI é necessário fazer um *wrapper* nas funções *receive* e *send*, que recebem e enviam
objetos chamados **eventos** para as camadas superiores e inferiores.

Para instanciar esse *middleware*, o processo é o mesmo:

```python
app = FastAPI()

app.add_middleware(MeuMiddleware, meuParametro="oi")
# outros middlewares...

# rotas e Routers...
```

*Middlewares* dos dois tipos podem ser combinados numa mesma aplicação FastAPI.

**Observação:** caso uma execeção precise ser gerada em uma classe ASGI, é importante
que a exceção gerada seja subclasse de uma HTTPException, pois o FastAPI entende que
deve interromper o processamento da solicitação apenas quando captura uma HTTPException.

### Ordem de execução dos *middlewares*

A ordem em que os *middlewares* são inclusos na aplicação é a ordem na qual as 
solicitações vão passar por eles.

```python
app = FastAPI()

app.add_middleware(MiddlewareA)
app.add_middleware(MiddlewareB)
app.add_middleware(MiddlewareC)
app.add_middleware(MiddlewareD)

# rotas e Routers...
```

Neste exemplo, uma solicitação que chega ao sistema seria processada nesta ordem:

```
solicitação
     |
     v
MiddlewareA -> MiddlewareB -> MiddlewareC -> MiddlewareD
                                                  |
                                                  v
                                              [Routers]
                                                  |
                                                  v
MiddlewareA <- MiddlewareB <- MiddlewareC <- MiddlewareD
     |
     v
  resposta
```

Respectivamente, a solicitação passaria pelos *middlewares* A, B, C, D, é passada pelos
*routers*, e a resposta é retornada pelos *middlewares* na ordem D, C, B, A.

A ordem é importante se você está utilizando algo como um *middleware* que captura erros.
Esse *middleware* deve estar preferencialmente na camada mais externa, para que todas as
exceções geradas em camadas inferiores possam ser interceptadas por ele.

## *Middlewares* ativos no site do PET

O site do PET atualmente utiliza 5 middlewares, além dos incluídos automaticamente
pelo FastAPI:

1. **ExcecaoAPIMiddleware:** responsável por capturar exceções geradas pelo código e
    convertê-las em respostas de erro JSON.
2. **LoggerMiddleware:** registra todas as solicitações realizadas e seus detalhes em um
    *log*.
3. **TempoLimiteMiddleware:** estabelece um tempo limite para uma requisição. Se o tempo
   necessário para processar inteiramente uma solicitação (recebê-la do usuário, 
   processá-la e retorná-la) for maior que um intervalo pré-especificado, ela é
   abortada.
4. **TamanhoLimiteMiddleware:** estabelece um limite de tamanho em bytes para dados
   recebidos pelo usuário.
5. **CORSMiddleware:** adiciona *headers* CORS (*Cross-Origin Resource Sharing*) à
   resposta HTTP. Esta classe é fornecida pelo próprio FastAPI.

Mais detalhes podem ser consultados na documentação de cada uma dessas classes.