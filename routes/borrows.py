# Borrow Management Routes

from flask import Blueprint, request, jsonify
from models import BorrowRecord, Book, User
from datetime import datetime

borrows_bp = Blueprint('borrows', __name__)

@borrows_bp.route('/api/borrows', methods=['POST'])
def create_borrow_request():
    """Create a borrow request"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'book_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Check if user exists
        user = User.find_by_id(data['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'message': 'User does not exist'
            }), 404
        
        # Check if book exists
        book = Book.find_by_id(data['book_id'])
        if not book:
            return jsonify({
                'success': False,
                'message': 'Book does not exist'
            }), 404
        
        # Check stock
        if book['stock'] <= 0:
            return jsonify({
                'success': False,
                'message': 'Book is out of stock'
            }), 400
        
        # Create borrow request
        result = BorrowRecord.create(
            user_id=data['user_id'],
            book_id=data['book_id'],
            status='requested',
            borrow_date=data['borrow_date']
        )
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Borrow request submitted successfully'
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to submit borrow request'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to submit borrow request: {str(e)}'
        }), 500

@borrows_bp.route('/api/borrows/user/<int:user_id>', methods=['GET'])
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


@borrows_bp.route('/api/borrows/<int:record_id>/status', methods=['PUT'])
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

