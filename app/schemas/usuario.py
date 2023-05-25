# classe com os dados de cadastro do usuario
import pydantic
class Usuario:
    nome: str
    cpf: str
    email: str
    senha: str
    curso: str
    contaAtiva: bool
