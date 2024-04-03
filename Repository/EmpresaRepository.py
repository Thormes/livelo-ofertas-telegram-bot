import Infra.database as DB
from Model.Model import Empresa, Categoria
from typing import List
from Repository.CategoriaRepository import CategoriaRepository


class EmpresaRepository:
    __catRepository = CategoriaRepository()
    __table = "empresa"

    def getAll(self) -> List[Empresa]:
        lista = []
        empresas = DB.getAll(self.__table, ("nome", "ASC"))
        categorias = self.__catRepository.getAll()
        cods = {k.nome: k  for k in categorias}
        for empresa in empresas:
            emp = Empresa()
            emp.id = empresa[0]
            emp.nome = empresa[1]
            emp.codigo = empresa[2]
            emp.url = empresa[3]
            cat_empresas = empresa[4].split(" ") if not empresa[4] is None else []
            for cat in cat_empresas:
                if cods.get(cat, False):
                    emp.categorias.append(cods[cat])
            lista.append(emp)
        return lista

    def save(self, empresa: Empresa) -> bool:
        existente = DB.getByProperty(self.__table, "codigo", empresa.codigo)
        if len(existente) > 0:
            id = existente[0][0]
            if existente[0][4] is None:
                DB.cur.execute(f"UPDATE empresa set categorias='{empresa.categorias}' WHERE id={id}")
                DB.con.commit()
            return True
        properties = {"nome": empresa.nome, "codigo": empresa.codigo, "url": empresa.url, "categorias": empresa.categorias}
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
