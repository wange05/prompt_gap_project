# prompt_gap_project
# 🚀 대화의 격차: AI를 부리는 질문의 힘 

사용자의 단순하고 투박한 질문(Raw Prompt)을 AI가 프롬프트 엔지니어링 원칙에 따라 스스로 수정하고, 원본과 정제본의 결과를 실시간으로 대조하여 보여주는 비교 체험형 인터랙티브 웹 플랫폼입니다. 대학생 참여자들의 AI 리터러시를 함양하고 질문 방식에 따른 결과물의 질적 차이를 직관적으로 체득할 수 있도록 돕기 위해 기획 및 개발되었습니다.

---

## ✨ 주요 기능

1. **프롬프트 자가 수정 (Self-Refining):** 사용자가 입력한 모호하고 짧은 질문을 분석하여 구체적인 페르소나 부여, 명확한 맥락 추가, 출력 형식 지정 등의 전략을 반영한 정교한 프롬프트(Insight Card)로 자동 재구성합니다.
2. **병렬 비교 체험 (Side-by-Side):** 파이썬의 병렬 처리 엔진(`ThreadPoolExecutor`)을 활용하여 두 개의 API를 동시에 호출함으로써 원본 질문의 결과와 정제된 질문의 전문적인 결과를 화면 좌우에 나란히 배치해 질적 차이를 직접 대조하게 합니다.
3. **AI 답변 품질 평가 (LLM-as-a-Judge):** 평가 전용 모델이 개입하여 두 답변의 '구체성', '실용성', '가독성' 지표를 100점 만점으로 엄격하게 절대 평가하고, 이를 시각적인 막대그래프 차트로 제공합니다.
4. **단계별 온보딩 및 사후 설문 연동:** 참여자가 시스템을 체험하기 전과 후에 QR 코드 및 링크를 통해 설문조사에 완결성 있게 참여할 수 있도록 인터페이스 내에 통합되어 있습니다.

---

## 🛠️ 기술 스택 및 환경

- **Language / Framework:** Python 3.10+, Streamlit
- **AI Engine / LLM:** Google Gemini 2.5 Flash API (메인 생성 및 Judge 에디션 공통 적용)
- **Deployment:** Streamlit Community Cloud

---

## ⚙️ 시작하기 

이 프로젝트를 로컬 환경에 복제하여 실행하거나 본인의 API 키를 연동하려면 아래 단계를 따르세요.

### 1. 저장소 클론 및 패키지 설치
프로젝트 코드를 다운로드하고 이동한 뒤, 필요한 필수 라이브러리들을 설치합니다.

```bash
git clone [https://github.com/wange05/prompt_gap_project.git](https://github.com/wange05/prompt_gap_project.git)
cd prompt_gap_project
pip install -r requirements.txt
```

### 2. 환경 변수 설정 및 애플리케이션 실행
보안을 위해 API 키는 소스코드에 하드코딩하지 않고 환경 변수 파일로 관리합니다. 프로젝트 최상단 루트 폴더에 `.env` 파일을 생성하여 발급받은 실제 Gemini API 키를 입력한 후, Streamlit 애플리케이션을 즉시 실행합니다.

**환경 변수 파일 설정 (`.env`)**
```env
GEMINI_API_KEY=발급받으신_실제_Gemini_API_키_입력
```

**애플리케이션 실행**
```bash
streamlit run app.py
```
