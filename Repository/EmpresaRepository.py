import Infra.database as DB
from Model.Model import Empresa
from typing import List


class EmpresaRepository:
    __table = "empresa"

    def getAll(self) -> List[Empresa]:
        lista = []
        empresas = DB.getAll(self.__table)
        for empresa in empresas:
            emp = Empresa()
            emp.id = empresa[0]
            emp.nome = empresa[1]
            emp.codigo = empresa[2]
            lista.append(emp)
        return lista

    def save(self, empresa: Empresa) -> bool:
        existente = DB.getByProperty(self.__table, "codigo", empresa.codigo)
        if len(existente) > 0:
            return True
        properties = {"nome":empresa.nome,"codigo":empresa.codigo}
        add = DB.addRecord(self.__table, properties)
        return add.rowcount == 1

    def limpar(self):
        DB.cur.execute(f"DELETE FROM {self.__table}")
        DB.con.commit()