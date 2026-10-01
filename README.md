# CABLE AI 4 Week Lab

패션 상품을 선택하고 질문하면 RAG 검색 근거 또는 Agent 도구 호출 과정을 볼 수 있는 **로컬 학습 프로젝트**입니다. 웹 디자인은 CABLE 에디토리얼 스타일을 적용했습니다. 왼쪽 상단에 `Developer Hae Min Park`를 표시하고, 스마트폰에서는 화면 아래 질문창을 고정했습니다. 상품·가격·재고·판매 데이터는 모두 예시입니다. 주문/결제 기능은 없습니다.

## 0. 프로젝트 구조

```text
CABLE_AI_4Week_Lab/
├── README.md                 ← 이 실행 안내
├── requirements.txt          ← Python 설치 패키지
├── .env.example              ← 환경변수 양식 (.env로 복사)
├── docker-compose.yml        ← live 전용 로컬 pgvector DB
├── app/
│   ├── __init__.py
│   ├── config.py             ← 경로·모드·환경변수
│   ├── data.py               ← 예시 JSON 읽기
│   ├── search.py             ← demo TF-IDF 검색, live 검색 연결
│   ├── db.py                 ← live 문서 임베딩·pgvector 저장/검색
│   ├── rag.py                ← 검색 근거로 답변
│   ├── agent.py              ← 상품 검색/가격 계산 도구
│   └── main.py               ← FastAPI 및 정적 화면
├── data/
│   ├── knowledge.json        ← RAG 문서 7개
│   ├── products.json         ← 예시 상품 4개
│   ├── evaluation.csv        ← 질문 20개/기대 출처
│   └── sales_sample.csv      ← make_sales로 다시 만들 수 있는 예시
├── scripts/
│   ├── __init__.py
│   ├── check_data.py
│   ├── search_demo.py
│   ├── ingest_pgvector.py
│   ├── evaluate.py
│   ├── make_sales.py
│   └── ml_basics.py
├── web/
│   ├── index.html            ← 인터랙티브 화면
│   ├── style.css             ← 반응형 디자인·모바일 하단 고정 질문창
│   ├── app.js                ← 질문 동기화·API 호출·검색 근거/도구 기록 렌더링
│   └── assets/hero.png       ← 패션 에디토리얼 이미지
└── tests/
    ├── test_demo.py          ← 오프라인 핵심 확인
    └── test_live_flow.py     ← 실제 API 호출 없는 도구 루프 모의 확인
```

## 1. 가장 쉬운 실행: demo 모드

Mac 터미널에서 **압축을 푼 이 폴더 안으로 이동**한 다음 실행합니다. Python 3.12 또는 3.13 권장. Python 3.14에서 패키지 설치가 실패하면 3.12로 환경을 다시 만드세요.

```bash
cd ~/Downloads/CABLE_AI_4Week_Lab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -m scripts.check_data
python -m scripts.search_demo
python -m uvicorn app.main:app --reload --port 8001
```

브라우저: **http://127.0.0.1:8001**. 다른 프로그램이 8001을 사용하면 `--port 8002`로 바꾸고 브라우저 주소도 바꿉니다. 서버가 실행 중인 터미널은 그대로 둡니다. 종료는 Ctrl+C.

스마트폰 너비에서는 아래쪽에 질문창이 계속 보입니다. 상품과 RAG/Agent 방식을 선택하면 고정 질문창의 현재 선택 표시도 바뀝니다. 질문을 보내면 키보드를 닫고 결과로 이동합니다. **스마트폰에서 실제로 접속하려면** 실행 중인 서버에 휴대폰이 접근할 수 있어야 합니다. 같은 Wi-Fi에서 시험할 때는 `--host 0.0.0.0`으로 실행하고 컴퓨터의 로컬 IP와 포트(예: `http://192.168.x.x:8001`)를 휴대폰 브라우저에 입력합니다. 방화벽 허용이 필요할 수 있습니다. 이 로컬 실행은 외부 인터넷에서 언제든 접속하는 공개 서비스가 아닙니다.

Windows PowerShell:

```powershell
cd "$HOME\Downloads\CABLE_AI_4Week_Lab"
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --port 8001
```

데모는 API 키·Docker 없이 작동합니다. **TF-IDF 문자 검색 + 규칙 기반 답변/도구 선택**이므로 생성형 AI라고 표현하지 않습니다.

## 2. 실제 AI/RAG 사용: live 모드

OpenAI API 키와 Docker가 필요하며 API 사용량에 따라 비용이 발생합니다. `.env`에서 `CABLE_MODE=live`로 수정하고 **본인 키**를 `OPENAI_API_KEY=` 뒤에 넣습니다. 절대 `.env`를 Git에 올리지 마세요.

```bash
docker compose up -d
python -m scripts.ingest_pgvector
python -m uvicorn app.main:app --reload --port 8001
```

이 compose는 **5433번 로컬 포트의 새 DB**를 쓰고 `cable_lab_documents` 테이블만 만듭니다. 기존 `cableai`의 `documents` 테이블을 변경하지 않습니다. 기존 pgvector 컨테이너를 쓰려면 `DATABASE_URL`만 본인 환경에 맞게 바꾸고 해당 DB에서 vector 확장 생성 권한을 확인하세요. 같은 문서 id 재수집은 upsert하므로 중복 행을 만들지 않습니다.

live 검색: `text-embedding-3-small` (1536차원) → pgvector 코사인 거리 → top-k. live 답변: Responses API의 `OPENAI_MODEL`. live Agent: 모델이 `search_products`, `calculate_total` 중 읽기 전용 도구를 선택합니다. 모델 접근 권한이 없는 경우 `.env`의 `OPENAI_MODEL`을 계정에서 사용 가능한 모델로 바꿉니다.

## 3. 주차별 학습 순서

1. **1주차 검색/평가**: `python -m scripts.check_data`, `python -m scripts.search_demo`, `python -m scripts.evaluate`. 제공된 20개 질문에서 기대 출처·실제 결과를 비교하고 본인 질문을 추가합니다.
2. **2주차 API/RAG**: `app/main.py`의 `/api/ask`를 화면에서 호출. live 모드라면 DB 수집 후 답변과 출처를 확인합니다. `http://127.0.0.1:8001/docs`에서 API도 테스트합니다.
3. **3주차 Agent**: `T01 2개 가격은 얼마인가요?` 질문으로 검색 도구와 계산 도구의 입력·출력을 비교합니다.
4. **4주차 평가/강의**: 기대 출처 20개 평가, 근거 없는 답변 검토, 15분 시범 강의와 오류 해결 시연.

## 4. 머신러닝 별도 실습

```bash
python -m scripts.make_sales
python -m scripts.ml_basics
```

`sales_sample.csv`는 **가상 데이터 80행**입니다. 가격·할인율·광고비·주말 여부로 판매 수량을 예측하고 기준선 MAE와 RandomForest MAE를 비교합니다. 결과가 좋아도 실제 판매 예측으로 사용하면 안 됩니다. 이 지도학습 모델은 RAG 검색·LLM 답변과 별도입니다.

## 5. 확인과 오류

```bash
python -m unittest discover -s tests -v
```

- `No module named fastapi`: 가상환경을 켠 뒤 `python -m pip install -r requirements.txt`.
- `Address already in use`: `--port 8002`로 변경.
- `can't open file` / `No module named app`: 프로젝트 최상위 폴더에서 `python -m scripts.파일명` 실행.
- `503` live: API 키, 모델 접근 권한, Docker DB, `python -m scripts.ingest_pgvector` 순으로 확인.
- `422`: `/docs`에서 `question`(2~500자), `pipeline`(rag 또는 agent) 확인.
- `검색 결과 없음`: demo는 `DEMO_MIN_SCORE`, live는 `LIVE_MIN_SCORE`와 문서/질문 표현, 임베딩 모델, DB 저장 상태 확인. 두 임계값은 예시이며 정답 보증이 아닙니다.
- 화면 정적 서버 `python -m http.server --directory web`만 실행하면 `/api/*`가 없어 기능이 작동하지 않습니다. **uvicorn** 명령으로 실행하세요.

## 6. 범위와 안전

이 프로젝트는 학습용 로컬 앱입니다. 인증, 요금 제한, 공개 배포 설정이 없으므로 인터넷에 공개하지 마세요. 브라우저와 API는 동일 출처여서 별도 CORS 허용을 추가하지 않았습니다. 예시 상품은 실제 판매 상품이 아니며 가격·재고도 실시간이 아닙니다. 검색 유사도 임계값은 정답 보증이 아니므로 평가 질문으로 조정하세요.

기술 참고: [OpenAI Function Calling](https://developers.openai.com/api/docs/guides/function-calling), [OpenAI Embeddings](https://developers.openai.com/api/docs/guides/embeddings), [pgvector](https://github.com/pgvector/pgvector), [FastAPI](https://fastapi.tiangolo.com/).
