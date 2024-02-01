import re

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium import webdriver


class CardParceiro:
    def __init__(self):
        self.empresa = ""
        self.moeda = "R$"
        self.base = 1
        self.pontos = 0
        self.pontosClube = 0
        self.promocao = False
        self.url = ""
        self.inicio = None
        self.fim = None
        self.codigo = ""

    def fromCard(self, card: WebElement):
        divs = card.find_elements(By.XPATH, "./div")
        if len(divs) != 4:
            raise ValueError("Card não tem 4 divs filhas")

        self.__getDadosPromocao(divs[0])
        self.__getDadosValores(divs[2])
        self.__getDadosParceiro(divs[3])

    def __str__(self):
        if self.promocao:
            return f"{self.empresa}\t\t{self.pontos} pontos ({self.pontosClube} Clube)\t a cada: {self.moeda} (OFERTA)"
        else:
            return f"{self.empresa}\t\t{self.pontos} pontos ({self.pontosClube} Clube)\t a cada: {self.moeda}"

    def __getDadosParceiro(self, div: WebElement):
        link = div.find_element(By.TAG_NAME, "a")
        empresa = link.get_dom_attribute("title")
        empresa = empresa.replace("Ir para regras do parceiro ", "")
        self.empresa = empresa
        self.url = link.get_attribute("href")
        self.codigo = self.url[self.url.rfind("/") + 1:]
        if len(self.codigo) > 3:
            self.codigo = ""

    def __getDadosPromocao(self, div: WebElement):
        try:
            div_oferta = div.find_element(By.TAG_NAME, "div")
            self.promocao = True
        except NoSuchElementException:
            pass

    def __getDadosValores(self, div: WebElement):
        info = div.find_element(By.CLASS_NAME, "info__value")
        text = info.text.replace("\n", " ")
        text_clube = None
        try:
            div_clube = div.find_element(By.CLASS_NAME, "info__club")
            text_clube = div_clube.text.replace("\n", " ")
        except NoSuchElementException:
            pass

        if text_clube is None:
            self.moeda = text[0:2]
            numbers = re.findall('\d{1,3}', text)
            self.pontos = numbers[1]
            self.pontosClube = self.pontos
        else:
            self.moeda = text_clube[0:2]
            numbers_clube = re.findall('\d{1,3}', text_clube)
            self.pontosClube = numbers_clube[1]
            numbers = re.findall('\d{1,3}', text)
            self.pontos = numbers[0]
