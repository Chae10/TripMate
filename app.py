import streamlit as st
from openai import OpenAI
from datetime import date

# --------------------
# 페이지 설정
# --------------------
st.set_page_config(
    page_title="✈️ TripMate - AI 여행 추천",
    page_icon="✈️",
    layout="centered"
)

# --------------------
# 사이드바: API Key (저장 안 됨)
# --------------------
st.sidebar.title("🔐 OpenAI API Key")
api_key = st.sidebar.text_input(
    "API Key 입력",
    type="password",
    help="입력한 키는 저장되지 않고 현재 세션에서만 사용됩니다."
)
st.sidebar.caption("※ 새로고침 시 키는 사라집니다.")

# --------------------
# 제목 & 소개
# --------------------
st.title("✈️ TripMate")
st.subheader("AI가 일정 · 예산 · 컨셉 · 기후까지 고려해 여행지를 추천해드립니다")

st.divider()

# --------------------
# 질문 0️⃣ 현재 위치
# --------------------
current_location = st.text_input(
    "📍 현재 어디에 계신가요?",
    placeholder="예: 대한민국 서울"
)

# --------------------
# 질문 1️⃣ 동행
# --------------------
companion = st.radio(
    "1️⃣ 누구와 여행을 가시나요?",
    ["혼자", "친구", "연인", "가족", "부모님 / 어르신 포함"]
)

# --------------------
# 질문 2️⃣ 여행 날짜 범위
# --------------------
date_range = st.date_input(
    "2️⃣ 여행 날짜를 선택해 주세요 (출발일 ~ 도착일)",
    value=(date.today(), date.today())
)

travel_days = None
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    travel_days = (end_date - start_date).days + 1
    if travel_days > 0:
        st.caption(f"🗓️ 여행 기간: **{travel_days}일**")
    else:
        st.warning("⚠️ 도착일은 출발일 이후여야 합니다.")

# --------------------
# 질문 3️⃣ 1인당 여행 예산
# --------------------
budget = st.text_area(
    "3️⃣ 1인당 여행 예산은 어느 정도인가요?",
    placeholder="예: 항공 포함 1인당 150만 원 정도를 생각하고 있어요."
)

# --------------------
# 질문 4️⃣ 여행 컨셉 (복수 선택)
# --------------------
concepts = st.multiselect(
    "4️⃣ 원하는 여행 컨셉을 모두 선택해 주세요",
    ["힐링 / 휴식", "관광 / 명소", "맛집 / 미식", "자연 / 풍경", "액티비티", "도시 감성"]
)

# --------------------
# 질문 5️⃣ 기타 조건
# --------------------
extra = st.text_area(
    "5️⃣ 기타 원하는 점이나 피하고 싶은 것이 있다면?",
    placeholder="예: 너무 더운 곳은 피하고 싶고, 이동이 많은 일정은 부담돼요."
)

st.divider()

# --------------------
# AI 추천 버튼
# --------------------
if st.button("AI 여행지 추천받기"):

    # 입력 검증
    if not api_key:
        st.error("⚠️ 사이드바에 OpenAI API Key를 입력해 주세요.")
        st.stop()

    if not current_location or not travel_days or travel_days <= 0:
        st.error("⚠️ 현재 위치와 올바른 여행 날짜를 입력해 주세요.")
        st.stop()

    if not concepts:
        st.error("⚠️ 최소 하나 이상의 여행 컨셉을 선택해 주세요.")
        st.stop()

    client = OpenAI(api_key=api_key)
    concept_text = ", ".join(concepts)

    # --------------------
    # 여행지 추천 요청
    # --------------------
    with st.spinner("🔍 AI가 여행지를 분석 중입니다..."):
        prompt = f"""
        다음 사용자 정보를 바탕으로 여행지 3곳을 추천해줘.

        반드시 고려할 요소:
        - 여행 날짜({start_date} ~ {end_date})의 일반적인 기후
        - 여행 기간 {travel_days}일에 적합한 이동 범위
        - 1인당 예산 수준
        - 동행 유형
        - 선택한 여행 컨셉 (복수 가능)

        [사용자 정보]
        - 현재 위치: {current_location}
        - 동행: {companion}
        - 여행 기간: {travel_days}일
        - 1인당 예산: {budget}
        - 여행 컨셉: {concept_text}
        - 기타 조건: {extra}

        [출력 형식 – 반드시 지켜]
        여행지명 | 추천 이유 (3~4문장)

        위 형식으로 정확히 3줄 작성해줘.
        """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "너는 여행 기획 전문가야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )

    results = response.choices[0].message.content.strip().split("\n")

    # --------------------
    # 결과 카드 출력
    # --------------------
    st.subheader("✨ AI 추천 여행지 TOP 3")

    for line in results:
        try:
            place, reason = line.split("|", 1)
        except ValueError:
            continue

        with st.container(border=True):
            st.markdown(f"### 📍 {place.strip()}")
            st.write(reason.strip())