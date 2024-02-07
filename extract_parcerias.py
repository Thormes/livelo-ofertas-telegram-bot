import json
import re
from datetime import datetime
from typing import Any, Optional
from Logger.logger import get_logger

import requests

from Model.Model import Empresa, Parceria
from Repository.EmpresaRepository import EmpresaRepository
from Repository.ParceriaRepository import ParceriaRepository

loger = get_logger("Parcerias", "parcerias.log")


def extract_parcerias():
    repository = EmpresaRepository()
    loger.info("Buscando Empresas")
    empresas = repository.getAll()
    loger.info(f"{len(empresas)} encontradas")
    codigos = []

    for empresa in empresas:
        if len(empresa.codigo) == 3: codigos.append(empresa.codigo)

    param = ",".join(sorted(codigos))
    loger.info("Solicitando parcerias atualizadas")
    response = requests.get("https://apis.pontoslivelo.com.br/partners-campaign/v1/campaigns/active",
                            {"partnersCodes": param})
    parcerias = json.loads(response.text)

    __cadastraParcerias(empresas, parcerias)


def __cadastraParcerias(empresas: list, parcerias: Any):
    if parcerias is None:
        raise ValueError("Json de parcerias não é um json válido")
    parceria_repository = ParceriaRepository()
    loger.info("Limpando registro de parcerias")
    parceria_repository.limpar()
    loger.info(f"Iniciando cadastro de {len(parcerias)} parcerias")
    for parceria in parcerias:
        if parceria['parityBau'] is None:
            continue
        codigo = parceria['partnerCode']
        empresa = __findEmpresa(empresas, codigo)
        newParceria = Parceria()
        newParceria.empresa = empresa
        newParceria.moeda = parceria["currency"]
        newParceria.pontos = int(parceria["parity"])
        newParceria.pontosClube = int(parceria["parityClub"])
        newParceria.pontosBase = int(parceria["parityBau"])
        newParceria.oferta = parceria["promotion"]
        newParceria.regras = parceria['legalTerms']
        newParceria.conectivo = parceria['separator']
        __getDatesFromLegalTerm(newParceria)
        parceria_repository.save(newParceria)


def __findEmpresa(empresas: list, codigo: str) -> Optional[Empresa]:
    for empresa in empresas:
        if empresa.codigo == codigo:
            return empresa
    return None


def __getDatesFromLegalTerm(parceria: Parceria):
    texto = parceria.regras
    padrao = r'(\d{1,2}(?:\/\d{1,2})?(?:\/\d{2,4})?) a (\d{1,2}/\d{1,2}/\d{2,4})'
    # padrão para capturar datas

    datas_encontradas = re.search(padrao, texto)

    if datas_encontradas:
        inicio = datas_encontradas.group(1)
        fim = datas_encontradas.group(2)
        str_fim = fim.split("/")
        if len(str_fim[2]) == 4:
            format = "%d/%m/%Y"
        elif len(str_fim[2]) == 2:
            format = "%d/%m/%y"
        else:
            raise ValueError("Data fim inválida: " + fim)

        data_fim = datetime.strptime(fim, format)
        dados_inicio = inicio.split("/")
        if len(dados_inicio) == 1:
            data_inicio = datetime.strptime(f"{inicio}/{data_fim.month}/{data_fim.year}", "%d/%m/%Y")
        elif len(dados_inicio) == 2:
            data_inicio = datetime.strptime(f"{dados_inicio[0]}/{dados_inicio[1]}/{data_fim.year}", "%d/%m/%Y")
        elif len(dados_inicio) == 3:
            if len(dados_inicio[2]) == 4:
                format = "%d/%m/%Y"
            elif len(dados_inicio[2]) == 2:
                format = "%d/%m/%y"
            data_inicio = datetime.strptime(inicio, format)
        else:
            raise ValueError("Não reconhecível data de início: " + inicio)

        parceria.inicio = data_inicio
        parceria.fim = data_fim


if __name__ == "__main__":
    extract_parcerias()
