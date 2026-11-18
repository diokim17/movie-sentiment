"""
Streamlit을 사용하여 영화 목록을 조회하는 웹 화면을 제공합니다.
"""

import os

import requests
import streamlit as st


# FastAPI 서버 주소 설정
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Streamlit 페이지 설정
st.set_page_config(
    page_title="Movie Review",
    layout="wide",
)

st.title("Movie Review")
st.write("영화 정보와 사용자 리뷰 및 감성 분석 결과를 확인할 수 있습니다.")

# FastAPI에서 전체 영화 목록 조회
def get_movies() -> list[dict]:
    response = requests.get(
        f"{API_BASE_URL}/movies",
        timeout=10,
    )
    response.raise_for_status()

    return response.json()


# 선택한 영화의 리뷰를 등록하고 GPT 감성 분석 결과를 표시합니다.
def show_review_form(movie_id: int) -> None:
    with st.form(f"review_form_{movie_id}", clear_on_submit=True):
        content = st.text_area("리뷰 내용")
        rating = st.slider(
            "평점",
            min_value=0.0,
            max_value=5.0,
            value=3.0,
            step=0.5,
        )

        submitted = st.form_submit_button("리뷰 등록")

        if submitted:
            if not content.strip():
                st.warning("리뷰 내용을 입력해 주세요.")
                return

            review_data = {
                "content": content.strip(),
                "rating": rating,
            }

            try:
                with st.spinner("GPT가 리뷰의 감성을 분석하고 있습니다..."):
                    response = requests.post(
                        f"{API_BASE_URL}/movies/{movie_id}/reviews",
                        json=review_data,
                        timeout=60,
                    )
                    response.raise_for_status()

            except requests.RequestException as error:
                st.error(f"리뷰 등록에 실패했습니다: {error}")
                return

            st.success("리뷰 등록 및 감성 분석이 완료되었습니다.")
            st.rerun()

# 선택한 영화의 리뷰 목록과 감성 분석 결과 표시
def show_reviews(movie_id: int) -> None:
    try:
        response = requests.get(
            f"{API_BASE_URL}/movies/{movie_id}/reviews",
            timeout=10,
        )
        response.raise_for_status()
        reviews = response.json()

    except requests.RequestException as error:
        st.error(f"리뷰 조회에 실패했습니다: {error}")
        return

    if not reviews:
        st.info("아직 등록된 리뷰가 없습니다.")
        return

    average_rating = sum(review["rating"] for review in reviews) / len(reviews)

    st.write(f"평균 평점: {average_rating:.1f} / 5.0")
    st.write(f"전체 리뷰: {len(reviews)}개")

    sentiment_labels = {
        "positive": "긍정",
        "negative": "부정",
        "neutral": "중립",
    }

    for review in reviews:
        with st.container(border=True):
            st.write(f"평점: {review['rating']:.1f} / 5.0")
            st.write(review["content"])
            st.write(
                f"감성 분석: {sentiment_labels.get(review['sentiment'], '알 수 없음')}"
            )
            st.caption(review["sentiment_reason"])

# 영화 목록을 화면에 표시
def show_movies() -> None:
    st.subheader("영화 목록")

    try:
        movies = get_movies()
    except requests.RequestException as error:
        st.error(f"영화 목록을 불러오지 못했습니다: {error}")
        return

    if not movies:
        st.info("등록된 영화가 없습니다.")
        return

    for movie in movies:
        col1, col2 = st.columns([1, 3])

        with col1:
            st.image(
                movie["poster_url"],
                width="stretch",
            )

        with col2:
            st.subheader(movie["title"])
            st.write(f"감독: {movie['director']}")
            st.write(f"개봉일: {movie['release_date']}")
            st.write(f"장르: {movie['genre']}")

        with st.expander(f"{movie['title']} - 리뷰 보기 및 작성"):
            show_reviews(movie["id"])
            st.divider()
            show_review_form(movie["id"])

        st.divider()

# 영화 등록 폼을 표시하고 FastAPI에 등록 요청
def show_movie_form() -> None:
    st.subheader("영화 등록")

    with st.form("movie_form", clear_on_submit=True):
        title = st.text_input("영화 제목")
        release_date = st.date_input("개봉일")
        director = st.text_input("감독")
        genre = st.text_input("장르")
        poster_url = st.text_input("포스터 URL")

        submitted = st.form_submit_button("영화 등록")

        if submitted:
            if not all([title.strip(), director.strip(), genre.strip(), poster_url.strip()]):
                st.warning("모든 항목을 입력해 주세요.")
                return

            movie_data = {
                "title": title.strip(),
                "release_date": release_date.isoformat(),
                "director": director.strip(),
                "genre": genre.strip(),
                "poster_url": poster_url.strip(),
            }

            try:
                response = requests.post(
                    f"{API_BASE_URL}/movies",
                    json=movie_data,
                    timeout=10,
                )
                response.raise_for_status()

            except requests.RequestException as error:
                st.error(f"영화 등록에 실패했습니다: {error}")
                return

            st.success("영화가 등록되었습니다.")
            st.rerun()

show_movie_form()
show_movies()