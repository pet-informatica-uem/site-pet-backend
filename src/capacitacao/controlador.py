import os
import csv
from datetime import datetime


class CapacitacaoControlador:
    @staticmethod
    def registrar_presenca(codigo):
        # Criar pasta "data" se não existir
        pasta = "src/capacitacao/data"
        if not os.path.exists(pasta):
            os.makedirs(pasta)

        # Criar nome do arquivo baseado na data atual
        data_atual = datetime.now().strftime("%Y-%m-%d")
        caminho_arquivo = os.path.join(pasta, f"presenca-{data_atual}.csv")

        # Verificar se o arquivo já existe
        arquivo_existe = os.path.exists(caminho_arquivo)

        # Escrever no arquivo CSV
        with open(caminho_arquivo, mode="a", newline="") as arquivo:
            escritor = csv.writer(arquivo)

            # Se o arquivo não existia, escrever o cabeçalho
            if not arquivo_existe:
                escritor.writerow(["Codigo", "Timestamp"])

            # Adicionar linha com código e timestamp atual
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            escritor.writerow([codigo, timestamp])

        return "Ok"
