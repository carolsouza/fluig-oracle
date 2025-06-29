import sqlite3

class SQLitePipeline:
    def open_spider(self, spider):
        self.connection = sqlite3.connect('../src/data/content_data.db')
        self.cursor = self.connection.cursor()

        self.cursor.execute('DROP TABLE IF EXISTS content_data')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                title TEXT,
                url TEXT,
                content TEXT,
                content_md TEXT,
                created_date datetime default current_timestamp
            )
        ''')
        self.connection.commit()

    def process_item(self, data, spider):               
        self.cursor.execute('''
            INSERT INTO content_data (title, category, url, content, content_md) VALUES (?, ?, ?, ?, ?)
        ''', (data['title'], data['category'], data['url'], data['content'], data["content_md"]))
        self.connection.commit()
        return data

    def close_spider(self, spider):
        self.connection.commit()
        self.connection.close()