# Flask Blog

Flask 기반 블로그 서비스입니다. TDD(Test-Driven Development) 방식으로 개발되었습니다.

## 기능

- **글 목록**: 전체 글 리스트 조회, 카테고리별 필터링
- **글 작성/수정/삭제**: 블로그 글 CRUD
- **글 상세보기**: 개별 글 전체 내용 조회
- **통계 대시보드**: 전체 글 수, 카테고리별, 월별 통계

## 기술 스택

- Python / Flask
- SQLite
- HTML / CSS (Jinja2 템플릿)
- pytest (테스트)
- GitHub Actions (CI/CD)
- Docker / GHCR (배포)

## 설치 및 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python app.py
```

http://localhost:5000 에서 확인할 수 있습니다.

## 테스트

```bash
pytest tests/ -v
```

## Docker

```bash
# 빌드
docker build -t flask-blog .

# 실행
docker run -p 5000:5000 flask-blog
```

## 프로젝트 구조

```
flask-blog/
├── app.py              # Flask 라우트
├── models.py           # DB 모델/함수
├── templates/          # Jinja2 템플릿
├── static/             # CSS
├── tests/              # 테스트
├── .github/workflows/  # CI/CD
├── Dockerfile          # Docker 설정
└── requirements.txt    # 의존성
```

## 카테고리

- `general` - 일반
- `tech` - 기술
- `life` - 일상
- `study` - 공부

## 라이선스

MIT
