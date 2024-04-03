import json
import time

import requests

from Model.Model import Empresa, Categoria
from Repository.EmpresaRepository import EmpresaRepository
from Repository.CategoriaRepository import CategoriaRepository

from Logger.logger import get_logger

loger = get_logger("Empresas", "empresas.log")


def extractEmpresas():
    repository = EmpresaRepository()
    loger.info("Realizando requisição de lista de empresas")
    try:

        response = requests.get(
            "https://www.livelo.com.br/ccstore/v1/files/thirdparty/config_partners_compre_e_pontue.json")
        empresas = json.loads(response.text)
    except Exception as ex:
        loger.error("Não foi possível baixar empresas: " + str(ex))
        return

    if empresas is None:
        loger.error("Json de empresas não é um json válido: " + response.text)
        return

    parceiros = empresas['partners']
    loger.info(f"Encontrado um total de {len(parceiros)} empresas parceiras. Verificando parcerias ativas.")
    ativas = list(filter(lambda x: x['enableBenefits'] is True, parceiros))
    ativas = sorted(ativas, key=lambda x: x['name'].lower())
    loger.info(f"Encontrados {len(ativas)} parcerias ativas.")
    for emp in ativas:
        if 'XXX' in emp['id']: continue
        empresa = Empresa()
        empresa.nome = emp['name'].strip()
        empresa.codigo = emp['id'].strip()
        empresa.categorias = emp['categories']
        url = "https://www.livelo.com.br" + emp['partnerDetailsPage'] if str(emp['partnerDetailsPage']).startswith(
            "/") else emp['partnerDetailsPage']
        empresa.url = url
        repository.save(empresa)

    categoriaRepository = CategoriaRepository()
    loger.info("Realizando importação de categorias")
    categorias = empresas['categories']
    loger.info(f"Encontrado um total de {len(categorias)} categorias")
    for categoria in categorias:
        if categoria == 'e' or categoria == 'ou':
            continue
        cat = Categoria(nome=categoria.strip())
        categoriaRepository.save(cat)


if __name__ == "__main__":
    extractEmpresas()
