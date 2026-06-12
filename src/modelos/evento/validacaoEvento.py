""""
    Funções relacionadas a validação de campos de evento
"""

import datetime


class ValidacaoEvento:
    """
    Contém métodos para a validação da criação de eventos.
    """

    @staticmethod
    def diasValidos(
        cls, dias: list[tuple[datetime, datetime]] | None
    ) -> list[tuple[datetime, datetime]] | None:
        """
        Verifica se as datas a serem atualizar de início e fim de cada dia do evento são válidas.
            :cls: EventoCriar -> referência à classe EventoCriar, na qual o método está sendo definido.
            :dias: list[tuple[datetime, datetime]] -> a data e a hora de início e fim de cada dia do evento.
        """
        if dias:
            for i, dia in enumerate(dias):
                if dia[0] > dia[1]:
                    raise ValueError(
                        f"A data de início do dia {i} deve ser anterior à data de fim do dia {i}."
                    )

        return dias
    
    def inscricoesValidas(self) -> Self:
        """
        Verifica se as datas a serem atualizadas das inscrições do evento são válidas.
            :self: EventoCriar -> referência à classe EventoCriar, na qual o método está sendo definido.
        """
        if (
            self.inicioInscricao
            and self.fimInscricao
            and self.inicioInscricao > self.fimInscricao
        ):
            raise ValueError(

                "A data de início das inscrições deve ser anterior à data de fim das inscrições."
            )

        return self
