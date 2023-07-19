import re


class ValidacaoCadastro():
# https://pt.stackoverflow.com/questions/64608/como-validar-e-calcular-o-d%C3%ADgito-de-controle-de-um-cpf
    def cpf(self, cpf: str) -> bool:
        """
        Efetua a validacao do CPF, nao valida a formatacao!!!!!!.

        Parametros:
            cpf (str): CPF a ser validado

        Retorno:
            bool:
                - Falso, quando o CPF nao possuir 11 caracteres numericos;
                - Falso, quando os digitos verificadores forem invalidos;
                - Verdadeiro, caso contrario.

        Exemplos:

        validate('529.982.247-25')
        True
        validate('52998224725')
        True
        """

        # Obtem apenas os numeros do CPF, ignorando pontuacoes
        cpf :str = re.sub(r"\D", "", cpf)

        # Verifica se o CPF possui 11 numeros ou se todos sao iguais:
        if len(cpf) != 11 or len(set(cpf)) == 1:
            return False

        # Validacao do primeiro digito verificador:
        somaDosProdutos :int = sum(int(a) * int(b) for a, b in zip(cpf[0:9], range(10, 1, -1)))
        digitoEsperado :int = (somaDosProdutos * 10 % 11) % 10
        if cpf[9] != digitoEsperado:
            return False

        # Validacao do segundo digito verificador:
        somaDosProdutos :int = sum(a * b for a, b in zip(cpf[0:10], range(11, 1, -1)))
        digitoEsperado :int = (somaDosProdutos * 10 % 11) % 10
        if cpf[10] != digitoEsperado:
            return False

        return True


    # https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
    def email(self, email: str) -> bool:
        """
        Valida se um email estah na expressao regular correta.
        """

        # expressao regular do gmail:
        regex :re = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"

        # vendo se o gmail esta na expressao regular:
        return bool(re.fullmatch(regex, email))


    # https://pt.stackoverflow.com/questions/519132/como-fazer-valida%C3%A7%C3%A3o-de-senha-em-python
    def senha(self, senha1: str, senha2: str) -> bool:
        """
        Para a senha ser aceita ela deve ter:
        -Ao menos 8 caracteres e ao máximo 64
        -Ao menos uma letra MAIUSCULA
        -Ao menos um numero
        -Ao menos um caractere especial(!@#$%¨&*)
        -confirmacao de senha identica a senha
        """

        if senha1.islower():  # nao tem nenhum maiusculo:
            return False
        if not 7 < len(senha1) < 65:  # nao tem 8 caracteres ou excede 64 caracteres
            return False
        if senha1.isalpha():  # nao tem nenhum numero
            return False
        if senha1.isalnum():  # nao tem caracteres especiais
            return False
        if not senha1 == senha2:
            return False
        return True
