

import requests


def search_flights(origin, destination, depart_date, adults=1):
    """항공권 검색"""

    try:
        from fast_flights import FlightData, Passengers, get_flights
    except ImportError as e:
        raise RuntimeError(
            "항공권 라이브러리를 불러오지 못했어요. "
            "requirements.txt와 설치 로그를 확인해 주세요."
        ) from e

    result = get_flights(
        flight_data=[
            FlightData(
                date=depart_date,
                from_airport=origin,
                to_airport=destination,
            )
        ],
        trip="one-way",
        seat="economy",
        passengers=Passengers(adults=int(adults)),
        fetch_mode="fallback",
    )

    return result


def search_hotels(city, checkin, checkout, api_token, guests=2):
    """Apify를 이용한 숙박 검색"""

    actor_id = "johnvc~google-hotels-search-scraper"

    url = (
        f"https://api.apify.com/v2/acts/"
        f"{actor_id}/run-sync-get-dataset-items"
    )

    payload = {
        "q": f"hotels in {city}",
        "gl": "kr",
        "hl": "ko",
        "currency": "KRW",
        "check_in_date": checkin,
        "check_out_date": checkout,
        "max_pages": 1,
    }

    response = requests.post(
        url,
        params={"token": api_token, "clean": "true"},
        json=payload,
        timeout=120,
    )

    response.raise_for_status()
    data = response.json()

    if not isinstance(data, list):
        raise ValueError("숙박 검색 결과 형식이 올바르지 않습니다.")

    return data
