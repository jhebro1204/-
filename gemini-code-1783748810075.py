import streamlit as st
import re

# --- [페이지 기본 설정] ---
st.set_page_config(page_title="국어 서논술형 학습지", page_icon="📝", layout="centered")

# --- [커스텀 CSS 디자인] ---
# 학습지 느낌을 주기 위한 스타일 설정
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #2c3e50;
        font-weight: 800;
        margin-bottom: 10px;
    }
    .sub-title {
        text-align: center;
        color: #7f8c8d;
        font-size: 16px;
        margin-bottom: 30px;
    }
    .passage-box {
        background-color: #fdfdfd;
        border: 1px solid #dcdde1;
        border-top: 4px solid #3498db;
        padding: 25px;
        border-radius: 8px;
        font-size: 16px;
        line-height: 1.8;
        color: #2f3640;
        margin-bottom: 30px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .question-title {
        color: #2c3e50;
        font-weight: bold;
        font-size: 19px;
        margin-top: 30px;
        margin-bottom: 15px;
        border-left: 5px solid #e74c3c;
        padding-left: 10px;
    }
    .condition-box {
        background-color: #f1f2f6;
        padding: 15px 20px;
        border-radius: 5px;
        font-size: 14.5px;
        color: #2f3640;
        border-left: 3px solid #7f8c8d;
        margin-bottom: 15px;
    }
    .dialogue-speaker {
        font-weight: bold;
        color: #2980b9;
    }
</style>
""", unsafe_allow_html=True)

# --- [채점 로직 함수 (기존과 동일)] ---
def check_keywords(text, positive_list, negative_list=None):
    if not text: return False
    text = text.replace(" ", "")
    has_positive = any(p in text for p in positive_list)
    if negative_list:
        has_negative = any(n in text for n in negative_list)
        return has_positive and not has_negative
    return has_positive

def extract_and_verify_method(text):
    method_match = re.search(r'\((.*?)\)', text)
    if not method_match:
        return False, "설명 방법 표기 누락"
    
    method = method_match.group(1).strip()
    text_without_bracket = re.sub(r'\(.*?\)', '', text).strip()
    
    if "예시" in method:
        if check_keywords(text_without_bracket, ["예를들어", "예컨대", "등이있다", "등을들수"]):
            return True, "예시"
        return False, "예시 특성 부족"
    elif "대조" in method or "비교" in method:
        if check_keywords(text_without_bracket, ["달리", "반면", "다르게", "차이", "그러나", "그렇지않다"]):
            return True, method
        return False, "대조/비교 특성 부족"
    elif "정의" in method:
        if check_keywords(text_without_bracket, ["란", "무엇이다", "뜻한다", "의미한다"]):
            return True, "정의"
        return False, "정의 특성 부족"
    return False, "조건 외 방법"

def grade_set_1(q1_1, q1_2, q1_3, q2_1, q2_2, q3_v, q3_a):
    score = 0
    feedback = []
    
    #
