import sqlite3

class SQLitePipeline:
    def __init__(self, db_name='../src/data/content_data.db'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                title TEXT,
                url TEXT,
                content TEXT,
                created_date datetime default current_timestamp
            )
        ''')
        self.connection.commit()

    def process_new_data(self, data):
        self.cursor.execute('''
            INSERT INTO scraped_data (title, category url, content) VALUES (?, ?, ?, ?)
        ''', (data['title'], data['category'], data['url'], data['content']))
        self.connection.commit()
        return data

    def close_connection(self):
        self.connection.close()