import sqlite3
from sqlite3 import Connection, Cursor

from models import *

def create_geo_id_table() -> None:
    conn: Connection = _get_connection()
    try:
        cursor: Cursor = conn.cursor()
        cursor.execute(CREATE_GEO_ID_TABLE)
        conn.commit()
    finally:
        conn.close()

def insert_geo_id(geo_id: GeoId) -> None:
    conn: Connection = _get_connection()
    try:
        cursor: Cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO geo_id (geo_id, country) VALUES (?, ?)",
            (geo_id.geo_id, geo_id.country.lower())
        )
        conn.commit()
    finally:
        conn.close()

def get_geo_id(country: str) -> GeoId:
    conn: Connection = _get_connection()
    try:
        cursor: Cursor = conn.cursor()
        cursor.execute("SELECT geo_id, country FROM geo_id WHERE country = ?", (country.lower(),))
        row = cursor.fetchone()
        if row:
            return GeoId(geo_id=row[0], country=row[1])
        else:
            return None
    finally:
        conn.close()

def _get_connection(db_path:str="data_base/main_data_base.db") -> Connection:
    return sqlite3.connect(db_path) 


