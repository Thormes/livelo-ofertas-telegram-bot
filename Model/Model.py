class Empresa:
    def __init__(self):
        self.nome = ""
        self.codigo = ""
        self.id = None

    def __str__(self):
        return f"{self.nome}"


class Parceria:
    def __init__(self):
        self.moeda = "R$"
        self.base = 1
        self.pontos = 0
        self.pontosClube = 0
        self.oferta = False
        self.inicio = None
        self.fim = None
        self.regras = ""
        self.empresa = None
        self.id = None

    def __str__(self):
        if self.oferta and self.inicio is not None:
            return f"*{self.empresa.nome}* - {self.pontos} pontos ({self.pontosClube} clube) por {self.moeda} - OFERTA ({self.inicio.strftime('%d/%m/%Y')} a {self.fim.strftime('%d/%m/%Y')}). _{self.regras}_"
        else:
            return f"*{self.empresa.nome}* - {self.pontos} pontos ({self.pontosClube} clube) por {self.moeda}. _{self.regras}_"
