# MySQL Database Connection Utility

import pymysql
from config import Config

class Database:
    def __init__(self):
        self.host = Config.MYSQL_HOST
        self.port = Config.MYSQL_PORT
        self.user = Config.MYSQL_USER
        self.password = Config.MYSQL_PASSWORD
        self.database = Config.MYSQL_DATABASE
        
    def get_connection(self):
        """Establish and return a database connection"""
        try:
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection
        except Exception as e:
            print(f"Database connection failed: {e}")
            return None
    
    def execute_query(self, query, params=None):
        """Execute a SELECT query"""
        connection = self.get_connection()
        if not connection:
            return None
            
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
                return result
        except Exception as e:
            print(f"Query execution failed: {e}")
            return None
        finally:
            connection.close()
    
    def execute_update(self, query, params=None):
        """Execute an INSERT, UPDATE, or DELETE statement"""
        print(f"\n--- Database.execute_update 调试日志 ---")
        print(f"连接参数: host={self.host}, port={self.port}, user={self.user}, database={self.database}")
        
        connection = self.get_connection()
        if not connection:
            print("❌ 数据库连接失败")
            return False
        
        print("✅ 数据库连接成功")
        print(f"执行的SQL: {query}")
        print(f"SQL参数: {params}")
        print(f"参数类型: {[type(p) for p in params] if params else 'None'}")
            
        try:
            with connection.cursor() as cursor:
                print("准备执行SQL...")
                cursor.execute(query, params)
                print("SQL执行成功，准备提交事务...")
                connection.commit()
                rowcount = cursor.rowcount
                lastrowid = cursor.lastrowid
                print(f"✅ 事务提交成功")
                print(f"影响行数: {rowcount}")
                print(f"插入ID: {lastrowid}")
                return lastrowid if lastrowid else rowcount
        except Exception as e:
            print(f"❌ SQL执行失败: {str(e)}")
            print(f"错误类型: {type(e).__name__}")
            import traceback
            print("完整错误堆栈:")
            traceback.print_exc()
            connection.rollback()
            print("已回滚事务")
            return False
        finally:
            connection.close()
            print("数据库连接已关闭")

# Global database instance
db = Database()
