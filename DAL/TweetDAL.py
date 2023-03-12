import psycopg2

class TweetDAL:
    def __init__(self):
        self.conn = psycopg2.connect(
            database="postgres",
            user='postgres',
            password='Goodluck123!',
            host='localhost',
            port='5432'
        )

        self.scheme_name = 'tweepy'
        self.table_name = 'tweet'

    def fetch_all(self):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {self.scheme_name}.{self.table_name}")
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def insert(self, input_data):
        cursor = self.conn.cursor()
        sql = f"INSERT into {self.scheme_name}.{self.table_name} " \
            f"(tweet_id, created_at, author_id, text, conversation_id, conversation_txt," \
            f"retweet_count, reply_count, like_count, quote_count, sentiment_score) " \
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.executemany(sql, input_data)
        self.conn.commit()