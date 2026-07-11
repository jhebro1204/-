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
        feedback.append("✅ [서·논술형 1] 정답입니다. (30/30점) 핵심 정보를 정확히 요약했습니다.")
    else:
        feedback.append("❌ [서·논술형 1] 오답 혹은 부분 점수입니다. 키워드 누락이 있거나 오개념이 섞여 있습니다.")
        
    # [서·논술형 2] 채점
    q2_1_method_ok, q2_1_msg = extract_and_verify_method(q2_1)
    q2_2_method_ok, q2_2_msg = extract_and_verify_method(q2_2)
    q2_1_logic_ok = check_keywords(q2_1, ["쉬운", "친숙한"], ["어려운", "복잡한"])
    q2_2_logic_ok = check_keywords(q2_2, ["어려운", "도전", "복잡한"], ["쉬운", "친숙한"])
    
    if q2_1_method_ok and q2_2_method_ok and q2_1_logic_ok and q2_2_logic_ok:
        score += 40
        feedback.append("✅ [서·논술형 2] 정답입니다. (40/40점) 설명 방법을 잘 활용하여 글을 구성했습니다.")
    else:
        feedback.append(f"❌ [서·논술형 2] 감점 요인이 있습니다. (문장 1: {q2_1_msg} / 문장 2: {q2_2_msg}) 또는 논리 오류가 있습니다.")
        
    # [서·논술형 3] 채점
    q3_v_ok = check_keywords(q3_v, ["혼자", "차분", "집중", "독서실"]) and check_keywords(q3_v, ["효과", "어려운", "방해"])
    q3_a_ok = check_keywords(q3_a, ["조용한", "작게", "사각", "시계", "초침", "없음"]) and check_keywords(q3_a, ["집중", "몰입"])
    
    if q3_v_ok and q3_a_ok:
        score += 30
        feedback.append("✅ [서·논술형 3] 정답입니다. (30/30점) 시청각 요소와 그 효과를 본문 근거에 맞게 잘 서술했습니다.")
    else:
        feedback.append("❌ [서·논술형 3] 감점 요인이 있습니다. 시/청각 요소가 상황에 맞지 않거나 효과 서술 시 지문의 근거가 부족합니다.")
        
    return score, feedback

# --- [사이드바: 핵심 개념] ---
with st.sidebar:
    st.header("📖 2회고사 대비 핵심 개념")
    st.markdown("---")
    
    st.subheader("1. 다양한 설명 방법")
    st.info("""
    * **정의**: 대상의 뜻, 개념 등을 밝힐 때
    * **예시**: 구체적인 예를 바탕으로 대상을 설명할 때
    * **인과**: 원인과 결과를 중심으로 대상을 설명할 때
    * **분석**: 여러 요소나 부분으로 이루어진 대상을 설명할 때
    * **비교와 대조**: 둘 이상의 대상의 공통점(비교)과 차이점(대조)을 드러낼 때
    * **분류와 구분**: 대상을 기준에 따라 묶거나 나눌 때
    """)
    
    st.subheader("2. 영상 매체의 복합양식성")
    st.info("""
    * **복합양식성**: 문자, 소리, 그림, 사진, 동영상 등 다양한 양식이 결합된 것
    * **유의할 점**: 
      - 영상 매체 자료의 특징인 복합양식성을 고려해야 함
      - 주제와 목적, 예상 시청자를 고려해야 함
    * **스토리보드 구성**: 화면(시각), 소리(청각), 자막 등
    """)

# --- [메인 화면: 지문 및 문제] ---
st.title("📝 국어 서·논술형 문항 실전 연습")
st.markdown("왼쪽 사이드바의 개념을 참고하여 아래의 지문을 읽고 물음에 답하시오.")
st.markdown("---")

# [본문 지문]
st.subheader("[지문] 효율적인 표현법 실전 적용-1")
st.success("""
**기자**: 심리학 용어인 '사회적 촉진'과 '사회적 억제'를 일상생활, 특히 우리의 학습에 어떻게 적용할 수 있을까요?

**전문가**: 이 두 가지 개념을 알면 상황에 맞춰 유용하게 활용할 수 있습니다. 예를 들어, 비교적 쉬운 취미 생활이나 큰 노력을 들일 필요가 없는 과제를 할 때는 어떨까요?

**기자**: 음, 그냥 집에서 편하게 혼자 하는 게 집중이 잘되지 않을까요?

**전문가**: 그렇지 않습니다. 오히려 집에서 혼자 하는 것보다는 커피숍이나 도서관에서 하는 것이 더 효율적일 수 있습니다. 평소 친숙하고 좋아하는 과목이라면 공부 모임을 만들어서 다른 사람들과 함께 공부하는 것도 좋은 방법이죠.

**기자**: 그렇다면 어렵고 복잡한 과제를 할 때는 어떻게 해야 하나요?

**전문가**: 그럴 때는 반대입니다. 지나치게 어렵거나 도전이 필요한 과제는 충분히 연습하며 익숙해질 때까지 차분하게 혼자 집중하는 시간을 가지는 것이 좋습니다.
""")

# [문제 1]
st.markdown("### [서·논술형 1] 표 요약하기 (30점)")
st.markdown("윗글을 요약하여 표로 정리하였다. ( )에 들어갈 내용을 찾아 쓰시오.")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**과제의 특성**")
    st.write("비교적 쉽거나 노력이 필요 없는 과제")
    st.write("지나치게 어렵거나 도전이 필요한 과제")
with col2:
    st.markdown("**효율적인 환경 및 방법**")
    q1_1 = st.text_input("(1) 빈칸 입력", key="q1_1")
    q1_2 = st.text_input("(2) 빈칸 입력", key="q1_2")
with col3:
    st.markdown("**관련된 심리 현상**")
    st.write("사회적 촉진")
    q1_3 = st.text_input("(3) 빈칸 입력", key="q1_3")

st.markdown("---")

# [문제 2]
st.markdown("### [서·논술형 2] 설명문 작성하기 (40점)")
st.markdown("""
윗글을 활용하여 '과제 난이도에 따른 효율적인 학습 전략'에 대한 설명문을 작성하려 한다. 주어진 첫 문장에 이어지는 내용인 (1), (2)를 <조건>에 맞추어 작성하시오.

> **과제의 특성과 난이도에 따라 우리의 학습 효율을 높이는 방법은 다르게 적용되어야 한다.**
""")
st.info("""
**<조건>**
* 서로 다른 2가지의 설명 방법을 사용하여, 이어지는 문장을 (1), (2)에 각각 하나씩 작성할 것.
* 윗글에 제시된 내용만을 활용할 것. (외부 배경지식 활용 불가)
* 각 문장의 끝에 자신이 사용한 설명 방법의 명칭을 괄호에 넣어 표기할 것. (예: ~이다. (대조))
""")
q2_1 = st.text_area("(1) 문장 작성 (설명 방법 포함)")
q2_2 = st.text_area("(2) 문장 작성 (설명 방법 포함)")

st.markdown("---")

# [문제 3]
st.markdown("### [서·논술형 3] 영상 기획안 작성하기 (30점)")
st.markdown("""
윗글을 바탕으로 '상황에 맞는 학습 공간 선택법'을 설명하는 영상을 제작하려 한다. **[장면 2] 어려운 과제를 할 때** 에 들어갈 연출 계획을 세우시오.
""")
st.info("""
**<조건>**
* 윗글을 참고하여 '어려운 과제'를 할 때 필요한 환경의 특성이 잘 드러나도록 시각 요소(Ⓐ)와 청각 요소(Ⓑ)를 기획할 것.
* 자신이 설정한 시각/청각 요소가 글의 내용을 전달하는 데 어떤 **효과**가 있는지 **윗글의 내용을 근거로 반드시 서술**할 것.
""")
q3_v = st.text_area("시각 요소(Ⓐ)의 내용과 그 효과 서술")
q3_a = st.text_area("청각 요소(Ⓑ)의 내용과 그 효과 서술")

# [채점 버튼]
if st.button("답안 제출 및 자동 채점하기", type="primary"):
    total_score, results = grade_set_1(q1_1, q1_2, q1_3, q2_1, q2_2, q3_v, q3_a)
    st.divider()
    st.header(f"💯 총점: {total_score}점 / 100점")
    
    for res in results:
        if "✅" in res:
            st.success(res)
        else:
            st.error(res)
            
    if total_score >= 80:
        st.balloons()
        st.info("**평가:** 성취수준 A에 도달했습니다! 글의 맥락을 정확히 파악하고 다양한 설명 방법과 매체의 특징을 완벽히 이해하고 있습니다.")
    elif total_score >= 50:
        st.warning("**평가:** 성취수준 B~C 수준입니다. 지문의 내용을 자신의 말로 정확하게 풀어쓰거나, 조건에 맞게 설명 방법을 표기했는지 다시 점검해 보세요.")
    else:
        st.error("**평가:** 성취수준 D 수준 이하입니다. 사이드바의 핵심 개념을 다시 한번 복습하고 답안을 수정해 보세요.")
