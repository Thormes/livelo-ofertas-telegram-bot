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

    def remove(self, acompanhamento: Acompanhamento) -> bool:
        query = f"DELETE FROM {self.__table} WHERE chat_id = ? AND empresa_codigo = ?"
        params = (acompanhamento.user.chat_id, acompanhamento.empresa.codigo,)
        exec = DB.cur.execute(query, params)
        DB.con.commit()
        return exec.rowcount > 0

    def getAcompanhamentosComOfertas(self):
        query = self.__baseQuery__
        query += " WHERE id in (SELECT empresa_id FROM parceria WHERE oferta=1)"
        result = DB.cur.execute(query).fetchall()
        return [self.__mapInnerJoin(x) for x in result]

    def registerEnvio(self, acompanhamento):
        query = "UPDATE acompanhamento SET ultima_informacao=? WHERE chat_id=? AND empresa_codigo=?"
        param=(datetime.datetime.today().strftime("%Y-%m-%d"),acompanhamento.user.chat_id, acompanhamento.empresa.codigo)
        result = DB.cur.execute(query, param)
        DB.con.commit()
        return result.rowcount == 1

    def __mapInnerJoin(self, acomp: Any):
        u = User()
        ac = Acompanhamento()
        emp = Empresa()
        u.chat_id = acomp[3]
        u.first_name = acomp[4]
        u.last_name = acomp[5]
        u.username = acomp[6]
        emp.id = acomp[7]
        emp.nome = acomp[8]
        emp.codigo = acomp[9]
        emp.url = acomp[10]
        ac.empresa = emp
        ac.user = u
        ac.ultima_informacao = datetime.datetime.strptime(acomp[2], "%Y-%m-%d") if acomp[2] is not None else None
        return ac

