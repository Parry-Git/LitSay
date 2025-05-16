import MySQLdb
import sys

try:
    # 建立数据库连接
    connection = MySQLdb.connect(host="obmt6mf0yc1gvn4w-mi.aliyun-cn-hangzhou-internet.oceanbase.cloud", 
                                port=3306, user="parry", 
                                password="2739458679AAbb//", database="paperdb-alpha")
                                #  ssl_mode="VERIFY_CA", ssl={"ca": "database\\ssl\\ca.pem"})
    
    # 创建游标对象
    cursor = connection.cursor()
    
    # 查询所有表
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    print("数据库中的表:")
    for table in tables:
        print(f"- {table[0]}")
    
    # 获取整个数据库的结构
    cursor.execute("""
        SELECT table_name, column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = 'paperdb-alpha'
        ORDER BY table_name, ordinal_position
    """)
    db_structure = cursor.fetchall()
    
    print("\n数据库完整结构:")
    current_table = None
    for row in db_structure:
        if row[0] != current_table:
            current_table = row[0]
            print(f"\n表 {current_table}:")
        print(f"- {row[1]}: {row[2]}{f'({row[3]})' if row[3] else ''}")
    
    
except MySQLdb.Error as e:
    print(f"数据库错误: {e}")
    sys.exit(1)
    
finally:
    # 关闭数据库连接
    if 'connection' in locals() and connection.open:
        cursor.close()
        connection.close()
        print("数据库连接已关闭")
      