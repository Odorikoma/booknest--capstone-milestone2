from utils.database import db
import decimal
from datetime import datetime

def convert_decimal_to_float(data):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(data, dict):
        return {k: convert_decimal_to_float(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_decimal_to_float(item) for item in data]
    elif isinstance(data, decimal.Decimal):
        return float(data)
    else:
        return data

# -------------------------
# Users
# -------------------------
class User:
    """User model"""

    @staticmethod
    def create(username, email, password_hash, role="user"):
        """
        创建新用户
        """
        sql = """
        INSERT INTO users (username, email, password_hash, role, create_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (username, email, password_hash, role, datetime.now())
        return db.execute_update(sql, params)

    @staticmethod
    def find_by_email(email):
        """
        根据邮箱查找用户
        """
        sql = """
        SELECT id, username, email, password_hash AS password, role, create_at
        FROM users
        WHERE email = %s
        """
        rows = db.execute_query(sql, (email,))
        return rows[0] if rows else None

    @staticmethod
    def find_by_id(user_id):
        sql = "SELECT * FROM users WHERE id = %s"
        rows = db.execute_query(sql, (user_id,))
        return rows[0] if rows else None

    @staticmethod
    def search(query):
        sql = "SELECT * FROM users WHERE username LIKE %s OR email LIKE %s"
        pattern = f"%{query}%"
        return db.execute_query(sql, (pattern, pattern))


# -------------------------
# Books
# -------------------------
class Book:
    """Book model"""

    @staticmethod
    def get_all(search_title=None, search_author=None):
        sql = "SELECT * FROM books WHERE 1=1"
        params = []
        if search_title:
            sql += " AND title LIKE %s"
            params.append(f"%{search_title}%")
        if search_author:
            sql += " AND author LIKE %s"
            params.append(f"%{search_author}%")
        sql += " ORDER BY created_at DESC"
        result = db.execute_query(sql, params if params else None) or []
        return convert_decimal_to_float(result)

    @staticmethod
    def find_by_id(book_id):
        sql = "SELECT * FROM books WHERE id = %s"
        rows = db.execute_query(sql, (book_id,))
        result = rows[0] if rows else None
        return convert_decimal_to_float(result) if result else None

    @staticmethod
    def create(title, author, description, stock, cover_image_url=None, price=0.0):
        """
        创建新图书
        """
        sql = """
        INSERT INTO books (title, author, description, stock, cover_image_url, price)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (title, author, description, stock, cover_image_url, price)
        return db.execute_update(sql, params)

    @staticmethod
    def update(book_id, title, author, description, stock, cover_image_url=None, price=0.0):
        """
        更新图书信息
        """
        sql = """
        UPDATE books
        SET title=%s, author=%s, description=%s, stock=%s,
            cover_image_url=%s, price=%s, updated_at=CURRENT_TIMESTAMP
        WHERE id=%s
        """
        params = (title, author, description, stock, cover_image_url, price, book_id)
        return db.execute_update(sql, params)

    @staticmethod
    def delete(book_id):
        sql = "DELETE FROM books WHERE id = %s"
        return db.execute_update(sql, (book_id,))

    @staticmethod
    def update_stock(book_id, delta):
        """
        更新图书库存
        """
        sql = "UPDATE books SET stock = stock + %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
        return db.execute_update(sql, (delta, book_id))


# -------------------------
# Borrows
# -------------------------
class BorrowRecord:
    """
    借阅记录模型 - 对应数据库表 `borrows`
    """

    @staticmethod
    def create(user_id, book_id, borrow_status="requested", borrow_date=None, notes=None):
        print(f"\n--- BorrowRecord.create 调试日志 ---")
        print(f"输入参数:")
        print(f"  user_id: {user_id} (类型: {type(user_id)})")
        print(f"  book_id: {book_id} (类型: {type(book_id)})")
        print(f"  borrow_status: {borrow_status} (类型: {type(borrow_status)})")
        print(f"  borrow_date: {borrow_date} (类型: {type(borrow_date)})")
        print(f"  notes: {notes} (类型: {type(notes)})")
        
        # 处理日期
        if borrow_date:
            # 如果传入的是字符串格式的日期，尝试转换为datetime对象
            if isinstance(borrow_date, str):
                try:
                    from datetime import datetime as dt
                    actual_borrow_date = dt.strptime(borrow_date, '%Y-%m-%d')
                    print(f"字符串日期 '{borrow_date}' 转换为datetime: {actual_borrow_date}")
                except ValueError as e:
                    print(f"日期格式转换失败: {e}, 使用当前时间")
                    actual_borrow_date = datetime.now()
            else:
                actual_borrow_date = borrow_date
        else:
            actual_borrow_date = datetime.now()
        print(f"实际使用的借阅日期: {actual_borrow_date} (类型: {type(actual_borrow_date)})")
        
        sql = """
        INSERT INTO borrows (user_id, book_id, borrow_date, borrow_status, notes)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (user_id, book_id, actual_borrow_date, borrow_status, notes)
        
        print(f"准备执行的SQL: {sql}")
        print(f"SQL参数: {params}")
        
        try:
            result = db.execute_update(sql, params)
            print(f"数据库执行结果: {result}")
            print(f"结果类型: {type(result)}")
            return result
        except Exception as e:
            print(f"❌ 数据库执行出错: {str(e)}")
            print(f"错误类型: {type(e).__name__}")
            import traceback
            print("错误堆栈:")
            traceback.print_exc()
            raise e

    @staticmethod
    def get_by_user(user_id):
        sql = """
        SELECT br.id, br.user_id, br.book_id, br.borrow_date, br.return_date, br.borrow_status, br.notes,
               b.title, b.author
          FROM borrows br
          JOIN books b ON br.book_id = b.id
         WHERE br.user_id = %s
         ORDER BY br.borrow_date DESC
        """
        return db.execute_query(sql, (user_id,)) or []

    @staticmethod
    def get_all(borrow_status=None):
        sql = """
        SELECT br.*, b.title, b.author, u.username, u.email
          FROM borrows br
          JOIN books b ON br.book_id = b.id
          JOIN users u ON br.user_id = u.id
        """
        params = []
        if borrow_status:
            sql += " WHERE br.borrow_status = %s"
            params.append(borrow_status)
        sql += " ORDER BY br.borrow_date DESC"
        return db.execute_query(sql, params if params else None) or []

    @staticmethod
    def update_status(record_id, borrow_status, return_date=None, notes=None):
        if return_date is not None and notes is not None:
            sql = "UPDATE borrows SET borrow_status=%s, return_date=%s, notes=%s WHERE id=%s"
            params = (borrow_status, return_date, notes, record_id)
        elif return_date is not None:
            sql = "UPDATE borrows SET borrow_status=%s, return_date=%s WHERE id=%s"
            params = (borrow_status, return_date, record_id)
        elif notes is not None:
            sql = "UPDATE borrows SET borrow_status=%s, notes=%s WHERE id=%s"
            params = (borrow_status, notes, record_id)
        else:
            sql = "UPDATE borrows SET borrow_status=%s WHERE id=%s"
            params = (borrow_status, record_id)
        return db.execute_update(sql, params)

    @staticmethod
    def find_by_id(record_id):
        sql = "SELECT * FROM borrows WHERE id = %s"
        rows = db.execute_query(sql, (record_id,))
        return rows[0] if rows else None

    @staticmethod
    def find_active_borrow(user_id, book_id):
        """查找用户对特定图书的活跃借阅记录（未归还的）"""
        sql = """
        SELECT * FROM borrows 
        WHERE user_id = %s AND book_id = %s 
        AND borrow_status IN ('requested', 'borrowed')
        """
        rows = db.execute_query(sql, (user_id, book_id))
        return rows[0] if rows else None


