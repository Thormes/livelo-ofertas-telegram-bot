import datetime

import Infra.database as DB
from Model.Model import User
from typing import List, Optional


class UserRepository:
    __table = "user"

    def getAll(self) -> List[User]:
        lista = []
        users = DB.getAll(self.__table)
        for user in users:
            u = User()
            u.chat_id = user[0]
            u.first_name = user[1]
            u.last_name = user[2]
            lista.append(u)
        return lista

    def getById(self, userId: int) -> Optional[User]:
        user = DB.getByProperty(self.__table, 'chat_id', str(userId))
        if len(user) == 0:
            return None
        return user[0]

    def save(self, user: User) -> bool:
        existing = self.getById(user.chat_id)
        if existing is None:
            properties = {"name": user.first_name, "last_name": user.last_name, "chat_id": user.chat_id, "username": user.username}
            add = DB.addRecord(self.__table, properties)
            return add.rowcount == 1
        else:
            return True

    def limpar(self):
        DB.cur.execute(f"DELETE FROM {self.__table}")
        DB.con.commit()
