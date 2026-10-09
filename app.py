import os
print("현재 실행 파일:", os.path.abspath(__file__))
import os
import json
import crawler
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

DATA_FILE = Path("price_history.csv")

st.set_page_config(page_title="여행 최저가 트래커", page_icon="✈️", layout="wide")

st.markdown("""
<style>
    .main {background: #f7f9fc;}
    .hero {padding: 1.4rem 1.6rem; border-radius: 18px; background: linear-gradient(120deg,#eaf3ff,#f2edff); margin-bottom: 1rem;}
    .hero h1 {margin:0; color:#17345c;}
    .hero p {margin:.5rem 0 0 0; color:#415675;}
    div[data-testid="stMetric"] {background:white; padding:14px; border-radius:14px; border:1px solid #e5eaf2;}
</style>
<div class="hero">
<h1>✈️ 여행 최저가 변동 측정기</h1>
<p>항공권과 숙박 가격을 검색하고, 저장된 가격을 비교해 변동을 확인해요.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ API 설정")
    st.caption("키는 코드에 직접 적지 말고 환경 변수나 Streamlit Secrets에 보관하세요.")
    st.markdown("**Apify 숙박 검색**")
    apify_token_input = st.text_input("Apify API Token (선택)", type="password", help="Apify 계정에서 발급받은 토큰")
    st.markdown("---")
    st.markdown("**항공권 검색**")
    st.info("fast-flights는 Google Flights 결과를 조회하는 비공식 라이브러리예요. 검색이 실패하거나 결과 형식이 달라질 수 있어요.")
    st.markdown("[fast-flights 안내](https://pypi.org/project/fast-flights/)")
    st.markdown("[Apify 숙박 스크레이퍼](https://apify.com/johnvc/google-hotels-search-scraper)")

if "results" not in st.session_state:
    st.session_state.results = []
if "message" not in st.session_state:
    st.session_state.message = ""

tab_flight, tab_hotel, tab_history = st.tabs(["✈️ 항공권", "🏨 숙박", "📈 가격 기록"])

def add_history(kind, query, item, price, currency="KRW", note=""):
    row = {
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "kind": kind,
        "query": query,
        "item": item,
        "price": float(price),
        "currency": currency,
        "note": note,
    }
    df_new = pd.DataFrame([row])
    if DATA_FILE.exists():
        old = pd.read_csv(DATA_FILE)
        df_new = pd.concat([old, df_new], ignore_index=True)
    df_new.to_csv(DATA_FILE, index=False)
    return row

def read_history():
    if DATA_FILE.exists():
        try:
            return pd.read_csv(DATA_FILE)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame(columns=["checked_at","kind","query","item","price","currency","note"])

with tab_flight:
    st.subheader("항공권 검색")
    st.caption("출발·도착 공항 코드는 IATA 3자리 코드로 입력하세요. 예: ICN, NRT, LAX")
    c1,c2,c3 = st.columns(3)
    origin = c1.text_input("출발 공항", "ICN", key="origin").strip().upper()
    destination = c2.text_input("도착 공항", "NRT", key="destination").strip().upper()
    depart_date = c3.date_input("출발 날짜", value=date.today(), min_value=date.today(), key="flight_date")
    adults = st.number_input("성인 인원", min_value=1, max_value=9, value=1, key="adults")
    if st.button("항공권 가격 검색", type="primary", key="search_flight"):
        if len(origin) != 3 or len(destination) != 3:
            st.error("공항 코드는 ICN처럼 영문 3자리로 입력해 주세요.")
        else:
            try:
                from fast_flights import FlightData, Passengers, get_flights
                with st.spinner("항공권 검색 중..."):
                    result = get_flights(
                        flight_data=[FlightData(date=depart_date.strftime("%Y-%m-%d"), from_airport=origin, to_airport=destination)],
                        trip="one-way",
                        seat="economy",
                        passengers=Passengers(adults=int(adults)),
                        fetch_mode="fallback",
                    )
                st.write("### 검색 결과")
                st.write(result)
                st.warning("라이브러리 결과 형식은 버전에 따라 달라질 수 있어요. 아래 입력란에 실제로 확인한 가격을 기록하면 변동 그래프에 반영됩니다.")
                manual_price = st.number_input("기록할 항공권 가격 (원)", min_value=0, value=0, step=1000, key="flight_price")
                if st.button("항공권 가격 기록 저장", key="save_flight"):
                    if manual_price > 0:
                        add_history("항공권", f"{origin} → {destination} / {depart_date}", "검색 결과", manual_price)
                        st.success("가격 기록을 저장했어요!")
                    else:
                        st.error("0보다 큰 가격을 입력해 주세요.")
            except Exception as e:
                st.error("항공권 검색에 실패했어요. 설치 버전, 인터넷 연결, Google Flights 응답을 확인해 주세요.")
                st.code(str(e))
                st.info("검색이 안 되더라도 아래에서 가격을 직접 기록할 수 있어요.")
    st.markdown("#### 직접 가격 기록")
    fc1,fc2 = st.columns(2)
    flight_label = fc1.text_input("항공권 이름/조건", f"{origin} → {destination} / {depart_date}", key="flight_label")
    flight_manual = fc2.number_input("확인한 가격 (원)", min_value=0, value=0, step=1000, key="flight_manual")
    if st.button("직접 입력한 항공권 가격 저장", key="manual_save_flight"):
        if flight_manual > 0:
            add_history("항공권", f"{origin} → {destination} / {depart_date}", flight_label, flight_manual)
            st.success("가격 기록을 저장했어요.")
        else:
            st.error("0보다 큰 가격을 입력해 주세요.")

with tab_hotel:
    st.subheader("숙박 검색")
    hc1,hc2 = st.columns(2)
    city = hc1.text_input("도시 또는 지역", "Tokyo", key="hotel_city")
    guests = hc2.number_input("투숙 인원", min_value=1, max_value=12, value=2, key="hotel_guests")
    hc3,hc4 = st.columns(2)
    checkin = hc3.date_input("체크인", value=date.today(), min_value=date.today(), key="checkin")
    checkout = hc4.date_input("체크아웃", value=date.today() + timedelta(days=1), min_value=date.today(), key="checkout")
    if st.button("숙박 가격 검색", type="primary", key="search_hotel"):
        if checkout <= checkin:
            st.error("체크아웃 날짜는 체크인보다 뒤여야 해요.")
        elif not apify_token_input:
            st.warning("숙박 검색을 하려면 왼쪽 사이드바에 Apify API Token을 입력해 주세요. 토큰은 코드나 GitHub에 올리지 마세요.")
        else:
            try:
                import requests
                actor_id = "johnvc~google-hotels-search-scraper"
                url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"
                payload = {
                    "q": f"hotels in {city}",
                    "gl": "kr",
                    "hl": "ko",
                    "currency": "KRW",
                    "check_in_date": checkin.isoformat(),
                    "check_out_date": checkout.isoformat(),
                    "max_pages": 1
                }
                with st.spinner("Apify를 통해 숙박 검색 중..."):
                    response = requests.post(url, params={"token": apify_token_input, "clean": "true"}, json=payload, timeout=120)
                if response.status_code >= 400:
                    st.error(f"Apify 응답 오류: HTTP {response.status_code}")
                    st.code(response.text[:2000])
                else:
                    data = response.json()
                    if not isinstance(data, list):
                        st.warning("검색 응답이 예상한 목록 형식이 아니에요.")
                        st.json(data)
                    elif not data:
                        st.warning("검색 결과가 비어 있어요. 검색어와 날짜를 확인해 주세요.")
                    else:
                        st.success(f"{len(data)}개 결과를 받았어요.")
                        st.json(data[:10])
                        st.caption("숙소 이름과 가격 필드 구조는 Actor 결과 버전에 따라 다를 수 있어요. 확인한 총액은 아래 가격 기록에 저장할 수 있습니다.")
            except Exception as e:
                st.error("숙박 검색 요청에 실패했어요. Apify 토큰, Actor 입력 형식, 사용량을 확인해 주세요.")
                st.code(str(e))
    st.markdown("#### 숙박 가격 기록")
    hotel_label = st.text_input("숙소 이름/조건", f"{city} / {checkin}–{checkout}", key="hotel_label")
    hotel_price = st.number_input("확인한 총 숙박 가격 (원)", min_value=0, value=0, step=1000, key="hotel_price")
    if st.button("숙박 가격 기록 저장", key="save_hotel"):
        if checkout <= checkin:
            st.error("체크아웃 날짜는 체크인보다 뒤여야 해요.")
        elif hotel_price > 0:
            add_history("숙박", f"{city} / {checkin}–{checkout} / {guests}명", hotel_label, hotel_price)
            st.success("숙박 가격 기록을 저장했어요.")
        else:
            st.error("0보다 큰 가격을 입력해 주세요.")

with tab_history:
    st.subheader("가격 기록과 변동")
    hist = read_history()
    if hist.empty:
        st.info("아직 기록이 없어요. 항공권 또는 숙박 탭에서 가격을 저장해 보세요.")
    else:
        hist["price"] = pd.to_numeric(hist["price"], errors="coerce")
        latest = hist.sort_values("checked_at").iloc[-1]
        m1,m2,m3 = st.columns(3)
        m1.metric("저장한 기록", f"{len(hist)}건")
        m2.metric("최근 기록 가격", f"{latest['price']:,.0f}원")
        m3.metric("최근 기록 종류", str(latest["kind"]))
        hist["checked_at"] = pd.to_datetime(hist["checked_at"], errors="coerce")
        fig = px.line(hist.sort_values("checked_at"), x="checked_at", y="price", color="item", markers=True,
                      title="저장한 가격 변화", labels={"checked_at":"기록 시간","price":"가격 (원)","item":"항공권/숙소"})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(hist.sort_values("checked_at", ascending=False), use_container_width=True, hide_index=True)
        csv = hist.to_csv(index=False).encode("utf-8-sig")
        st.download_button("기록 CSV 다운로드", data=csv, file_name="price_history.csv", mime="text/csv")
        if st.button("모든 가격 기록 삭제", type="secondary"):
            DATA_FILE.unlink(missing_ok=True)
            st.success("기록을 삭제했어요. 화면을 새로고침하면 반영돼요.")

st.markdown("---")
st.caption("프로젝트용 시제품입니다. 실제 가격은 검색 시점과 조건에 따라 달라질 수 있으며, 예약·결제 기능은 포함하지 않습니다.")
