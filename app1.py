import re
import time
import pandas as pd
import altair as alt
import streamlit as st

# Streamlit 페이지 기본 설정 (전체 화면 넓게 쓰기)
st.set_page_config(page_title="대화의 격차 | AI 프롬프트 데모", page_icon="🚀", layout="wide")

# 세션 상태 초기화 (결과 유지용)
if 'has_results' not in st.session_state:
    st.session_state.has_results = False

# ----------------------------------------------------------------품
# [데모 모드] 실제 AI 호출 대신 가짜 데이터(Mock Data)를 반환하는 시뮬레이션 함수들
# ----------------------------------------------------------------
def get_mock_refined_prompt(user_input):
    """AI 프롬프트 엔지니어가 정제한 것 같은 가짜 프롬프트를 생성합니다."""
    return f"""# Persona
너는 10년 경력의 베테랑 전문가이자 핵심 요약 마스터야.

# Context
사용자는 현재 '{user_input}'에 대한 정보를 필요로 하고 있으며, 비전문가도 한눈에 이해할 수 있는 최고 수준의 결과물을 원해.

# Constraints
- 주관적인 수식어는 배제하고 데이터와 논리에 기반하여 작성해줘.
- 전문 용어가 나올 경우 괄호를 활용해 쉬운 설명을 덧붙여줘.

# Output Format
가독성을 극대화하기 위해 핵심 내용을 요약 카드와 Side-by-Side 비교 구조로 출력해."""

def get_mock_raw_response():
    """투박한 질문에 대한 일반적인 줄글 형태의 답변 샘플입니다."""
    return "요청하신 내용에 대한 일반적인 답변입니다. 질문이 다소 추상적이거나 명확한 제약 조건이 주어지지 않았기 때문에, 모델이 기본 학습 데이터에 의존하여 보편적이고 평범한 수준의 정보를 나열합니다. 글머리 기호나 가독성을 높이는 마크다운 구조가 배제되어 있어, 사용자가 필요한 핵심 인사이트를 빠르게 찾아내기에 다소 비효율적일 수 있습니다."

def get_mock_refined_response():
    """정제된 프롬프트로 인해 구조화되고 전문적인 답변이 나온 샘플입니다."""
    return """### ✨ 프롬프트 엔지니어링이 적용된 마스터클래스 답변

#### 1. 핵심 전략 및 포지셔닝
- **타겟 최적화:** 사용자의 숨은 의도를 파악하여 직관적이고 즉각적인 실행이 가능한 솔루션을 제공합니다.
- **구조적 배치:** 정보의 중요도에 따라 레이아웃을 계층화하여 시각적 피로도를 최소화합니다.

#### 2. 실무 적용 가이드
| 단계 | 주요 태스크 | 기대 효과 |
| :--- | :--- | :--- |
| **01단계** | 요구사항 구체화 및 페르소나 설정 | AI의 답변 왜곡(Hallucination) 현상 방지 |
| **02단계** | 출력 포맷(Table, List) 강제 지정 | 가독성 200% 향상 및 데이터 구조화 완수 |

> **💡 전문가 인사이트:** 질문의 구체성이 확보될 때 최신 범용 모델(LLM)은 단순 답변 기계에서 강력한 전략적 파트너로 진화합니다."""

# ----------------------------------------------------------------
# UI: 메인 데모 화면 (발표 시연용 레이아웃)
# ----------------------------------------------------------------
st.title("🚀 대화의 격차: AI를 부리는 질문의 힘")
st.markdown("단순한 질문과 **'프롬프트 엔지니어링'**이 적용된 질문의 결과 차이를 직관적으로 비교해 보세요.")

# 사이드바 구성 (사전 설문조사 영역 및 추천 질문)
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📋 Step 1: 사전 설문조사")
    st.markdown("체험 전, AI 활용 능력에 대한 간단한 설문을 진행해 주세요.")
    
    # 오픈소스 배포용 플레이스홀더 주소 유지
    pre_survey_url = "{여기에_사전_설문조사_구글폼_링크를_입력하세요}" 
    
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={pre_survey_url}", width=150)
    st.markdown(f"[🔗 모바일이 아니라면? 링크로 참여하기]({pre_survey_url})")
    st.markdown("---")
    
    st.markdown("### 💡 시연용 추천 질문")
    st.code("대학교 IT 동아리 신입생 모집 홍보 전략이랑 면접 질문 짜줘.", language="text")
    st.code("파이썬으로 시계열 데이터 분석 코드 짜는데 에러가 나. 어떻게 고쳐?", language="text")

# 질문 입력창
raw_prompt = st.text_input("💬 AI에게 던질 투박한 질문을 입력해 보세요!", placeholder="예: 대학교 동아리 홍보 전략 짜줘.")

# 실행 버튼 및 시뮬레이션 애니메이션
if st.button("결과 비교 및 분석하기 🔍", type="primary", use_container_width=True):
    if not raw_prompt:
        st.warning("질문을 먼저 입력해 주세요!")
    else:
        # 실제 API 대기 시간을 시각적으로 보여주기 위한 진행 상태 바 애니메이션 생성
        my_bar = st.progress(0, text="단계 1/3: 프롬프트 재구성 중...")
        time.sleep(0.8)
        
        refined_prompt = get_mock_refined_prompt(raw_prompt)
        my_bar.progress(33, text="단계 2/3: 병렬 AI 응답 생성 중...")
        time.sleep(1.0)

        res_raw = get_mock_raw_response()
        res_ref = get_mock_refined_response()
        
        my_bar.progress(66, text="단계 3/3: LLM 품질 정량 분석 중...")
        time.sleep(0.8)
        
        # 가짜 점수 셋팅 (원본은 낮게, 정제본은 높게 대조군 설정)
        score_raw = {"구체성": 45, "실용성": 50, "가독성": 40}
        score_ref = {"구체성": 95, "실용성": 92, "가독성": 98}
        
        my_bar.progress(100, text="✅ 시연용 데이터 매핑 완료!")
        time.sleep(0.4)
        my_bar.empty()

        # 세션 상태에 데이터 박제
        st.session_state.has_results = True
        st.session_state.res_data = {
            "raw_p": raw_prompt, "ref_p": refined_prompt,
            "raw_a": res_raw, "ref_a": res_ref,
            "s_raw": score_raw, "s_ref": score_ref
        }

# ----------------------------------------------------------------
# UI: 결과 대시보드 렌더링부
# ----------------------------------------------------------------
if st.session_state.has_results:
    data = st.session_state.res_data
    st.markdown("---")
    
    # 1. 정제된 프롬프트 노출 (Insight Card)
    cleaned_refined_prompt = re.sub(r'\n{3,}', '\n\n', data['ref_p'].strip())
    custom_css_box = f"""
    <div style="background-color: #FFFFFF; color: #000000; padding: 20px; border-radius: 10px; border: 2px solid #E5E7EB; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 30px; max-height: 250px; overflow-y: auto;">
        <div style="font-weight: bold; font-size: 1.1em; color: #1C83E1; margin-bottom: 10px;">✨ AI가 재구성한 마법의 프롬프트 (Insight Card):</div>
        <div style="font-size: 1em; line-height: 1.6; white-space: pre-wrap; word-break: break-word;">{cleaned_refined_prompt}</div>
    </div>
    """
    st.markdown(custom_css_box, unsafe_allow_html=True)
    
    # 2. 텍스트 결과 비교 (Side-by-Side)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔴 1. 원본 질문의 결과")
        with st.expander("질문 보기"): st.write(data['raw_p'])
        with st.container(height=400, border=True): st.markdown(data['raw_a'])
    with col2:
        st.markdown("#### 🔵 2. 정제된 질문의 결과")
        with st.expander("질문 보기"): st.write(data['ref_p'])
        with st.container(height=400, border=True): st.markdown(data['ref_a'])

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. 데이터프레임 변환 및 Altair 막대 차트 시각화 (LLM-as-a-Judge 코스프레)
    st.markdown("#### 📊 3. AI 답변 품질 평가 (LLM-as-a-Judge 시뮬레이션)")
    df_melted = pd.DataFrame({
        "평가 지표": ["구체성", "실용성", "가독성"] * 2,
        "유형": ["🔴 원본"]*3 + ["🔵 정제본"]*3,
        "점수": list(data['s_raw'].values()) + list(data['s_ref'].values())
    })

    chart = alt.Chart(df_melted).mark_bar().encode(
        x=alt.X('평가 지표:N', title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y('점수:Q', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('유형:N', scale=alt.Scale(domain=["🔴 원본", "🔵 정제본"], range=["#FF8787", "#339AF0"]), legend=alt.Legend(title=None, orient="bottom")),
        xOffset='유형:N'
    ).properties(height=300).configure_view(stroke='transparent')
    
    st.altair_chart(chart, use_container_width=True)

    # 사후 설문조사 QR 코드 및 아웃트로 푸터
    st.markdown("---")
    st.markdown("### 🎯 Step 2: 사후 설문조사 및 지식 확인")
    st.markdown("프롬프트 엔지니어링의 위력을 체감하셨나요? 설문에 참여하고 핵심 요약본을 받아가세요!")
    
    col_qr1, col_qr2 = st.columns([1, 4])
    with col_qr1:
        post_survey_url = "{여기에_사후_설문조사_구글폼_링크를_입력하세요}"
        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={post_survey_url}", width=150)
    with col_qr2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"**[👉 사후 설문조사 참여 및 PDF 다운로드 링크 바로가기]({post_survey_url})**")
        st.success("💡 본 화면은 오프라인 및 API 비연동 상태에서도 서비스 인프라 구성을 발표·테스트할 수 있는 무호출 데모 샌드박스입니다.")