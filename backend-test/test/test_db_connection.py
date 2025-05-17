import pytest
from flask import g, current_app
from app.db import get_db # get_db 负责实际的连接尝试
import mysql.connector # 导入以捕获特定的数据库错误类型

def test_database_can_connect(app):
    """
    测试应用程序是否可以使用其配置和 get_db() 工具成功连接到数据库。
    这个测试依赖于 app fixture (来自 conftest.py) 来提供应用上下文和配置。
    """
    with app.app_context():
        current_app.logger.info(
            f"Attempting to connect to database: {current_app.config['OB_DATABASE']} "
            f"on {current_app.config['OB_HOST']}:{current_app.config['OB_PORT']} "
            f"as user {current_app.config['OB_USER']}"
        )
        try:
            # 调用 get_db() 会尝试建立连接并将其存储在 g.db
            # 如果连接失败，get_db() 内部的 mysql.connector.connect() 会抛出异常
            db_connection = get_db()

            # 检查 g.db 是否已设置
            assert g.db is not None, "g.db was not set after calling get_db(). Connection might have failed silently before this point if get_db() doesn't raise."
            
            # 检查连接对象是否存在且已连接
            assert db_connection is not None, "get_db() returned None, connection failed."
            assert db_connection.is_connected(), "Database connection was established but is_connected() returns False."

            # (可选) 执行一个非常简单的查询以进一步验证连接是否可用
            cursor = db_connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            
            assert result is not None and result[0] == 1, "Basic 'SELECT 1' query failed after connecting."
            
            success_msg = (f"Successfully connected to OceanBase database "
                           f"'{current_app.config['OB_DATABASE']}' "
                           f"and executed a test query.")
            current_app.logger.info(success_msg)
            print(f"\n[INFO] {success_msg}") # Print for visibility if running pytest with -s

        except mysql.connector.Error as e:
            # 如果 get_db() 中的连接尝试失败，它会抛出 mysql.connector.Error
            # 这个显式的捕获和 pytest.fail 提供了更清晰的失败信息
            error_msg = (f"Database connection or simple query failed for "
                         f"'{current_app.config['OB_DATABASE']}': {e}")
            current_app.logger.error(error_msg)
            pytest.fail(error_msg)
        except Exception as e_general:
            # 捕获测试过程中任何其他意外的异常
            error_msg = f"An unexpected error occurred during database connection test: {e_general}"
            current_app.logger.error(error_msg, exc_info=True)
            pytest.fail(error_msg)
        
        # 注意: 不需要在这里显式关闭 g.db。
        # 在 app/__init__.py 中注册的 app.teardown_appcontext(close_db)
        # 会在应用上下文结束时自动处理数据库连接的关闭。