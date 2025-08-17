# Borrow Management Routes

from flask import Blueprint, request, jsonify
from models import BorrowRecord, Book, User
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

borrows_bp = Blueprint('borrows', __name__)

@borrows_bp.route('/api/borrows', methods=['POST', 'OPTIONS'])
def create_borrow_request():
    """Create a borrow request - 简化版本"""
    # 处理CORS预检请求
    if request.method == 'OPTIONS':
        print("处理CORS预检请求")
        from flask import make_response
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response
    
    print("\n=== 借阅请求开始 ===")
    print(f"请求方法: {request.method}")
    print(f"请求头: {dict(request.headers)}")
    
    # 检查Authorization头
    auth_header = request.headers.get('Authorization')
    print(f"Authorization头: {auth_header}")
    
    if not auth_header:
        print("ERROR: 缺少Authorization头")
        return jsonify({
            'success': False,
            'message': 'Authorization token required'
        }), 401
    
    if not auth_header.startswith('Bearer '):
        print("ERROR: Authorization头格式错误")
        return jsonify({
            'success': False,
            'message': 'Invalid authorization format'
        }), 401
    
    # 现在使用JWT装饰器
    from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
    try:
        verify_jwt_in_request()
        current_user_id_str = get_jwt_identity()
        current_user_id = int(current_user_id_str)  # 转换回整数
        print(f"JWT验证成功，当前用户ID: {current_user_id} (类型: {type(current_user_id)})")
    except Exception as jwt_error:
        print(f"JWT验证失败: {jwt_error}")
        return jsonify({
            'success': False,
            'message': f'JWT verification failed: {str(jwt_error)}'
        }), 401
    
    try:
        # 获取请求数据
        data = request.get_json()
        print(f"请求数据: {data}")
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        book_id = data.get('book_id')
        if not book_id:
            return jsonify({
                'success': False,
                'message': '图书ID不能为空'
            }), 400
        
        print(f"图书ID: {book_id}")
        
        # 验证图书是否存在
        book = Book.find_by_id(book_id)
        if not book:
            return jsonify({
                'success': False,
                'message': '图书不存在'
            }), 404
        
        # 检查库存
        if book.get('stock', 0) <= 0:
            return jsonify({
                'success': False,
                'message': '图书库存不足'
            }), 400
        
        # 检查是否已经借阅过
        try:
            existing = BorrowRecord.find_active_borrow(current_user_id, book_id)
            if existing:
                return jsonify({
                    'success': False,
                    'message': '您已经借阅过这本书'
                }), 400
        except Exception as e:
            print(f"检查现有借阅记录失败: {e}")
            # 继续执行
        
        # 创建借阅记录
        borrow_id = BorrowRecord.create(
            user_id=current_user_id,
            book_id=book_id,
            borrow_status="requested"
        )
        
        if borrow_id:
            print(f"成功创建借阅记录: {borrow_id}")
            return jsonify({
                'success': True,
                'message': '借阅请求提交成功',
                'data': {'borrow_id': borrow_id}
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': '创建借阅记录失败'
            }), 500
            
    except Exception as e:
        print(f"借阅请求异常: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500

@borrows_bp.route('/api/borrows/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_borrows(user_id):
    """Get borrowing history for a user"""
    try:
        # Check if user exists
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User does not exist'
            }), 404
        
        # Get borrowing records
        borrows = BorrowRecord.get_by_user(user_id)
        
        return jsonify({
            'success': True,
            'data': borrows,
            'message': 'Successfully retrieved borrowing history'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve borrowing history: {str(e)}'
        }), 500

@borrows_bp.route('/api/borrows', methods=['GET'])
@jwt_required()
def get_all_borrows():
    """Get all borrow records (admin use)"""
    try:
        # 从 query string 获取 borrow_status
        borrow_status = request.args.get('borrow_status')  # 前端传 ?borrow_status=requested
        borrows = BorrowRecord.get_all(borrow_status=borrow_status)
        
        return jsonify({
            'success': True,
            'data': borrows,
            'message': 'Successfully retrieved borrow records'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve borrow records: {str(e)}'
        }), 500


@borrows_bp.route('/api/borrows/<int:record_id>/borrow_status', methods=['PUT'])
@jwt_required()
def update_borrow_status(record_id):
    """Update borrow status (admin use)"""
    try:
        data = request.get_json()
        
        # Validate required field
        if 'borrow_status' not in data:
            return jsonify({
                'success': False,
                'message': 'Missing required field: borrow_status'
            }), 400
        
        # Check if record exists
        record = BorrowRecord.find_by_id(record_id)
        if not record:
            return jsonify({
                'success': False,
                'message': 'Borrow record not found'
            }), 404
        
        borrow_status = data['borrow_status']  # 改成 borrow_status
        return_date = None
        
        # If changing to 'borrowed', reduce stock
        if borrow_status == 'borrowed' and record['borrow_status'] == 'requested':
            Book.update_stock(record['book_id'], -1)
        
        # If changing to 'returned', increase stock and set return date
        elif borrow_status == 'returned' and record['borrow_status'] == 'borrowed':
            Book.update_stock(record['book_id'], 1)
            return_date = datetime.now()
        
        # Update borrow status
        result = BorrowRecord.update_status(record_id, borrow_status, return_date)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Borrow status updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update borrow status'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to update borrow status: {str(e)}'
        }), 500

@borrows_bp.route('/api/borrows/<int:record_id>/return', methods=['PUT'])
@jwt_required()
def return_book(record_id):
    """User returns a borrowed book"""
    try:
        current_user_id_str = get_jwt_identity()
        current_user_id = int(current_user_id_str)
        
        # Check if record exists
        record = BorrowRecord.find_by_id(record_id)
        if not record:
            return jsonify({
                'success': False,
                'message': 'Borrow record not found'
            }), 404
        
        # Check if the user owns this borrow record
        if record['user_id'] != current_user_id:
            return jsonify({
                'success': False,
                'message': 'You can only return your own borrowed books'
            }), 403
        
        # Check if the book is currently borrowed
        if record['borrow_status'] != 'borrowed':
            return jsonify({
                'success': False,
                'message': 'This book is not currently borrowed'
            }), 400
        
        # Update the record to returned status
        return_date = datetime.now()
        result = BorrowRecord.update_status(record_id, 'returned', return_date)
        
        if result:
            # Increase the book stock
            Book.update_stock(record['book_id'], 1)
            
            return jsonify({
                'success': True,
                'message': 'Book returned successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to return book'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to return book: {str(e)}'
        }), 500

@borrows_bp.route('/api/borrows/<int:record_id>', methods=['GET'])
def get_borrow_record(record_id):
    """Get details of a single borrow record"""
    try:
        record = BorrowRecord.find_by_id(record_id)
        
        if not record:
            return jsonify({
                'success': False,
                'message': 'Borrow record not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': record,
            'message': 'Successfully retrieved borrow record'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve borrow record: {str(e)}'
        }), 500
