"""
Funções relacioandas a validação de cadastro de usuários.
"""

import re


class ValidacaoCadastro:
    """
    Contém métodos para validação de cadastro de usuários.
    """

    # https://pt.stackoverflow.com/questions/64608/como-validar-e-calcular-o-d%C3%ADgito-de-controle-de-um-cpf
    @staticmethod
    def cpf(cpf: str) -> bool:
        """
        Efetua a validação do CPF. A validação é executada apenas sobre os dígitos numéricos do CPF, ignorando-se
        os demais caracteres.

        :param cpf: CPF a ser validado
        :return valido: Falso, quando o CPF não possuir 11 caracteres numéricos; Falso, quando os dígitos verificadores forem inválidos; Verdadeiro, caso contrário.

        Exemplos:

        >>> ValidacaoCadastro.cpf('529.982.247-25')
        True
        >>> ValidacaoCadastro.cpf('52998224725')
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
        Valida se um email está na expressao regular correta.

        :param email: email a ser validado
        :return valido: Falso, quando o email não possuir o formato correto; Verdadeiro, caso contrário.
        """

        # expressao regular do gmail:
        regex: str = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"

        # vendo se o gmail esta na expressao regular:
        return bool(re.fullmatch(regex, email))

    # https://pt.stackoverflow.com/questions/519132/como-fazer-valida%C3%A7%C3%A3o-de-senha-em-python
    @staticmethod
    def senha(senha: str) -> bool:
        """
        Verifica se a senha é válida.

        Para a senha ser aceita ela deve ter:
        - Ao menos 8 caracteres e ao máximo 64
        - Ao menos uma letra MAIUSCULA
        - Ao menos um numero
        - Ao menos um caractere especial(!@#$%¨&*)
        - confirmacao de senha identica a senha

        :param senha: senha a ser validada
        :return valido: Verdadeiro apenas se todos os critérios forem atendidos; Falso, caso contrário.
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
