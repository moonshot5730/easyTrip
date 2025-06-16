# 🚀 EasyTrip

## 1. 국내 여행 일정 계획 에이전트

**여행 일정 계획 멀티 에이전트**는 사용자와의 대화를 통해 국내 여행의 일정을 계획해주고 관리해주는 챗봇 서비스입니다.

- **핵심 아이디어**
  - 사용자 대화를 통해 맞춤형 여행 일정을 생성하고 관리하는 멀티 에이전트 시스템
- **주요 기능** 
  - 장소 검색
  - 여행 계획서 작성 및 공유
  - 캘린더 등록, 수정, 삭제, 조회

---

## 2. 기능 설명

### 2.1. 기본 요구사항

#### ✅ 에이전트와의 대화를 통한 여행 장소 검색
- 키워드 기반 장소 검색 및 조건 필터링 지원
- 카카오 장소 검색 API 또는 네이버 지역 검색 API 활용

#### ✅ 대화를 활용한 여행 계획서 작성 
- 포함 정보: 장소, 시간, 활동, 예산 등
- 사용자의 대화 입력을 기반으로 자동 계획서 구성

#### ✅ 대화를 통한 여행 일정 캘린더 등록, 조회, 수정, 삭제 [계획 필요]
- Google Calendar API와 연동
- "OO일 오후 2시에 도착" 등 자연어 명령으로 캘린더 조작

#### ✅ 대화를 통한 여행 계획서 외부 공유 [계획 필요]
- URL 생성 또는 SNS 플랫폼 공유 기능 제공

#### ✅ 에이전트 거짓 정보 방지
- 사용자 피드백 기반 응답 검증 로직 적용

---

### 2.2. 우대 사항 [마지막에 지우기]

#### ✅ 상용 서비스 가정을 통한 아키텍처 설계
- Microservices 기반 구성 고려
- Event-driven 구조 및 확장성 고려
- 다이어그램 및 설계 문서 포함

#### ✅ LLM 및 프롬프트 확장성 구조
- 모델 버전 관리 및 태스크별 최적 모델 사용
- 프롬프트 템플릿 관리 및 동적 생성 구조 설계

#### ✅ 장애 및 예외 상황 대응 처리
- API 실패, LLM 지연/오류, 사용자 오류에 대한 예외 처리
- 재시도 로직, 에러 메시지 전달, 상세 로깅 구현

#### ✅ LLM 품질 테스트 및 평가
- 시나리오 기반 테스트
- 응답 품질 평가 및 사용자 만족도 수집 구조

#### ✅ LLM 가드레일 설정
- 금지 주제 차단, 유해 콘텐츠 필터링, 개인정보 보호 로직 적용

#### ✅ 협업 가능성 고려
- Black, isort 등 linting 도구 사용

#### ✅ 추가 기술 요소
- 비동기 처리 및 스트리밍 응답 제공

---

## 3. 기술 스택

| 항목          | 사용 기술                              |
|-------------|------------------------------------|
| **백엔드 프레임워크** | Python (FastAPI)                   |
| **LLM 프레임워크** | LangChain, LangGraph, LangSmith    |
| **LLM 모델**  | OpenAI, Google                     |
| **UI**      | Streamlit                          |
| **외부 API**  | 카카오 장소 검색 API, Google Calendar API |
| **데이터베이스 (옵션)** | SQLite, PostgreSQL                 |

---

## 4. 아키텍처

![architecture-diagram](./resources/images/architecture.png) <!-- 실제 다이어그램 파일로 대체 -->


### 서비스 흐름 [그림으로 대체]
1. 사용자의 요청 입력 (Streamlit UI)
2. LangChain 기반 에이전트 처리
3. 외부 API/LLM 호출 및 응답 수집
4. 캘린더/계획서 반영 → 사용자에게 시각화된 응답 출력

---

## 5. 설치 및 실행 방법

### 5.1. 환경 설정

```bash
# Python 가상환경 설정
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 패키지 설치
pip install -r requirements.txt
```

### 5.2 주의! 아래의 환경 변수 입력이 필요합니다.
```bash
OPENAI_API_KEY="your_openai_api_key"                    # LLM API 전용
GOOGLE_API_KEY="your_openai_api_key"                    # LLM API 전용
LANGSMITH_API_KEY="your_openai_api_key"                 # LLM 에이전트 모니터링 및 추적용
KAKAO_API_KEY="your_kakao_api_key"                      # 카카오 지도 API 호출용
GOOGLE_CALENDAR_API_KEY="your_google_calendar_api_key"  # 구글 캘린더 등록 전용
```

### 5.2 주의! 아래의 환경 변수 입력이 필요합니다.
```bash
streamlit run easy_trip_streamlit.py                   # 스트림릿 UI 실행
python -m uvicorn main:app --reload    # API 서버 실행
```

## 6. 데모 및 사용 예시

### 대화 기반 장소 검색 예시

### 일정 추가/조회 캘린더 반영 화면

### 계획서 PDF or URL 공유 예시

### 에이전트 응답 캡처 (GIF 또는 이미지)