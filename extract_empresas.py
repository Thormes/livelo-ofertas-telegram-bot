import time
from CardParceiro import CardParceiro
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from Model.Model import Empresa
from Repository.EmpresaRepository import EmpresaRepository


def extractEmpresas():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome()
    driver.get("https://www.livelo.com.br/ganhe-pontos-compre-e-pontue")
    try:
        myElem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'div-parity')))
        print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")
    lista_cards = driver.find_element(By.ID, "div-cardsParity")
    parceiros = []
    if not lista_cards is None:
        cards = lista_cards.find_elements(By.ID, "div-parity")
        for card in cards:
            cardParceiro = CardParceiro()
            cardParceiro.fromCard(card)
            parceiros.append(cardParceiro)

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
