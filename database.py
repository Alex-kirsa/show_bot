import sqlite3
from icecream import ic

class Database:
    def _connect(self):
        return sqlite3.connect("database.db")
    
    def _select(self, request:str):
        with self._connect() as con:
            cur = con.cursor()
            cur.execute(request)
        return cur
    
    def _request(self, request:str):
        with self._connect() as con:
            cur = con.cursor()
            cur.execute(request)
            con.commit()
        return

    def check_user_in_db(self, user_id:str):
        with self._connect() as con:
            cur = con.cursor()
            user = cur.execute(f"SELECT * FROM users WHERE user_id='{user_id}'").fetchone()
        if user==None:
            self._request(f"INSERT INTO users(user_id) VALUES ('{user_id}')")
        
    def update_language(self, user_id:str, lang:str):
        self._request(f"UPDATE users SET language='{lang}' WHERE user_id='{user_id}'")

    def get_language_by_id(self, user_id:str|int) -> str:
        lang = self._select(f"SELECT language FROM users WHERE user_id='{user_id}'").fetchone()
        lang[0]
        return lang[0]


    
db = Database()