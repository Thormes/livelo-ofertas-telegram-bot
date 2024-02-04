import time
from CardParceiro import CardParceiro
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from Model.Model import Empresa
from Repository.EmpresaRepository import EmpresaRepository

from Logger.logger import get_logger

loger = get_logger("Empresas", "empresas.log")

def extractEmpresas():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=old")
    loger.info("Iniciando Chrome Driver")
    driver = webdriver.Chrome(options)
    loger.info("Navegando até a página de parcerias")
    driver.get("https://www.livelo.com.br/ganhe-pontos-compre-e-pontue")
    try:
        loger.info("Aguardando localizar o primeiro elemento de card de parceria presente na página")
        myElem = WebDriverWait(driver, 59).until(EC.presence_of_element_located((By.ID, 'div-parity')))

    except TimeoutException:
        loger.info("Elemento não foi encontrado, mesmo após 59 segundos")
        driver.close()
        return
    lista_cards = driver.find_element(By.ID, "div-cardsParity")
    parceiros = []
    loger.info("Lendo cards de parcerias")
    if not lista_cards is None:
        cards = lista_cards.find_elements(By.ID, "div-parity")
        for card in cards:
            cardParceiro = CardParceiro()
            cardParceiro.fromCard(card)
            parceiros.append(cardParceiro)

    loger.info("Realizando importação de", len(parceiros), "parceiros")
    empresa_repository = EmpresaRepository()
    for card in parceiros:
        empresa = Empresa()
        empresa.nome = card.empresa
        empresa.codigo = card.codigo
        empresa.url = card.url
        empresa_repository.save(empresa)

    driver.close()


if __name__ == "__main__":
    extractEmpresas()
