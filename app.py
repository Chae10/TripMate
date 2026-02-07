import streamlit as st
import requests

# ---------------------------------
# 페이지 설정
# ---------------------------------
st.set_page_config(page_title="🎬 나와 어울리는 영화는?", page_icon="🎬")

st.title("🎬 나와 어울리는 영화는?")
st.write(
    "5가지 질문에 답하면 당신에게 어울리는 영화 장르와\n"
    "그에 맞는 영화를 추천해드려요 😊"
)

# ---------------------------------
# 사이드바: TMDB API Key
# ---------------------------------
TMDB_API_KEY = st.sidebar.text_input("TMDB API Key", type="password")

st.divider()

# ---------------------------------
# 장르 점수 초기화
# ---------------------------------
scores = {
    "로맨스": 0,
    "액션": 0,
    "SF": 0,
    "코미디": 0,
}

# ---------------------------------
# 선택지 → 장르 매핑
# ---------------------------------
ANSWER_MAP = {
    # Q1
    "조용한 카페에서 음악 들으며 하루를 정리한다 ☕": "로맨스",
    "친구들과 바로 여행 계획부터 세운다 ✈️": "액션",
    "집에 가서 게임이나 영화 몰아보며 현실 탈출 🎮": "SF",
    "친구들과 술 마시며 웃고 떠든다 🍻": "코미디",

    # Q2
    "감정선이 섬세한 영화나 드라마 🎞️": "로맨스",
    "스케일 큰 블록버스터, 박진감 넘치는 영화 💥": "액션",
    "세계관이 탄탄한 시리즈물 🌌": "SF",
    "아무 생각 없이 웃을 수 있는 예능이나 영화 😂": "코미디",

    # Q3
    "공감 잘하고 감수성이 풍부한 편 💭": "로맨스",
    "즉흥적이고 도전적인 성격 🔥": "액션",
    "상상력이 풍부하고 혼자만의 세계가 있다 🧠": "SF",
    "분위기 메이커, 농담 잘하는 편 😆": "코미디",

    # Q4
    "현실적인 사랑과 성장 이야기 💔": "로맨스",
    "위기 상황에서 펼쳐지는 극적인 반전 🏃‍♂️": "액션",
    "다른 세계, 미래, 초능력이 존재하는 이야기 🚀": "SF",
    "일상 속에서 벌어지는 황당한 사건들 🤡": "코미디",

    # Q5
    "여운과 감정의 깊이 💗": "로맨스",
    "긴장감과 몰입도 ⚡": "액션",
    "신선한 설정과 상상력 ✨": "SF",
    "얼마나 많이 웃었는지 😄": "코미디",
}

# ---------------------------------
# 질문
# ---------------------------------
options = list(ANSWER_MAP.keys())

q1 = st.radio("Q1. 시험이 끝난 날, 가장 먼저 하고 싶은 것은?", options[0:4], index=None)
q2 = st.radio("Q2. 주말에 시간이 생기면 어떤 콘텐츠를 찾을까?", options[4:8], index=None)
q3 = st.radio("Q3. 친구들이 말하는 나의 성격은?", options[8:12], index=None)
q4 = st.radio("Q4. 가장 끌리는 영화 속 설정은?", options[12:16], index=None)
q5 = st.radio("Q5. 영화를 보고 난 뒤, 내가 가장 중요하게 생각하는 건?", options[16:20], index=None)

answers = [q1, q2, q3, q4, q5]

st.divider()

# ---------------------------------
# TMDB 장르 ID
# ---------------------------------
GENRE_ID = {
    "액션": 28,
    "코미디": 35,
    "로맨스": 10749,
    "SF": 878,
}

# ---------------------------------
# 결과 보기
# ---------------------------------
if st.button("🎥 결과 보기"):
    if None in answers:
        st.warning("모든 질문에 답해주세요!")
    elif not TMDB_API_KEY:
        st.warning("사이드바에 TMDB API Key를 입력해주세요.")
    else:
        # 점수 계산
        for a in answers:
            genre = ANSWER_MAP[a]
            scores[genre] += 1

        # 최종 장르
        result_genre = max(scores, key=scores.get)

        st.header(f"🎉 당신에게 딱인 장르는: **{result_genre}**!")

        # ---------------------------------
        # TMDB API 호출
        # ---------------------------------
        with st.spinner("추천 영화를 불러오는 중... 🍿"):
            url = (
                "https://api.themoviedb.org/3/discover/movie"
                f"?api_key={TMDB_API_KEY}"
                f"&with_genres={GENRE_ID[result_genre]}"
                "&language=ko-KR&sort_by=popularity.desc"
            )
            response = requests.get(url)
            data = response.json()
            movies = data.get("results", [])[:5]

        st.subheader("🎬 추천 영화")

        # ---------------------------------
        # 영화 출력
        # ---------------------------------
        for movie in movies:
            cols = st.columns([1, 2])

            with cols[0]:
                if movie.get("poster_path"):
                    st.image(
                        "https://image.tmdb.org/t/p/w500" + movie["poster_path"],
                        use_container_width=True,
                    )

            with cols[1]:
                st.markdown(f"### {movie['title']}")
                st.write(f"⭐ 평점: **{movie['vote_average']} / 10**")
                st.write(movie.get("overview", "줄거리 정보가 없습니다."))

                st.info(
                    f"💡 추천 이유: "
                    f"{result_genre} 장르 특유의 분위기와 재미를 잘 느낄 수 있는 인기 작품이에요."
                )

            st.divider()
