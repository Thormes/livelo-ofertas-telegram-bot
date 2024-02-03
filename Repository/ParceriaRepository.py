import datetime

import Infra.database as DB
from Model.Model import Empresa, Parceria
from typing import List


class ParceriaRepository:
    __table = "parceria"

    def getAll(self) -> List[Parceria]:
        lista = []
        query = "SELECT * FROM empresa INNER JOIN parceria ON parceria.empresa_id = empresa.id"
        parcerias = DB.cur.execute(query).fetchall()
        for parceria in parcerias:
            emp = Empresa()
            emp.id = parceria[0]
            emp.nome = parceria[1]
            emp.codigo = parceria[2]
            emp.url = parceria[3]
            parc = Parceria()
            parc.id = parceria[4]
            parc.empresa = emp
            parc.moeda = parceria[5]
            parc.pontos = parceria[6]
            parc.pontosClube = parceria[7]
            parc.pontosBase = parceria[8]
            parc.oferta = True if parceria[9] == 1 else False
            if not parceria[10] is None:
                parc.inicio = datetime.datetime.strptime(parceria[10], "%Y-%m-%d")
                parc.fim = datetime.datetime.strptime(parceria[11], "%Y-%m-%d")
            parc.regras = parceria[12]
            lista.append(parc)
        return lista

    def save(self, parceria: Parceria) -> bool:
        properties = {"moeda": parceria.moeda, "pontos": parceria.pontos, "pontos_clube": parceria.pontosClube,
                      "oferta": parceria.oferta, "regras": parceria.regras, "empresa_id": parceria.empresa.id, "pontos_base": parceria.pontosBase}
        if not parceria.inicio is None:
            properties["inicio"] = parceria.inicio.strftime("%Y-%m-%d")
        if not parceria.fim is None:
            properties["fim"] = parceria.fim.strftime("%Y-%m-%d")
        add = DB.addRecord(self.__table, properties)
        return add.rowcount == 1

    def limpar(self):
        DB.cur.execute(f"DELETE FROM {self.__table}")
        DB.con.commit()
