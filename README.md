# 📚 TiDB 기반 도서관리시스템 (Bookstore Management System)

TiDB Cloud Serverless 데이터베이스의 서점 데이터(고객, 도서, 주문)를 기반으로 구축된 **반응형 Flask 웹서비스**입니다.  
GitHub와 Render Cloud를 연동하여 PC를 꺼두어도 24시간 스마트폰과 외부 기기에서 언제 어디서나 접속 및 데이터 관리(CRUD, 복합 조인 검색)가 가능합니다.

---

## 🌟 주요 기능 및 특징

1. **전체 데이터 CRUD (추가·조회·수정·삭제)**
   - **고객 관리 (`고객` 테이블)**: 고객번호, 고객명, 주소, 연락처 검색 및 등록/수정/삭제
   - **도서 관리 (`도서` 테이블)**: 도서번호, 도서명, 출판사, 정가 검색 및 등록/수정/삭제
   - **주문 관리 (`주문` 테이블)**: 고객 및 도서 드롭다운 선택, 판매가 자동 입력, 주문일자 지정 및 등록/수정/삭제
   - **안전한 데이터 관리**: 삭제 시 브라우저 2차 확인 절차(`confirm`) 및 외래키(FK) 무결성 예외 처리 완비

2. **테이블 조인 통합 검색 및 통계**
   - 고객 + 도서 + 주문 3개 테이블을 결합한 실시간 조인 내역 조회
   - 고객별 총 주문금액 및 구매건수 VIP 통계
   - 도서별 판매 실적 및 베스트셀러 순위 분석
   - 미판매 도서 목록 및 출판사별 출간 현황 집계

3. **반응형 대시보드 UI (Bootstrap 5)**
   - PC 모니터부터 스마트폰, 태블릿까지 최적화된 반응형 인터페이스
   - 페이지 새로고침 없는 비동기(Fetch API) 처리 및 실시간 검색 필터

4. **📱 모바일 접속 QR코드**
   - 네비게이션 바의 **`📱 모바일 접속 QR`** 버튼 클릭 시, 현재 접속된 공개 URL의 QR코드를 자동 생성하여 모달로 출력
   - 스마트폰 카메라로 스캔하여 즉시 모바일 화면으로 접속 가능

---

## 📁 프로젝트 파일 구조

```
flask_bookstore/
├── app.py                # Flask 메인 애플리케이션 (REST API 및 웹 라우팅)
├── db.py                 # TiDB Cloud TLS 암호화 연결 및 CRUD/조인 쿼리 모듈
├── requirements.txt      # 의존성 패키지 목록 (Flask, PyMySQL, Gunicorn, cryptography 등)
├── Procfile              # Render 배포용 WSGI 서버 실행 명세 (web: gunicorn app:app)
├── .gitignore            # Git 제외 설정
├── README.md             # 배포 및 실행 가이드 문서
└── templates/
    └── index.html        # 반응형 단일 페이지 대시보드 템플릿
```

---

## 💻 1. 로컬 환경에서 테스트 및 실행 방법

### 1) 의존성 패키지 설치
터미널(PowerShell 또는 CMD)에서 해당 디렉터리로 이동 후 다음 명령어를 실행합니다:
```bash
cd C:\DB-2026\TiDB웹서비스\flask_bookstore
pip install -r requirements.txt
```

### 2) Flask 서버 로컬 실행
```bash
python app.py
```

### 3) 웹 브라우저 접속
- 주소: `http://localhost:5000`
- 정상 접속 시 상단에 `TiDB Cloud (서점데이터베이스) 연결됨` 초록색 뱃지가 표시됩니다.

---

## 🚀 2. GitHub 업로드 및 Render Cloud 배포 단계별 안내

### 1단계: GitHub 저장소(Repository) 생성
1. [GitHub](https://github.com/)에 로그인합니다.
2. 우측 상단의 `+` 버튼을 누르고 **`New repository`**를 클릭합니다.
3. 설정 입력:
   - **Repository name**: `flask-bookstore` (또는 원하는 이름)
   - **Public** 선택
   - *Initialize this repository with... (README, .gitignore 등) 체크박스는 모두 해제합니다.* (이미 로컬에 파일이 준비되어 있습니다)
4. **`Create repository`** 버튼을 클릭합니다.
5. 생성 후 화면에 나타나는 저장소 주소(예: `https://github.com/<사용자ID>/flask-bookstore.git`)를 복사해 둡니다.

---

### 2단계: 로컬 코드를 GitHub에 Push
터미널에서 `flask_bookstore` 디렉터리로 이동한 후 다음 명령어를 순서대로 입력합니다:

```bash
cd C:\DB-2026\TiDB웹서비스\flask_bookstore

# 1. Git 저장소 초기화
git init

# 2. 파일 추가 및 첫 커밋
git add .
git commit -m "feat: TiDB 기반 도서관리 웹서비스 구축"

# 3. 브랜치 이름을 main으로 변경
git branch -M main

# 4. GitHub 원격 저장소 연결 (본인의 GitHub 저장소 URL로 변경)
git remote add origin https://github.com/<본인-GitHub-아이디>/flask-bookstore.git

# 5. GitHub로 코드 푸시
git push -u origin main
```

---

### 3단계: Render Cloud에 배포하기
1. [Render.com](https://render.com/)에 접속하여 회원가입 또는 로그인합니다. (GitHub 계정으로 간편 로그인 권장)
2. 대시보드 상단의 **`New +`** 버튼 클릭 ➡️ **`Web Service`**를 선택합니다.
3. **`Build and deploy from a Git repository`** 선택 ➡️ Next 클릭.
4. 방금 올린 `flask-bookstore` 리포지토리를 찾아 **`Connect`**를 클릭합니다.  
   *(저장소가 안 보이면 `Configure account`를 눌러 저장소 접근 권한을 부여합니다)*
5. 배포 설정을 다음과 같이 입력합니다:
   - **Name**: `bookstore-service` (원하는 서비스 명칭 입력)
   - **Region**: `Singapore (Southeast Asia)` 또는 `Oregon` (아시아 권장)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`
6. **Environment Variables (환경 변수)** 설정:
   - 하단의 `Environment Variables` 섹션에서 `Add Environment Variable` 클릭 후 아래 값들을 추가합니다:
     | Key | Value |
     | :--- | :--- |
     | `TIDB_HOST` | `gateway01.ap-northeast-1.prod.aws.tidbcloud.com` |
     | `TIDB_PORT` | `4000` |
     | `TIDB_USER` | `3r67Jehnt5APwkA.root` |
     | `TIDB_PASSWORD` | `vvtv8gilTEchbjzg` |
     | `TIDB_DATABASE` | `서점데이터베이스` |
7. 하단의 **`Deploy Web Service`** 버튼을 클릭합니다.

---

### 4단계: 배포 완료 및 공개 URL 확인
1. 빌드 및 배포 로그가 실시간으로 흘러가며, 약 2~3분 후 **`Live`** 상태로 바뀝니다.
2. 상단에 부여된 고유 URL(예: `https://bookstore-service.onrender.com`)을 클릭하여 접속합니다.
3. 이제 **개인 PC를 종료하더라도 스마트폰이나 다른 컴퓨터에서 해당 URL로 24시간 접속하여 TiDB 서점 데이터를 조회하고 CRUD 관리**를 진행할 수 있습니다!
4. 상단 네비게이션 바의 **`📱 모바일 접속 QR`** 버튼을 누르면 해당 Render 공개 주소의 QR 코드가 즉시 출력되어, 스마트폰으로 쉽게 스캔할 수 있습니다.
