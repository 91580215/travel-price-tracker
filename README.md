# 여행 최저가 변동 측정기

항공권(fast-flights)과 숙박(Apify Google Hotels Search Scraper)을 연결하는 프로젝트용 Streamlit 웹 앱 시작 코드입니다.

## 실행 방법

1. Python 3.10 이상을 설치합니다.
2. 프로젝트 폴더에서 터미널을 열고 아래를 실행합니다.

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

3. 필요한 라이브러리 설치:

```bash
pip install -r requirements.txt
```

4. 앱 실행:

```bash
streamlit run app.py
```

브라우저에서 Streamlit이 알려주는 주소를 엽니다.

## API/검색 관련 주의사항

- `fast-flights`는 Google Flights 검색 결과를 이용하는 비공식 라이브러리입니다. 결과가 달라지거나 검색이 실패할 수 있습니다.
- 숙박 탭에서는 Apify API Token이 필요합니다. Apify Actor의 입력 필드 이름은 버전에 따라 달라질 수 있으므로 Actor 페이지의 **Input** 탭에서 실제 스키마를 확인하고, `app.py`의 `payload`를 맞춰야 합니다.
- API 토큰을 Python 코드에 직접 넣거나 공개 GitHub에 올리지 마세요. 이 앱에서는 토큰을 사이드바에 입력하도록 했습니다.
- 가격 기록은 실행 폴더의 `price_history.csv`에 저장됩니다. 배포 환경에 따라 파일이 영구 보존되지 않을 수 있습니다.
- 이 앱은 프로젝트용 시제품이며 예약/결제 기능이 없습니다.

## 주요 기능

- 항공권 검색 시도
- 숙박 검색 API 요청
- 항공권/숙박 가격을 직접 기록
- 저장한 가격의 선 그래프와 CSV 다운로드

## 배포

Streamlit Community Cloud 등으로 배포할 수 있지만, 토큰을 공개 저장소에 넣지 말고 배포 플랫폼의 Secrets 기능을 사용하세요. 공개 서비스로 배포하기 전에는 API 사용 조건, 비용, 속도 제한, 데이터 수집 권한을 확인하세요.
