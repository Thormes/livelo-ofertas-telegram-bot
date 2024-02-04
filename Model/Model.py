import datetime


class Empresa:
    def __init__(self):
        self.nome = ""
        self.codigo = ""
        self.url = ""
        self.id = None

    def __str__(self):
        return f"{self.nome}"


class User:
    def __init__(self):
        self.chat_id = None
        self.first_name = ""
        self.last_name = ""


class Acompanhamento:
    def __init__(self):
        self.user = None
        self.empresa = None
        self.ultima_informacao = None


class Parceria:
    def __init__(self):
        self.moeda = "R$"
        self.pontos = 0
        self.pontosClube = 0
        self.pontosBase = 0
        self.conectivo = ""
        self.oferta = False
        self.inicio = None
        self.fim = None
        self.regras = ""
        self.empresa = None
        self.id = None

    def __emOferta__(self):
        hoje = datetime.datetime.today()
        return self.oferta and self.inicio is not None and (self.inicio <= hoje and self.fim >= hoje)

    def __str__(self):
        txt_conectivo = ""
        if self.conectivo == "até":
            txt_conectivo = "até "

        txt_pontos = "pontos" if self.pontos >1 else "ponto"



        if self.__emOferta__():
            return f"*{self.empresa.nome}* - {txt_conectivo}{self.pontos} {txt_pontos} ({self.pontosClube} clube) por {self.moeda} - OFERTA ({self.inicio.strftime('%d/%m/%Y')} a {self.fim.strftime('%d/%m/%Y')}). _{self.regras}_ {self.empresa.url}"
        else:
            return f"*{self.empresa.nome}* - {txt_conectivo}{self.pontos} {txt_pontos} ({self.pontosClube} clube) por {self.moeda}. _{self.regras}_ {self.empresa.url}"

    def toMarkdown(self):
        hoje = datetime.datetime.today()
        txt_conectivo = ""
        if self.conectivo == "até":
            txt_conectivo = "até "

        txt_pontos = "pontos" if self.pontos >1 else "ponto"
        if self.__emOferta__():
            extras = []
            if self.inicio.strftime("%Y%m%d") == hoje.strftime("%Y%m%d"):
                extras.append("🆕")

            if self.fim.strftime("%Y%m%d") == hoje.strftime("%Y%m%d"):
                extras.append("🏁")
            return f"*{self.empresa.nome}* {', '.join(extras)} - {txt_conectivo}{self.pontos} {txt_pontos} ({self.pontosClube} clube) por {self.moeda} - OFERTA ({self.inicio.strftime('%d/%m/%Y')} a {self.fim.strftime('%d/%m/%Y')}). _{self.regras}_ {self.empresa.url}"
        else:
            return f"*{self.empresa.nome}* - {txt_conectivo}{self.pontos} {txt_pontos} ({self.pontosClube} clube) por {self.moeda}. _{self.regras}_ {self.empresa.url}"

    def toHTML(self):
        hoje = datetime.datetime.today()
        txt_conectivo = ""
        if self.conectivo == "até":
            txt_conectivo = "até "

        txt_pontos = "pontos" if self.pontos >1 else "ponto"
        if self.__emOferta__():
            extras = []
            if self.inicio.strftime("%Y%m%d") == hoje.strftime("%Y%m%d"):
                extras.append("🆕")

            if self.fim.strftime("%Y%m%d") == hoje.strftime("%Y%m%d"):
                extras.append("🏁")
            return f"<b>{self.empresa.nome}</b> {', '.join(extras)} - {txt_conectivo}{self.pontos} {txt_pontos} ({self.pontosClube} clube) por {self.moeda} - OFERTA ({self.inicio.strftime('%d/%m/%Y')} a {self.fim.strftime('%d/%m/%Y')}). <i>{self.regras}</i> {self.empresa.url}"
        else:
            return f"<b>{self.empresa.nome}</b> - {txt_conectivo}{self.pontos} {txt_pontos} ({self.pontosClube} clube) por {self.moeda}. <i>{self.regras}</i> {self.empresa.url}"
