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
    
    # [서·논술형 1] 채점
    q1_1_ok = check_keywords(q1_1, ["모임", "도서관", "커피숍", "다른사람", "함께"], ["혼자", "차분하게"])
    q1_2_ok = check_keywords(q1_2, ["혼자", "차분하게", "집중"], ["모임", "커피숍", "함께"])
    q1_3_ok = "억제" in q1_3 and "촉진" not in q1_3
    
    if q1_1_ok and q1_2_ok and q1_3_ok:
        score += 30
        feedback.append("✅ [문항 1] +30점: 핵심 정보를 완벽하게 요약했습니다.")
    else:
        feedback.append("❌ [문항 1] 감점: 표의 빈칸에 알맞은 핵심 키워드가 누락되었거나 오개념이 있습니다.")
        
    # [서·논술형 2] 채점
    q2_1_method_ok, q2_1_msg = extract_and_verify_method(q2_1)
    q2_2_method_ok, q2_2_msg = extract_and_verify_method(q2_2)
    q2_1_logic_ok = check_keywords(q2_1, ["쉬운", "친숙한"], ["어려운", "복잡한"])
    q2_2_logic_ok = check_keywords(q2_2, ["어려운", "도전", "복잡한"], ["쉬운", "친숙한"])
    
    if q2_1_method_ok and q2_2_method_ok and q2_1_logic_ok and q2_2_logic_ok:
        score += 40
        feedback.append("✅ [문항 2] +40점: 설명 방법을 적절히 활용하여 논리적으로 서술했습니다.")
    else:
        feedback.append(f"❌ [문항 2] 감점: 설명 방법 표기/활용 오류({q2_1_msg}, {q2_2_msg}) 또는 내용 전개 오류가 있습니다.")
        
    # [서·논술형 3] 채점
    q3_v_ok = check_keywords(q3_v, ["혼자", "차분", "집중", "독서실"]) and check_keywords(q3_v, ["효과", "어려운", "방해"])
    q3_a_ok = check_keywords(q3_a, ["조용한", "작게", "사각", "시계", "초침", "없음"]) and check_keywords(q3_a, ["집중", "몰입"])
    
    if q3_v_ok and q3_a_ok:
        score += 30
        feedback.append("✅ [문항 3] +30점: 복합양식성을 상황에 맞게 훌륭히 기획했습니다.")
    else:
        feedback.append("❌ [문항 3] 감점: 시/청각 요소가 상황에 맞지 않거나, 윗글을 근거로 한 효과 서술이 부족합니다.")
        
    return score, feedback

# --- [사이드바: 핵심 개념] ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3145/3145765.png", width=50) # 장식용 아이콘
    st.header("📖 필수 학습 개념")
    st.markdown("---")
    
    with st.expander("📌 다양한 설명 방법", expanded=True):
        st.write("**• 정의**: 대상의 뜻, 개념 등을 밝힐 때")
        st.write("**• 예시**: 구체적인 예를 바탕으로 대상을 설명할 때")
        st.write("**• 인과**: 원인과 결과를 중심으로 대상을 설명할 때")
        st.write("**• 분석**: 여러 부분으로 이루어진 대상을 설명할 때")
        st.write("**• 비교와 대조**: 공통점(비교)과 차이점(대조)을 드러낼 때")
        st.write("**• 분류와 구분**: 기준에 따라 종류를 묶거나 나눌 때")
    
    with st.expander("📌 영상 매체의 복합양식성", expanded=True):
        st.write("**• 의미**: 문자, 소리, 그림, 동영상 등 다양한 양식이 결합된 것")
        st.write("**• 유의점**: 영상 매체 자료의 주제와 목적, 예상 시청자를 고려하여 복합양식성을 효과적으로 구성해야 함.")

# --- [메인 화면: 학습지 본문] ---
st.markdown("<h1 class='main-title'>2회고사 대비 모의 평가</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>3(2) 설명하는 글 쓰기 & 4(2) 영상 매체 자료 만들기</p>", unsafe_allow_html=True)

# [본문 지문]
st.markdown("<div class='question-title'>[지문] 다음 글을 읽고 물음에 답하시오.</div>", unsafe_allow_html=True)
st.markdown("""
<div class='passage-box'>
    <span class='dialogue-speaker'>기자:</span> 심리학 용어인 '사회적 촉진'과 '사회적 억제'를 일상생활, 특히 우리의 학습에 어떻게 적용할 수 있을까요?<br><br>
    <span class='dialogue-speaker'>전문가:</span> 이 두 가지 개념을 알면 상황에 맞춰 유용하게 활용할 수 있습니다. 예를 들어, 비교적 쉬운 취미 생활이나 큰 노력을 들일 필요가 없는 과제를 할 때는 어떨까요?<br><br>
    <span class='dialogue-speaker'>기자:</span> 음, 그냥 집에서 편하게 혼자 하는 게 집중이 잘되지 않을까요?<br><br>
    <span class='dialogue-speaker'>전문가:</span> 그렇지 않습니다. 오히려 집에서 혼자 하는 것보다는 커피숍이나 도서관에서 하는 것이 더 효율적일 수 있습니다. 평소 친숙하고 좋아하는 과목이라면 공부 모임을 만들어서 다른 사람들과 함께 공부하는 것도 좋은 방법이죠.<br><br>
    <span class='dialogue-speaker'>기자:</span> 그렇다면 어렵고 복잡한 과제를 할 때는 어떻게 해야 하나요?<br><br>
    <span class='dialogue-speaker'>전문가:</span> 그럴 때는 반대입니다. 지나치게 어렵거나 도전이 필요한 과제는 충분히 연습하며 익숙해질 때까지 차분하게 혼자 집중하는 시간을 가지는 것이 좋습니다.
</div>
""", unsafe_allow_html=True)

# --- [문제 영역] ---
st.markdown("<div class='question-title'>[서·논술형 1] 윗글을 요약하여 표로 정리하였다. 빈칸을 채우시오. (30점)</div>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.info("💡 **쉬운 과제 (사회적 촉진)**")
    q1_1 = st.text_input("(1) 효율적인 환경 및 방법은?", placeholder="예: 친구들과 함께...")
with col2:
    st.warning("💡 **어려운 과제 ( ? )**")
    q1_2 = st.text_input("(2) 효율적인 환경 및 방법은?", placeholder="예: 혼자서...")
    q1_3 = st.text_input("(3) 관련된 심리 현상은?", placeholder="정확한 명칭 입력")


st.markdown("<div class='question-title'>[서·논술형 2] 아래 문장에 이어질 설명문을 작성하시오. (40점)</div>", unsafe_allow_html=True)
st.markdown("> **과제의 특성과 난이도에 따라 우리의 학습 효율을 높이는 방법은 다르게 적용되어야 한다.**")
st.markdown("""
<div class='condition-box'>
    <b>&lt;조건&gt;</b><br>
    1. <b>서로 다른 2가지의 설명 방법</b>을 사용하여 (1), (2)에 각각 한 문장씩 작성할 것.<br>
    2. 윗글에 제시된 내용만을 활용할 것.<br>
    3. 각 문장의 끝에 자신이 사용한 <b>설명 방법의 명칭을 괄호에 넣어 표기</b>할 것. (예: ~이다. (비교와 대조))
</div>
""", unsafe_allow_html=True)
q2_1 = st.text_input("(1) 첫 번째 이어질 문장")
q2_2 = st.text_input("(2) 두 번째 이어질 문장")


st.markdown("<div class='question-title'>[서·논술형 3] 영상 기획안의 연출 계획을 세우시오. (30점)</div>", unsafe_allow_html=True)
st.markdown("""
<div class='condition-box'>
    <b>&lt;조건&gt;</b><br>
    1. 윗글을 참고하여 <b>'어려운 과제를 할 때'</b> 필요한 환경 특성이 잘 드러나도록 시/청각 요소를 기획할 것.<br>
    2. 설정한 요소가 내용을 전달하는 데 어떤 <b>효과</b>가 있는지 <b>윗글의 내용을 근거로 서술</b>할 것.
</div>
""", unsafe_allow_html=True)
q3_v = st.text_area("Ⓐ 시각 요소 및 효과 서술", height=100)
q3_a = st.text_area("Ⓑ 청각 요소 및 효과 서술", height=100)

st.markdown("<br>", unsafe_allow_html=True)

# --- [채점 및 피드백 영역] ---
if st.button("📝 답안 제출 및 채점하기", use_container_width=True):
    total_score, results = grade_set_1(q1_1, q1_2, q1_3, q2_1, q2_2, q3_v, q3_a)
    st.markdown("---")
    
    st.subheader(f"💯 당신의 점수는 {total_score}점 입니다!")
    
    # 결과 출력
    for res in results:
        if "✅" in res:
            st.success(res)
        else:
            st.error(res)
            
    # 최종 성취수준 피드백
    if total_score >= 80:
        st.balloons()
        st.info("**[성취수준 A]** 아주 훌륭합니다! 설명 대상의 특성에 맞는 적합한 설명 방법을 능숙하게 활용하고, 매체의 복합양식성을 매우 효과적으로 기획했습니다.")
    elif total_score >= 50:
        st.warning("**[성취수준 B~C]** 잘했습니다! 다만, 설명 방법의 명칭을 정확히 표기했는지, 영상 기획의 '효과'를 서술할 때 본문의 내용을 충분한 근거로 활용했는지 조건을 다시 확인해 보세요.")
    else:
        st.error("**[성취수준 D]** 사이드바의 핵심 개념(설명 방법, 복합양식성)을 다시 꼼꼼히 읽어보고 지문의 핵심 내용을 다시 한번 요약해 보는 연습이 필요합니다.")
