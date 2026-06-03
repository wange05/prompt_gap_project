import os
import re
import time
import json
import pandas as pd
import altair as alt
import streamlit as st
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# 1. API 셋업 및 앱 기본 설정
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 답변 생성용 모델 설정
model_name = 'gemini-2.5-flash'
model = genai.GenerativeModel(model_name)

# 평가(Judge) 전용 모델 세팅
judge_config = genai.GenerationConfig(response_mime_type="application/json")
judge_model = genai.GenerativeModel(model_name, generation_config=judge_config)

# Streamlit 페이지 기본 설정
st.set_page_config(page_title="대화의 격차 | AI 프롬프트 데모", page_icon="🚀", layout="wide")

if 'has_results' not in st.session_state:
    st.session_state.has_results = False

# 2. 핵심 로직 
# 프롬프트 자가 수정(Self-Refining) 로직
def refine_prompt(user_input):
    system_prompt = """
    너는 Professional Prompt Engineer야.
    사용자의 질문을 분석해서, AI가 최고 수준의 답변을 할 수 있도록 프롬프트를 고쳐줘.
    [원칙] 1. 구체적인 페르소나 부여  2. 명확한 목적/맥락 추가  3. 출력 형식 지정(표, 리스트 등)
    IMPORTANT: You MUST ONLY output the final refined prompt. No filler words.
    [사용자 질문]
    """
    return model.generate_content(system_prompt + user_input).text.strip()

# 원본 질문 응답 생성
def get_raw_response(prompt):
    # [Developer Note] 교육적 목적을 위해 의도적으로 AI의 자체 포맷팅을 제한함
    secret_instruction = "\n\n(System Note: 사용자의 원본 질문 의도에만 맞춰서 추가적인 포맷팅(마크다운 표, 글머리 기호 등) 없이 기본 줄글 형태로만 간결하게 답변해.)"
    return model.generate_content(prompt + secret_instruction).text.strip()

# 정제된 질문 응답 생성
def get_refined_response(prompt):
    secret_instruction = "\n\n(System Note: 프롬프트에 요구된 페르소나와 출력 형식을 완벽하게 적용해서 전문적이고 가독성 좋게 답변해.)"
    return model.generate_content(prompt + secret_instruction).text.strip()

# LLM-as-a-Judge 품질 평가 로직
def evaluate_quality_with_llm(raw_ans, refined_ans):
    judge_prompt = f"""
    너는 객관적이고 엄격한 텍스트 품질 평가자야. 
    아래 두 가지 답변(Answer A, Answer B)을 읽고, '구체성', '실용성', '가독성' 3가지 지표를 0에서 100점 사이로 절대 평가해.
    
    [Answer A (원본 질문 결과)]
    {raw_ans}
    
    [Answer B (정제된 질문 결과)]
    {refined_ans}
    
    반드시 아래의 JSON 형식으로만 응답해:
    {{
        "raw_score": {{"구체성": 0, "실용성": 0, "가독성": 0}},
        "ref_score": {{"구체성": 0, "실용성": 0, "가독성": 0}}
    }}
    """
    try:
        response = judge_model.generate_content(judge_prompt)
        score_data = json.loads(response.text)
        return score_data["raw_score"], score_data["ref_score"]
    except Exception as e:
        st.error(f"평가 중 오류가 발생했습니다: {e}")
        return {"구체성": 50, "실용성": 50, "가독성": 50}, {"구체성": 90, "실용성": 90, "가독성": 90}

# 3. UI: 메인 데모 화면 (발표 시연용)
st.title("🚀 대화의 격차: AI를 부리는 질문의 힘")
st.markdown("단순한 질문과 **'프롬프트 엔지니어링'**이 적용된 질문의 결과 차이를 직관적으로 비교해 보세요.")

with st.sidebar:
    st.markdown("---")
    st.markdown("### 📋 Step 1: 사전 설문조사")
    st.markdown("체험 전, AI 활용 능력에 대한 간단한 설문을 진행해 주세요.")

    pre_survey_url = "{여기에_사전_설문조사_구글폼_링크를_입력하세요}" 
    
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={pre_survey_url}", width=150)
    st.markdown(f"[🔗 모바일이 아니라면? 링크로 참여하기]({pre_survey_url})")
    st.markdown("---")
    
    st.markdown("### 💡 시연용 추천 질문")
    st.code("대학교 IT 동아리 신입생 모집 홍보 전략이랑 면접 질문 짜줘.", language="text")
    st.code("파이썬으로 시계열 데이터 분석 코드 짜는데 에러가 나. 어떻게 고쳐?", language="text")

raw_prompt = st.text_input("💬 AI에게 던질 투박한 질문을 입력해 보세요!")

if st.button("결과 비교 및 분석하기 🔍", type="primary", use_container_width=True):
    if not raw_prompt:
        st.warning("질문을 먼저 입력해 주세요!")
    else:
        my_bar = st.progress(0, text="단계 1/3: 프롬프트 재구성 중...")
        start_time = time.time()
        
        refined_prompt = refine_prompt(raw_prompt)
        my_bar.progress(33, text="단계 2/3: 병렬 AI 응답 생성 중...")

        # 병렬 처리(ThreadPoolExecutor)를 통한 API 대기 시간 최적화
        with ThreadPoolExecutor() as executor:
            res_raw = executor.submit(get_raw_response, raw_prompt).result()
            res_ref = executor.submit(get_refined_response, refined_prompt).result()
        
        my_bar.progress(66, text="단계 3/3: LLM 품질 정량 분석 중...")
        
        score_raw, score_ref = evaluate_quality_with_llm(res_raw, res_ref)
        
        my_bar.progress(100, text=f"✅ 실행 완료! ({time.time() - start_time:.2f}초 소요)")
        time.sleep(0.5)
        my_bar.empty()

        st.session_state.has_results = True
        st.session_state.res_data = {
            "raw_p": raw_prompt, "ref_p": refined_prompt,
            "raw_a": res_raw, "ref_a": res_ref,
            "s_raw": score_raw, "s_ref": score_ref
        }

# 4. UI: 결과 렌더링부
if st.session_state.has_results:
    data = st.session_state.res_data
    st.markdown("---")
    
    # 정제된 프롬프트 Insight Card 렌더링
    cleaned_refined_prompt = re.sub(r'\n{3,}', '\n\n', data['ref_p'].strip())
    custom_css_box = f"""
    <div style="background-color: #FFFFFF; color: #000000; padding: 20px; border-radius: 10px; border: 2px solid #E5E7EB; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 30px; max-height: 250px; overflow-y: auto;">
        <div style="font-weight: bold; font-size: 1.1em; color: #1C83E1; margin-bottom: 10px;">✨ AI가 재구성한 마법의 프롬프트 (Insight Card):</div>
        <div style="font-size: 1em; line-height: 1.6; white-space: pre-wrap; word-break: break-word;">{cleaned_refined_prompt}</div>
    </div>
    """
    st.markdown(custom_css_box, unsafe_allow_html=True)
    
    # Side-by-Side 결과 렌더링
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔴 1. 원본 질문의 결과")
        with st.expander("질문 보기"): st.write(data['raw_p'])
        with st.container(height=500, border=True): st.markdown(data['raw_a'])
    with col2:
        st.markdown("#### 🔵 2. 정제된 질문의 결과")
        with st.expander("질문 보기"): st.write(data['ref_p'])
        with st.container(height=500, border=True): st.markdown(data['ref_a'])

    st.markdown("<br>", unsafe_allow_html=True)

    # 평가 차트 렌더링
    st.markdown("#### 📊 3. AI 답변 품질 평가 (LLM-as-a-Judge)")
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

    # 사후 설문조사 QR 코드 렌더링
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
        st.success("💡 여러분의 솔직한 피드백은 'AI를 다루는 태도 변화'를 측정하는 소중한 연구 데이터로 활용됩니다.")