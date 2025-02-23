import sqlite3
from typing import List, Tuple, Dict


class SQLiteDB:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name: str, columns: Dict[str, str]):
        """
        Создает таблицу в базе данных.

        Args:
            table_name (str): Имя таблицы.
            columns (Dict[str, str]): Словарь с именами столбцов и их типами.
        """
        column_str = ', '.join(f'{key} {value}' for key, value in columns.items())
        query = f'CREATE TABLE {table_name} ({column_str})'
        self.cursor.execute(query)
        self.conn.commit()

    def insert_data(self, table_name: str, data: Dict[str, str]):
        """
        Вставляет данные в таблицу.

        Args:
            table_name (str): Имя таблицы.
            data (Dict[str, str]): Словарь с данными для вставки.
        """
        column_str = ', '.join(data.keys())
        value_str = ', '.join(f'"{value}"' for value in data.values())
        query = f'INSERT INTO {table_name} ({column_str}) VALUES ({value_str})'
        self.cursor.execute(query)
        self.conn.commit()

    def select_data(self, table_name: str, columns: List[str], conditions: List[Tuple[str, str]] = None):
        """
        Выполняет запрос SELECT к таблице.

        Args:
            table_name (str): Имя таблицы.
            columns (List[str]): Список имен столбцов для выборки.
            conditions (List[Tuple[str, str]], optional): Список условий для фильтрации данных. Defaults to None.

        Returns:
            List[Tuple]: Список кортежей с данными.
        """
        column_str = ', '.join(columns)
        query = f'SELECT {column_str} FROM {table_name}'
        if conditions:
            condition_str = ' AND '.join(f'{key} = "{value}"' for key, value in conditions)
            query += f' WHERE {condition_str}'
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def update_data(self, table_name: str, data: Dict[str, str], conditions: List[Tuple[str, str]]):
        """
        Обновляет данные в таблице.

        Args:
            table_name (str): Имя таблицы.
            data (Dict[str, str]): Словарь с данными для обновления.
            conditions (List[Tuple[str, str]]): Список условий для фильтрации данных.
        """
        set_str = ', '.join(f'{key} = "{value}"' for key, value in data.ite ms())
        condition_str = ' AND '.join(f'{key} = "{value}"' for key, value in conditions)
        query = f'UPDATE {table_name} SET {set_str} WHERE {condition_str}'
        self.cursor.execute(query)
        self.conn.commit()

    def delete_data(self, table_name: str, conditions: List[Tuple[str, str]]):
        """
        Удаляет данные из таблицы.

        Args:
            table_name (str): Имя таблицы.
            conditions (List[Tuple[str, str]]): Список условий для фильтрации данных.
        """
        condition_str = ' AND '.join(f'{key} = "{value}"' for key, value in conditions)
        query = f'DELETE FROM {table_name} WHERE {condition_str}'
        self.cursor.execute(query)
        self.conn.commit()

    def close(self):
        """
        Закрывает соединение с базой данных.
        """
        self.conn.close()
