from .connecttry import get_connection, close_connection
from contextlib import contextmanager

@contextmanager
def db_cursor():
    """数据库游标上下文管理器"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        yield cursor
    finally:
        if cursor:
            cursor.close()
        if conn:
            close_connection(conn)

class PaperOperations:
    @staticmethod
    def get_all():
        with db_cursor() as cursor:
            cursor.execute("SELECT * FROM papers")
            papers = cursor.fetchall()  # 添加结果处理
            return papers
    
    @staticmethod
    def search_title(query):
        with db_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM papers 
                WHERE title LIKE %s OR abstract LIKE %s
                """, (f"%{query}%", f"%{query}%"))
            papers = cursor.fetchall()  # 添加结果处理
            return papers

    @staticmethod
    def get_by_id(query):
        with db_cursor() as cursor:
            cursor.execute("SELECT * FROM papers WHERE id = %s", (query,))
            paper = cursor.fetchone()  # 添加结果处理
            return paper