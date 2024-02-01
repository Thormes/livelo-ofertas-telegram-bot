import sqlite3
import os
con = sqlite3.connect("database.db")
cur = con.cursor()


def createTables():
    cur.execute("CREATE TABLE IF NOT EXISTS empresa(id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, codigo TEXT)")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS parceria(id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, moeda TEXT, pontos INTEGER, pontos_clube INTEGER, oferta BOOLEAN, inicio DATE, fim DATE, regras TEXT, FOREIGN KEY (empresa_id) REFERENCES empresa (id))")
    con.commit()

createTables()
print(cur.execute("SELECT * FROM sqlite_master").fetchall())
def getAll(table: str):
    return cur.execute(f"SELECT * FROM {table}").fetchall()


def getById(table: str, id: int):
    param = (id,)
    return cur.execute(f"SELECT * FROM {table} where id = ?", param).fetchone()


def getByProperty(table: str, column: str, value: str):
    param = (value,)
    return cur.execute(f"SELECT * FROM {table} WHERE {column} = ?", param).fetchall()


def addRecord(table: str, properties: dict):
    params = list(properties.values(),)
    keys = ",".join(properties.keys())
    number = "?, " * len(properties)
    number = number[0:-2]
    query = f"INSERT INTO {table} ({str(keys)}) values ({number})"
    response = cur.execute(query, params)
    con.commit()
    return response
