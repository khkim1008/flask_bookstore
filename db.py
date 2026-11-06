import os
import pymysql
from pymysql.cursors import DictCursor

# TiDB Cloud Connection Configuration
DB_CONFIG = {
    'host': os.environ.get('TIDB_HOST', 'gateway01.ap-northeast-1.prod.aws.tidbcloud.com'),
    'port': int(os.environ.get('TIDB_PORT', 4000)),
    'user': os.environ.get('TIDB_USER', '3r67Jehnt5APwkA.root'),
    'password': os.environ.get('TIDB_PASSWORD', 'vvtv8gilTEchbjzg'),
    'database': os.environ.get('TIDB_DATABASE', '서점데이터베이스'),
    'charset': 'utf8mb4',
    'ssl': {'ssl': True},
    'cursorclass': DictCursor,
    'autocommit': True,
    'connect_timeout': 10
}

TABLE_PRIMARY_KEYS = {
    '고객': 'custid',
    '도서': 'bookid',
    '주문': 'orderid'
}

def get_connection():
    """Create and return a new connection to TiDB Cloud."""
    return pymysql.connect(**DB_CONFIG)

def test_connection():
    """Verify TiDB Cloud connectivity and return database info."""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT DATABASE() AS db, VERSION() AS ver, NOW() AS now;")
            info = cur.fetchone()
        conn.close()
        return {'status': 'success', 'data': info}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def get_next_id(table_name):
    """Calculate the next integer primary key for tables without AUTO_INCREMENT."""
    pk = TABLE_PRIMARY_KEYS.get(table_name)
    if not pk:
        return 1
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT IFNULL(MAX(`{pk}`), 0) + 1 AS next_id FROM `{table_name}`;")
            res = cur.fetchone()
            return res['next_id'] if res else 1
    finally:
        conn.close()

# ----------------- 고객 (Customer) CRUD -----------------
def get_customers(search_field=None, search_keyword=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT custid, name, address, phone FROM `고객`"
            params = []
            if search_keyword and search_keyword.strip():
                kw = f"%{search_keyword.strip()}%"
                if search_field == 'name':
                    query += " WHERE name LIKE %s"
                    params.append(kw)
                elif search_field == 'address':
                    query += " WHERE address LIKE %s"
                    params.append(kw)
                elif search_field == 'phone':
                    query += " WHERE phone LIKE %s"
                    params.append(kw)
                elif search_field == 'custid':
                    query += " WHERE CAST(custid AS CHAR) LIKE %s"
                    params.append(kw)
                else:
                    query += " WHERE name LIKE %s OR address LIKE %s OR phone LIKE %s OR CAST(custid AS CHAR) LIKE %s"
                    params.extend([kw, kw, kw, kw])
            query += " ORDER BY custid ASC;"
            cur.execute(query, params)
            return cur.fetchall()
    finally:
        conn.close()

def get_customer(custid):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT custid, name, address, phone FROM `고객` WHERE custid = %s;", (custid,))
            return cur.fetchone()
    finally:
        conn.close()

def add_customer(custid, name, address, phone):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if not custid:
                custid = get_next_id('고객')
            cur.execute(
                "INSERT INTO `고객` (custid, name, address, phone) VALUES (%s, %s, %s, %s);",
                (custid, name.strip(), address.strip() if address else None, phone.strip() if phone else None)
            )
            return custid
    finally:
        conn.close()

def update_customer(custid, name, address, phone):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE `고객` SET name = %s, address = %s, phone = %s WHERE custid = %s;",
                (name.strip(), address.strip() if address else None, phone.strip() if phone else None, custid)
            )
            return cur.rowcount > 0
    finally:
        conn.close()

def delete_customer(custid):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Check if referenced in orders
            cur.execute("SELECT COUNT(*) AS cnt FROM `주문` WHERE custid = %s;", (custid,))
            cnt = cur.fetchone()['cnt']
            if cnt > 0:
                raise ValueError(f"해당 고객(ID: {custid})과 연관된 주문 내역이 {cnt}건 존재하여 삭제할 수 없습니다. 관련 주문을 먼저 삭제해주세요.")
            cur.execute("DELETE FROM `고객` WHERE custid = %s;", (custid,))
            return cur.rowcount > 0
    finally:
        conn.close()

# ----------------- 도서 (Book) CRUD -----------------
def get_books(search_field=None, search_keyword=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT bookid, bookname, publisher, price FROM `도서`"
            params = []
            if search_keyword and search_keyword.strip():
                kw = f"%{search_keyword.strip()}%"
                if search_field == 'bookname':
                    query += " WHERE bookname LIKE %s"
                    params.append(kw)
                elif search_field == 'publisher':
                    query += " WHERE publisher LIKE %s"
                    params.append(kw)
                elif search_field == 'bookid':
                    query += " WHERE CAST(bookid AS CHAR) LIKE %s"
                    params.append(kw)
                else:
                    query += " WHERE bookname LIKE %s OR publisher LIKE %s OR CAST(bookid AS CHAR) LIKE %s"
                    params.extend([kw, kw, kw])
            query += " ORDER BY bookid ASC;"
            cur.execute(query, params)
            return cur.fetchall()
    finally:
        conn.close()

def get_book(bookid):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT bookid, bookname, publisher, price FROM `도서` WHERE bookid = %s;", (bookid,))
            return cur.fetchone()
    finally:
        conn.close()

def add_book(bookid, bookname, publisher, price):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if not bookid:
                bookid = get_next_id('도서')
            cur.execute(
                "INSERT INTO `도서` (bookid, bookname, publisher, price) VALUES (%s, %s, %s, %s);",
                (bookid, bookname.strip(), publisher.strip() if publisher else None, int(price) if price is not None and str(price).strip() != '' else 0)
            )
            return bookid
    finally:
        conn.close()

def update_book(bookid, bookname, publisher, price):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE `도서` SET bookname = %s, publisher = %s, price = %s WHERE bookid = %s;",
                (bookname.strip(), publisher.strip() if publisher else None, int(price) if price is not None and str(price).strip() != '' else 0, bookid)
            )
            return cur.rowcount > 0
    finally:
        conn.close()

def delete_book(bookid):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Check if referenced in orders
            cur.execute("SELECT COUNT(*) AS cnt FROM `주문` WHERE bookid = %s;", (bookid,))
            cnt = cur.fetchone()['cnt']
            if cnt > 0:
                raise ValueError(f"해당 도서(ID: {bookid})와 연관된 주문 내역이 {cnt}건 존재하여 삭제할 수 없습니다. 관련 주문을 먼저 삭제해주세요.")
            cur.execute("DELETE FROM `도서` WHERE bookid = %s;", (bookid,))
            return cur.rowcount > 0
    finally:
        conn.close()

# ----------------- 주문 (Order) CRUD -----------------
def get_orders(search_field=None, search_keyword=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = """
            SELECT 
                o.orderid,
                o.custid,
                c.name AS customer_name,
                o.bookid,
                b.bookname,
                b.price AS book_price,
                o.saleprice,
                DATE_FORMAT(o.orderdate, '%%Y-%%m-%%d') AS orderdate
            FROM `주문` o
            LEFT JOIN `고객` c ON o.custid = c.custid
            LEFT JOIN `도서` b ON o.bookid = b.bookid
            """
            params = []
            if search_keyword and search_keyword.strip():
                kw = f"%{search_keyword.strip()}%"
                if search_field == 'customer_name':
                    query += " WHERE c.name LIKE %s"
                    params.append(kw)
                elif search_field == 'bookname':
                    query += " WHERE b.bookname LIKE %s"
                    params.append(kw)
                elif search_field == 'orderid':
                    query += " WHERE CAST(o.orderid AS CHAR) LIKE %s"
                    params.append(kw)
                elif search_field == 'orderdate':
                    query += " WHERE DATE_FORMAT(o.orderdate, '%%Y-%%m-%%d') LIKE %s"
                    params.append(kw)
                else:
                    query += " WHERE c.name LIKE %s OR b.bookname LIKE %s OR CAST(o.orderid AS CHAR) LIKE %s OR DATE_FORMAT(o.orderdate, '%%Y-%%m-%%d') LIKE %s"
                    params.extend([kw, kw, kw, kw])
            query += " ORDER BY o.orderid DESC;"
            cur.execute(query, params)
            return cur.fetchall()
    finally:
        conn.close()

def get_order(orderid):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = """
            SELECT 
                o.orderid,
                o.custid,
                c.name AS customer_name,
                o.bookid,
                b.bookname,
                o.saleprice,
                DATE_FORMAT(o.orderdate, '%%Y-%%m-%%d') AS orderdate
            FROM `주문` o
            LEFT JOIN `고객` c ON o.custid = c.custid
            LEFT JOIN `도서` b ON o.bookid = b.bookid
            WHERE o.orderid = %s;
            """
            cur.execute(query, (orderid,))
            return cur.fetchone()
    finally:
        conn.close()

def add_order(orderid, custid, bookid, saleprice, orderdate):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if not orderid:
                orderid = get_next_id('주문')
            cur.execute(
                "INSERT INTO `주문` (orderid, custid, bookid, saleprice, orderdate) VALUES (%s, %s, %s, %s, %s);",
                (orderid, int(custid), int(bookid), int(saleprice), orderdate)
            )
            return orderid
    finally:
        conn.close()

def update_order(orderid, custid, bookid, saleprice, orderdate):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE `주문` SET custid = %s, bookid = %s, saleprice = %s, orderdate = %s WHERE orderid = %s;",
                (int(custid), int(bookid), int(saleprice), orderdate, orderid)
            )
            return cur.rowcount > 0
    finally:
        conn.close()

def delete_order(orderid):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM `주문` WHERE orderid = %s;", (orderid,))
            return cur.rowcount > 0
    finally:
        conn.close()

# ----------------- 조인 및 통계 검색 -----------------
PRESET_JOINS = [
    {
        'id': 'orders_full',
        'title': '고객별 도서 주문 전체 내역 (고객 + 도서 + 주문 조인)',
        'description': '고객(이름, 연락처), 도서(도서명, 정가), 주문(판매가, 할인액, 주문일자)의 전체 거래 내역을 결합하여 확인합니다.',
        'sql': """SELECT 
    o.orderid AS '주문번호',
    c.name AS '고객명',
    c.phone AS '연락처',
    b.bookname AS '도서명',
    b.price AS '정가(원)',
    o.saleprice AS '판매가(원)',
    (b.price - o.saleprice) AS '할인금액(원)',
    DATE_FORMAT(o.orderdate, '%Y-%m-%d') AS '주문일자'
FROM `주문` o
JOIN `고객` c ON o.custid = c.custid
JOIN `도서` b ON o.bookid = b.bookid
ORDER BY o.orderid ASC;"""
    },
    {
        'id': 'customer_stats',
        'title': '고객별 총 주문금액 및 구매건수 통계',
        'description': '고객별 총 구매액과 주문 건수를 집계하고, 총 구매금액 순으로 정렬합니다.',
        'sql': """SELECT 
    c.custid AS '고객번호',
    c.name AS '고객명',
    c.address AS '주소',
    c.phone AS '연락처',
    COUNT(o.orderid) AS '총주문건수',
    IFNULL(SUM(o.saleprice), 0) AS '총구매금액(원)',
    ROUND(IFNULL(AVG(o.saleprice), 0)) AS '평균구매금액(원)'
FROM `고객` c
LEFT JOIN `주문` o ON c.custid = o.custid
GROUP BY c.custid, c.name, c.address, c.phone
ORDER BY `총구매금액(원)` DESC;"""
    },
    {
        'id': 'bestsellers',
        'title': '도서별 판매 실적 및 베스트셀러 순위',
        'description': '판매 수량과 누적 매출액을 기준으로 어떤 도서가 인기 있는지 파악합니다.',
        'sql': """SELECT 
    b.bookid AS '도서번호',
    b.bookname AS '도서명',
    b.publisher AS '출판사',
    b.price AS '정가(원)',
    COUNT(o.orderid) AS '판매부수',
    IFNULL(SUM(o.saleprice), 0) AS '총매출액(원)'
FROM `도서` b
LEFT JOIN `주문` o ON b.bookid = o.bookid
GROUP BY b.bookid, b.bookname, b.publisher, b.price
ORDER BY `판매부수` DESC, `총매출액(원)` DESC;"""
    },
    {
        'id': 'books_never_ordered',
        'title': '주문된 적 없는 미판매 도서 목록',
        'description': '현재까지 한 번도 주문되지 않은 도서 목록을 필터링합니다.',
        'sql': """SELECT 
    b.bookid AS '도서번호',
    b.bookname AS '도서명',
    b.publisher AS '출판사',
    b.price AS '정가(원)'
FROM `도서` b
LEFT JOIN `주문` o ON b.bookid = o.bookid
WHERE o.orderid IS NULL
ORDER BY b.bookid ASC;"""
    },
    {
        'id': 'publisher_stats',
        'title': '출판사별 출간 도서 수 및 평균 가격',
        'description': '출판사별 보유 도서 수 및 평균 정가를 집계합니다.',
        'sql': """SELECT 
    b.publisher AS '출판사',
    COUNT(b.bookid) AS '등록도서수',
    ROUND(AVG(b.price)) AS '평균도서가격(원)'
FROM `도서` b
GROUP BY b.publisher
ORDER BY `등록도서수` DESC;"""
    }
]

def execute_preset_join(preset_id, search_keyword=None):
    preset = next((p for p in PRESET_JOINS if p['id'] == preset_id), None)
    if not preset:
        raise ValueError("알 수 없는 조인 쿼리입니다.")
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # If user provided a search keyword for the join view, filter the results or run base sql
            sql = preset['sql']
            cur.execute(sql)
            rows = cur.fetchall()
            
            # In-memory filter for flexible cross-column keyword search if provided
            if search_keyword and search_keyword.strip():
                kw = search_keyword.strip().lower()
                filtered = []
                for row in rows:
                    if any(kw in str(val).lower() for val in row.values() if val is not None):
                        filtered.append(row)
                rows = filtered
            
            return {
                'title': preset['title'],
                'description': preset['description'],
                'data': rows
            }
    finally:
        conn.close()
