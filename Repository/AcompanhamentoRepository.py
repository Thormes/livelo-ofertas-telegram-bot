import datetime

import Infra.database as DB
from Model.Model import User, Empresa, Acompanhamento
from typing import List, Optional, Any


class AcompanhamentoRepository:
    __table = "acompanhamento"
    __baseQuery__ = "SELECT * FROM acompanhamento " \
                    "INNER JOIN user ON acompanhamento.chat_id = user.chat_id " \
                    "INNER JOIN empresa ON acompanhamento.empresa_codigo = empresa.codigo"

    def getAll(self) -> List[Acompanhamento]:
        lista = []
        acompanhamentos = DB.cur.execute(self.__baseQuery__).fetchall()
        for acomp in acompanhamentos:
            ac = self.__mapInnerJoin(acomp)
            lista.append(ac)
        return lista

    def getByUserId(self, userId: int) -> list[Acompanhamento]:
        query = self.__baseQuery__ + " WHERE user.chat_id = ?"
        param = (userId,)
        acompanhamentos = DB.cur.execute(query, param)
        retorno = [self.__mapInnerJoin(acomp) for acomp in acompanhamentos]
        return retorno

    def save(self, user: User, empresa: Empresa) -> bool:
        properties = {"chat_id": user.chat_id, "empresa_codigo": empresa.codigo}
        add = DB.addRecord(self.__table, properties)
        return add.rowcount == 1

    def limpar(self):
        DB.cur.execute(f"DELETE FROM {self.__table}")
        DB.con.commit()

    def __mapInnerJoin(self, acomp: Any):
        u = User()
        ac = Acompanhamento()
        emp = Empresa()
        u.chat_id = acomp[3]
        u.first_name = acomp[4]
        u.last_name = acomp[4]
        emp.id = acomp[5]
        emp.nome = acomp[6]
        emp.codigo = acomp[7]
        ac.empresa = emp
        ac.user = u
        ac.ultima_informacao = datetime.datetime.strptime(acomp[2], "%Y-%m-%d")
        return ac
