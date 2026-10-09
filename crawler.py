

import requests


def search_flights(origin, destination, depart_date, adults=1):
    """항공권 검색 - fast-flights 3.x"""

    from fast_flights import (
        FlightQuery,
        Passengers,
        create_query,
        get_flights,
    )

    query = create_query(
        flights=[
            FlightQuery(
                date=depart_date,
                from_airport=origin,
                to_airport=destination,
            )
        ],
        seat="economy",
        trip="one-way",
        passengers=Passengers(adults=int(adults)),
    )

    return get_flights(query)


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
