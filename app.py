import os
import io
import base64
from flask import Flask, render_template, request, jsonify, send_file
import qrcode
import db

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def api_status():
    result = db.test_connection()
    return jsonify(result)

# ----------------- 고객 (Customer) APIs -----------------
@app.route('/api/customers', methods=['GET'])
def get_customers():
    try:
        search_field = request.args.get('search_field')
        search_keyword = request.args.get('search_keyword')
        customers = db.get_customers(search_field, search_keyword)
        return jsonify({'status': 'success', 'data': customers, 'count': len(customers)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/customers/<int:custid>', methods=['GET'])
def get_customer(custid):
    try:
        customer = db.get_customer(custid)
        if not customer:
            return jsonify({'status': 'error', 'message': '고객 정보를 찾을 수 없습니다.'}), 404
        return jsonify({'status': 'success', 'data': customer})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/customers/next-id', methods=['GET'])
def get_next_customer_id():
    try:
        next_id = db.get_next_id('고객')
        return jsonify({'status': 'success', 'next_id': next_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/customers', methods=['POST'])
def add_customer():
    try:
        data = request.get_json(force=True)
        name = data.get('name')
        if not name or not name.strip():
            return jsonify({'status': 'error', 'message': '고객 이름은 필수 입력 항목입니다.'}), 400
        
        custid = data.get('custid')
        if custid:
            try:
                custid = int(custid)
            except ValueError:
                return jsonify({'status': 'error', 'message': '고객번호는 정수여야 합니다.'}), 400
        
        new_id = db.add_customer(custid, name, data.get('address'), data.get('phone'))
        return jsonify({'status': 'success', 'message': f'고객(번호: {new_id})이 등록되었습니다.', 'custid': new_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/customers/<int:custid>', methods=['PUT'])
def update_customer(custid):
    try:
        data = request.get_json(force=True)
        name = data.get('name')
        if not name or not name.strip():
            return jsonify({'status': 'error', 'message': '고객 이름은 필수 입력 항목입니다.'}), 400
        
        success = db.update_customer(custid, name, data.get('address'), data.get('phone'))
        if success:
            return jsonify({'status': 'success', 'message': f'고객(번호: {custid}) 정보가 수정되었습니다.'})
        return jsonify({'status': 'error', 'message': '수정할 고객을 찾을 수 없습니다.'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/customers/<int:custid>', methods=['DELETE'])
def delete_customer(custid):
    try:
        success = db.delete_customer(custid)
        if success:
            return jsonify({'status': 'success', 'message': f'고객(번호: {custid})이 삭제되었습니다.'})
        return jsonify({'status': 'error', 'message': '삭제할 고객을 찾을 수 없습니다.'}), 404
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ----------------- 도서 (Book) APIs -----------------
@app.route('/api/books', methods=['GET'])
def get_books():
    try:
        search_field = request.args.get('search_field')
        search_keyword = request.args.get('search_keyword')
        books = db.get_books(search_field, search_keyword)
        return jsonify({'status': 'success', 'data': books, 'count': len(books)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/books/<int:bookid>', methods=['GET'])
def get_book(bookid):
    try:
        book = db.get_book(bookid)
        if not book:
            return jsonify({'status': 'error', 'message': '도서 정보를 찾을 수 없습니다.'}), 404
        return jsonify({'status': 'success', 'data': book})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/books/next-id', methods=['GET'])
def get_next_book_id():
    try:
        next_id = db.get_next_id('도서')
        return jsonify({'status': 'success', 'next_id': next_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/books', methods=['POST'])
def add_book():
    try:
        data = request.get_json(force=True)
        bookname = data.get('bookname')
        if not bookname or not bookname.strip():
            return jsonify({'status': 'error', 'message': '도서명은 필수 입력 항목입니다.'}), 400
        
        bookid = data.get('bookid')
        if bookid:
            try:
                bookid = int(bookid)
            except ValueError:
                return jsonify({'status': 'error', 'message': '도서번호는 정수여야 합니다.'}), 400
        
        new_id = db.add_book(bookid, bookname, data.get('publisher'), data.get('price'))
        return jsonify({'status': 'success', 'message': f'도서(번호: {new_id})가 등록되었습니다.', 'bookid': new_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/books/<int:bookid>', methods=['PUT'])
def update_book(bookid):
    try:
        data = request.get_json(force=True)
        bookname = data.get('bookname')
        if not bookname or not bookname.strip():
            return jsonify({'status': 'error', 'message': '도서명은 필수 입력 항목입니다.'}), 400
        
        success = db.update_book(bookid, bookname, data.get('publisher'), data.get('price'))
        if success:
            return jsonify({'status': 'success', 'message': f'도서(번호: {bookid}) 정보가 수정되었습니다.'})
        return jsonify({'status': 'error', 'message': '수정할 도서를 찾을 수 없습니다.'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/books/<int:bookid>', methods=['DELETE'])
def delete_book(bookid):
    try:
        success = db.delete_book(bookid)
        if success:
            return jsonify({'status': 'success', 'message': f'도서(번호: {bookid})가 삭제되었습니다.'})
        return jsonify({'status': 'error', 'message': '삭제할 도서를 찾을 수 없습니다.'}), 404
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ----------------- 주문 (Order) APIs -----------------
@app.route('/api/orders', methods=['GET'])
def get_orders():
    try:
        search_field = request.args.get('search_field')
        search_keyword = request.args.get('search_keyword')
        orders = db.get_orders(search_field, search_keyword)
        return jsonify({'status': 'success', 'data': orders, 'count': len(orders)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/orders/<int:orderid>', methods=['GET'])
def get_order(orderid):
    try:
        order = db.get_order(orderid)
        if not order:
            return jsonify({'status': 'error', 'message': '주문 정보를 찾을 수 없습니다.'}), 404
        return jsonify({'status': 'success', 'data': order})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/orders/next-id', methods=['GET'])
def get_next_order_id():
    try:
        next_id = db.get_next_id('주문')
        return jsonify({'status': 'success', 'next_id': next_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/orders', methods=['POST'])
def add_order():
    try:
        data = request.get_json(force=True)
        custid = data.get('custid')
        bookid = data.get('bookid')
        saleprice = data.get('saleprice')
        orderdate = data.get('orderdate')

        if not custid or not bookid or saleprice is None or not orderdate:
            return jsonify({'status': 'error', 'message': '고객, 도서, 판매가, 주문일자는 필수 항목입니다.'}), 400

        orderid = data.get('orderid')
        if orderid:
            try:
                orderid = int(orderid)
            except ValueError:
                return jsonify({'status': 'error', 'message': '주문번호는 정수여야 합니다.'}), 400

        new_id = db.add_order(orderid, custid, bookid, saleprice, orderdate)
        return jsonify({'status': 'success', 'message': f'주문(번호: {new_id})이 등록되었습니다.', 'orderid': new_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/orders/<int:orderid>', methods=['PUT'])
def update_order(orderid):
    try:
        data = request.get_json(force=True)
        custid = data.get('custid')
        bookid = data.get('bookid')
        saleprice = data.get('saleprice')
        orderdate = data.get('orderdate')

        if not custid or not bookid or saleprice is None or not orderdate:
            return jsonify({'status': 'error', 'message': '고객, 도서, 판매가, 주문일자는 필수 항목입니다.'}), 400

        success = db.update_order(orderid, custid, bookid, saleprice, orderdate)
        if success:
            return jsonify({'status': 'success', 'message': f'주문(번호: {orderid}) 정보가 수정되었습니다.'})
        return jsonify({'status': 'error', 'message': '수정할 주문을 찾을 수 없습니다.'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/orders/<int:orderid>', methods=['DELETE'])
def delete_order(orderid):
    try:
        success = db.delete_order(orderid)
        if success:
            return jsonify({'status': 'success', 'message': f'주문(번호: {orderid})이 삭제되었습니다.'})
        return jsonify({'status': 'error', 'message': '삭제할 주문을 찾을 수 없습니다.'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ----------------- 헬퍼 (드롭다운 데이터) -----------------
@app.route('/api/helpers/dropdowns', methods=['GET'])
def get_dropdowns():
    try:
        customers = db.get_customers()
        books = db.get_books()
        return jsonify({
            'status': 'success',
            'customers': [{'custid': c['custid'], 'name': c['name'], 'phone': c['phone']} for c in customers],
            'books': [{'bookid': b['bookid'], 'bookname': b['bookname'], 'price': b['price'], 'publisher': b['publisher']} for b in books]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ----------------- 복합 조인 & 통계 -----------------
@app.route('/api/joins', methods=['GET'])
def get_preset_joins():
    presets = [{'id': p['id'], 'title': p['title'], 'description': p['description']} for p in db.PRESET_JOINS]
    return jsonify({'status': 'success', 'presets': presets})

@app.route('/api/joins/<preset_id>', methods=['GET'])
def execute_preset_join(preset_id):
    try:
        search_keyword = request.args.get('search_keyword')
        result = db.execute_preset_join(preset_id, search_keyword)
        return jsonify({
            'status': 'success',
            'preset_id': preset_id,
            'title': result['title'],
            'description': result['description'],
            'data': result['data'],
            'count': len(result['data'])
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ----------------- QR 코드 생성 API -----------------
@app.route('/api/qrcode', methods=['GET'])
def get_qrcode():
    target_url = request.args.get('url')
    if not target_url:
        target_url = os.environ.get('RENDER_EXTERNAL_URL') or request.host_url
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2
    )
    qr.add_data(target_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    as_base64 = request.args.get('base64', 'false').lower() == 'true'
    if as_base64:
        b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode('utf-8')
        return jsonify({'status': 'success', 'url': target_url, 'qrcode': b64})
    
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f" * Starting Flask Bookstore on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
