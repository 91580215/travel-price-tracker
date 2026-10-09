```python
import requests


def search_travel_prices(api_url, params=None, headers=None):
    """
    API를 이용해 여행 가격 정보를 가져오는 함수
    """
    try:
        response = requests.get(
            api_url,
            params=params,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        print(f"API 요청 오류: {e}")
        return None

    except ValueError:
        print("JSON 데이터를 읽을 수 없습니다.")
        return None
```

