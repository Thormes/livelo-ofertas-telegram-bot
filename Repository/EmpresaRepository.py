import Infra.database as DB
from Model.Model import Empresa
from typing import List


class EmpresaRepository:
    __table = "empresa"

    def getAll(self) -> List[Empresa]:
        lista = []
        empresas = DB.getAll(self.__table, ("nome", "ASC"))
        for empresa in empresas:
            emp = Empresa()
            emp.id = empresa[0]
            emp.nome = empresa[1]
            emp.codigo = empresa[2]
            emp.url = empresa[3]
            lista.append(emp)
        return lista

    def save(self, empresa: Empresa) -> bool:
        existente = DB.getByProperty(self.__table, "url", empresa.url)
        if len(existente) > 0:
            return True
        properties = {"nome": empresa.nome, "codigo": empresa.codigo, "url": empresa.url}
        add = DB.addRecord(self.__table, properties)
        return add.rowcount == 1

    def limpar(self):
        DB.cur.execute(f"DELETE FROM {self.__table}")
        DB.con.commit()

    def remove(self, empresa: Empresa) -> bool:
        remove = DB.removeBy(self.__table, "url", empresa.url)
        if remove.rowcount > 0:
            return True

        return False
