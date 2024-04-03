import Infra.database as DB
from Model.Model import Categoria
from typing import List


class CategoriaRepository:
    __table = "categoria"

    def getAll(self) -> List[Categoria]:
        lista = []
        categorias = DB.getAll(self.__table, ("nome", "ASC"))
        for categoria in categorias:
            cat = Categoria(categoria[1], categoria[2])
            cat.id = categoria[0]
            lista.append(cat)
        return lista

    def save(self, categoria: Categoria) -> bool:
        existente = DB.getByProperty(self.__table, "nome", categoria.nome)
        if len(existente) > 0:
            return True
        properties = {"nome": categoria.nome, "descricao": categoria.descricao}
        add = DB.addRecord(self.__table, properties)
        return add.rowcount == 1

    def limpar(self):
        DB.cur.execute(f"DELETE FROM {self.__table}")
        DB.con.commit()

    def remove(self, categoria: Categoria) -> bool:
        remove = DB.removeBy(self.__table, "nome", categoria.nome)
        if remove.rowcount > 0:
            return True

        return False
