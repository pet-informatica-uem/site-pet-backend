import re


class ValidacaoCadastro:
    # https://pt.stackoverflow.com/questions/64608/como-validar-e-calcular-o-d%C3%ADgito-de-controle-de-um-cpf
    @staticmethod
    def cpf(cpf: str) -> bool:
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
        numbers = [int(digit) for digit in cpf if digit in "0123456789"]

        # Verifica se o CPF possui 11 numeros ou se todos sao iguais:
        if len(numbers) != 11 or len(set(numbers)) == 1:
            return False

        # Validacao do primeiro digito verificador:
        sum_of_products = sum(a * b for a, b in zip(numbers[0:9], range(10, 1, -1)))
        expected_digit = (sum_of_products * 10 % 11) % 10
        if numbers[9] != expected_digit:
            return False

        # Validacao do segundo digito verificador:
        sum_of_products = sum(a * b for a, b in zip(numbers[0:10], range(11, 1, -1)))
        expected_digit = (sum_of_products * 10 % 11) % 10
        if numbers[10] != expected_digit:
            return False

        return True

    # https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
    @staticmethod
    def email(email: str) -> bool:
        """
        Valida se um email estah na expressao regular correta.
        """

        # expressao regular do gmail:
        regex: re = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"

        # vendo se o gmail esta na expressao regular:
        return bool(re.fullmatch(regex, email))

    # https://pt.stackoverflow.com/questions/519132/como-fazer-valida%C3%A7%C3%A3o-de-senha-em-python
    @staticmethod
    def senha(senha: str) -> bool:
        """
        Para a senha ser aceita ela deve ter:
        -Ao menos 8 caracteres e ao máximo 64
        -Ao menos uma letra MAIUSCULA
        -Ao menos um numero
        -Ao menos um caractere especial(!@#$%¨&*)
        -confirmacao de senha identica a senha
        """

        if senha.islower():  # nao tem nenhum maiusculo:
            return False
        if not 7 < len(senha) < 65:  # nao tem 8 caracteres ou excede 64 caracteres
            return False
        if senha.isalpha():  # nao tem nenhum numero
            return False
        if senha.isalnum():  # nao tem caracteres especiais
            return False
        return True

print(ValidacaoCadastro.cpf('529.982.247-25'))