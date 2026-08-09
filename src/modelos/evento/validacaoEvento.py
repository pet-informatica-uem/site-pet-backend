""""
    Funções relacionadas a validação de campos de evento
"""

from datetime import datetime


class ValidacaoEvento:
    """
    Contém métodos para a validação da criação de eventos.
    """

    @staticmethod
    def diasValidos(dias: list[tuple[datetime, datetime]] | None) -> bool:
        """
        Verifica se as datas de início e fim de cada dia do evento são válidas.
        Para que os dias sejam validados, é necessário que:
        - Em cada tupla, ambas as datas possuam o mesmo dia.
        - O horário de término da tupla seja posterior ao horário de início.
        - A lista de dias é ordenada de acordo com os dias e horários.

            :dias: list[tuple[datetime, datetime]] -> a data e a hora de início e fim de cada dia do evento.
        """
        if not dias:
            raise ValueError("Datas ausentes.")

        for i in range(len(dias)):
            inicio, fim = dias[i]
            
            # Tupla deve ter itens que correspondem ao mesmo dia
            if inicio.date() != fim.date():
                raise ValueError(f"O início e o fim do dia {i + 1} devem ocorrer na mesma data.")
            
            # O horário de término deve ser posterior ao de início
            if inicio >= fim:
                raise ValueError(f"No dia {i + 1}, o horário de término deve ser posterior ao horário de início.")
            
            # Ordem cronológica entre dias do evento
            if i > 0:
                fim_dia_anterior = dias[i - 1][1]
                if inicio <= fim_dia_anterior:
                    raise ValueError(f"O dia {i + 1} deve começar após o término do dia {i}.")

        return True

    @staticmethod
    def valorValido(valor: float) -> bool:
        """
        Verifica se um evento possui um valor de preço válido.
        Para o valor ser validado, é necessário que:
        - Seja não-negativo.
        - Seja menor que 1000.

            :valor: float -> o preço de inscrição para um evento.
        """
        return valor >= 0 and valor < 1000

    @staticmethod
    def inscricoesValidas(inicioInscricao: datetime | None, fimInscricao: datetime | None) -> bool:
        """
        Verifica se as datas a serem atualizadas das inscrições do evento são válidas.
            :inicioInscricao: datetime -> a data e a hora de início do período de inscrições de um evento.
            :fimInscricao: datetime -> a data e a hora de fim do período de inscrições de um evento.
        """
        if inicioInscricao and fimInscricao and inicioInscricao > fimInscricao:
            return False

        return True

    @staticmethod
    def inscricaoAntesDoEvento(
        fimInscricao: datetime | None, inicioEvento: datetime | None) -> bool:
        """
        Verifica se o período de inscrições encerra antes do início do evento.
            :fimInscricao: datetime -> a data e a hora de fim do período de inscrições de um evento.
            :inicioEvento: datetime -> a data e a hora de início do evento.
        """
        if fimInscricao and inicioEvento and fimInscricao >= inicioEvento:
            return False

        return True
