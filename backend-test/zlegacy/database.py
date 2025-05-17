import MySQLdb

def get_connection():
    """获取数据库连接"""
    try:
        connection = MySQLdb.connect(
            host="obmt6mf0yc1gvn4w-mi.aliyun-cn-hangzhou-internet.oceanbase.cloud",
            port=3306,
            user="parry",
            password="2739458679AAbb//",
            database="paperdb-alpha"
        )
        return connection
    except MySQLdb.Error as e:
        raise Exception(f"数据库连接失败: {e}")

def close_connection(connection):
    """关闭数据库连接"""
    if connection and connection.open:
        connection.close()