import sqlite3
import os

con = sqlite3.connect("database.db", check_same_thread=False)
cur = con.cursor()


def createTables():
    cur.execute("CREATE TABLE IF NOT EXISTS empresa(id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, codigo TEXT, "
                "url TEXT)")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS parceria(empresa_id INTEGER PRIMARY KEY, moeda TEXT, "
        "pontos INTEGER, pontos_clube INTEGER, pontos_base INTEGER, conectivo TEXT, oferta BOOLEAN, inicio DATE, "
        "fim DATE, regras TEXT, FOREIGN KEY (empresa_id) REFERENCES empresa (id))")
    cur.execute("CREATE TABLE IF NOT EXISTS user (chat_id INTEGER PRIMARY KEY, name TEXT, last_name TEXT, username TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS acompanhamento (chat_id INTEGER, empresa_codigo TEXT, ultima_informacao "
                "DATE, PRIMARY KEY(chat_id, empresa_codigo))")
    con.commit()


createTables()


def getAll(table: str):
    return cur.execute(f"SELECT * FROM {table}").fetchall()


def getById(table: str, entityId: int):
    param = (entityId,)
    return cur.execute(f"SELECT * FROM {table} where id = ?", param).fetchone()


def getByProperty(table: str, column: str, value: str):
    param = (value,)
    return cur.execute(f"SELECT * FROM {table} WHERE {column} = ?", param).fetchall()


def addRecord(table: str, properties: dict):
    params = list(properties.values(), )
    keys = ",".join(properties.keys())
    number = "?, " * len(properties)
    number = number[0:-2]
    query = f"INSERT INTO {table} ({str(keys)}) values ({number})"
    response = cur.execute(query, params)
    con.commit()
    return response
