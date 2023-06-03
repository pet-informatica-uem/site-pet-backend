from app.models.usuarioBD import UsuarioBD
from core import enviarEmail

class RecuperaConta:
    def __init__(self, email: str) -> None:
        self.email = email

    #Envia um email para trocar de senha se o email estiver cadastrado no bd
    def enviaEmail(self) -> str: 
        #Verificar se o usuário está no bd
        user = UsuarioBD(email=self.email)
        if (user.getIdUsuario() == "Usuário não encontrado"):
            return "OK"
        
        #Enviar o email
        #TODO Gerar URL único para a troca da senha
        enviarEmail()
        return "OK"

