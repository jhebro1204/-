import streamlit as st
import re

# --- [채점 로직 함수] ---
def check_keywords(text, positive_list, negative_list=None):
    """긍정 키워드 포함 여부 및 부정 키워드(오개념) 미포함 여부 확인"""
    if not text:
        return False
    
    text = text.replace(" ", "")
    has_positive = any(p in text for p in positive_list)
    
    if negative_list:
        has_negative = any(n in text for n in negative_list)
        return has_positive and not has_negative
    return has_positive

def extract_and_verify_method(text):
    """괄호 안의 설명 방법을 추출하고, 해당 방법의 특성이 글에 드러나는지 확인"""
    method_match = re.search(r'\((.*?)\)', text)
    if not method_match:
        return False, "설명 방법이 괄호 안에 표기되지 않았습니다."
    
    method = method_match.group(1).strip()
    text_without_bracket = re.sub(r'\(.*?\)', '', text).strip()
    
    if "예시" in method:
        if check_keywords(text_without_bracket, ["예를들어", "예컨대", "등이있다", "등을들수"]):
            return True, "예시"
        return False, "예시의 특성(예를 들어 등)이 드러나지 않았습니다."
    elif "대조" in method or "비교" in method:
        if check_keywords(text_without_bracket, ["달리", "반면", "다르게", "차이", "그러나", "그렇지않다"]):
            return True, method
        return False, f"{method}의 특성(대조적 표현)이 드러나지 않았습니다."
    elif "정의" in method:
        if check_keywords(text_without_bracket, ["란", "무엇이다", "뜻한다", "의미한다"]):
            return True, "정의"
        return False, "정의의 특성(~란 ~이다 등)이 드러나지 않았습니다."
    
    return False, "조건에서 요구한 설명 방법(예시, 대조 등)이 아닙니다."

def grade_set_1(q1_1, q1_2, q1_3, q2_1, q2_2, q3_v, q3_a):
    score = 0
    feedback = []
    
    # [서·논술형 1] 채점
    q1_1_ok = check_keywords(q1_1, ["모임", "도서관", "커피숍", "다른사람", "함께"], ["혼자", "차분하게"])
    q1_2_ok = check_keywords(q1_2, ["혼자", "차분하게", "집중"], ["모임", "커피숍", "함께"])
    q1_3_ok = "억제" in q1_3 and "촉진" not in q1_3
    
    if q1_1_ok and q1_2_ok and q1_3_ok:
        score += 30
        feedback.append("✅ [서·논술형 1] 정답입니다. (오개념 없이 빈칸의 의미를 정확히 작성했습니다.)")
    else:
        feedback.append("❌ [서·논술형 1] 오답이 있습니다. 키워드 누락 혹은 오개념(다른 개념의 특성 혼용)이 발견되었습니다.")
        
    # [서·논술형 2] 채점
    q2_1_method_ok, q2_1_msg = extract_and_verify_method(q2_1)
    q2_2_method_ok, q2_2_msg = extract_and_verify_method(q2_2)
    
    # 결론 방향 확인 및 오개념 방지
    q2_1_logic_ok = check_keywords(q2_1, ["쉬운", "친숙한"], ["어려운", "복잡한"])
    q2_2_logic_ok = check_keywords(q2_2, ["어려운", "도전", "복잡한"], ["쉬운", "친숙한"])
    
    if q2_1_method_ok and q2_2_method_ok and q2_1_logic_ok and q2_2_logic_ok:
        score += 40
        feedback.append("✅ [서·논술형 2] 정답입니다. 두 가지 설명 방법을 적절히 사용하였고 결론이 명확합니다.")
    else:
        feedback.append(f"❌ [서·논술형 2] 감점 요인이 있습니다. (문장 1: {q2_1_msg} / 문장 2: {q2_2_msg}) 또는 논리 방향 오류입니다.")
        
    # [서·논술형 3] 채점 (결론 방향: '혼자 집중'의 효과가 드러나야 함)
    q3_v_ok = check_keywords(q3_v, ["혼자", "차분", "집중", "독서실"]) and check_keywords(q3_v, ["효과", "어려운", "방해"])
    q3_a_ok = check_keywords(q3_a, ["조용한", "작게", "사각", "시계", "초침", "없음"]) and check_keywords(q3_a, ["집중", "몰입"])
    
    if q3_v_ok and q3_a_ok:
        score += 30
        feedback.append("✅ [서·논술형 3] 정답입니다. 시/청각 요소와 그 효과가 본문 근거에 맞게 서술되었습니다.")
    else:
        feedback.append("❌ [서·논술형 3] 감점 요인이 있습니다. 시/청각 요소가 상황에 맞지 않거나 효과 서술 시 지문의 근거가 누락되었습니다.")
        
    return score, feedback

# --- [Streamlit UI 구성] ---
st.title("📝 국어 서·논술형 자동 채점 시스템")
st.markdown("성취기준 도달 여부를 확인하기 위한 모의고사 자동 채점기입니다.")

st.header("[세트 1] 사회적 촉진과 억제")

st.subheader("[서·논술형 1] 표 빈칸 채우기")
q1_1 = st.text_input("(1) 쉬운 과제의 환경/방법")
q1_2 = st.text_input("(2) 어려운 과제의 환경/방법")
q1_3 = st.text_input("(3) 관련된 심리 현상")
st.info("**모범 답안 및 허용 범위**\n* (1) 커피숍, 도서관 등에서 하거나 모임을 만들어 다른 사람들과 함께 함 (의미 포함 시 인정)\n* (2) 차분하게 혼자 집중하는 시간을 가짐 (의미 포함 시 인정)\n* (3) 사회적 억제 (오개념 방지: '사회적 촉진' 기재 시 오답)")

st.subheader("[서·논술형 2] 설명문 작성하기")
st.markdown("조건: 서로 다른 2가지 설명 방법 사용, 괄호 표기, 본문 내용 활용")
q2_1 = st.text_area("(1) 첫 번째 이어질 문장")
q2_2 = st.text_area("(2) 두 번째 이어질 문장")

st.subheader("[서·논술형 3] 영상 매체 기획안")
st.markdown("조건: '어려운 과제를 할 때'의 시청각 요소 및 효과 서술")
q3_v = st.text_area("시각 요소(Ⓐ) 및 효과")
q3_a = st.text_area("청각 요소(Ⓑ) 및 효과")

if st.button("채점하기"):
    total_score, results = grade_set_1(q1_1, q1_2, q1_3, q2_1, q2_2, q3_v, q3_a)
    st.divider()
    st.subheader(f"💯 총점: {total_score}점 / 100점")
    
    for res in results:
        st.write(res)
        
    if total_score >= 80:
        st.success("성취수준 A에 도달했습니다! 설명 방법을 능숙하게 활용하고 복합양식성을 훌륭히 기획했습니다.")
    elif total_score >= 50:
        st.warning("성취수준 B~C 수준입니다. 설명 방법의 정확한 표기나 조건(효과 근거)을 다시 확인해 보세요.")
    else:
        st.error("성취수준 D 수준 이하입니다. 본문의 핵심 정보와 설명 방법의 개념을 다시 복습해 봅시다.")