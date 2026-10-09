const flightTab = document.getElementById("flightTab");
const hotelTab = document.getElementById("hotelTab");

const flightForm = document.getElementById("flightForm");
const hotelForm = document.getElementById("hotelForm");

const results = document.getElementById("results");
const resultCount = document.getElementById("resultCount");
const statusMessage = document.getElementById("statusMessage");

const historyList = document.getElementById("historyList");
const historyMessage = document.getElementById("historyMessage");
const refreshHistory = document.getElementById("refreshHistory");

let currentResults = [];


// HTML에 안전하게 표시하기 위한 함수
function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, function (char) {
        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        };

        return entities[char];
    });
}


// 가격을 원화 형식으로 표시
function formatPrice(price) {
    return Number(price).toLocaleString("ko-KR") + "원";
}


// 서버에 요청을 보내는 공통 함수
async function apiRequest(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || "요청에 실패했어요.");
    }

    return data;
}


// 항공권 탭
flightTab.addEventListener("click", function () {
    flightTab.classList.add("active");
    hotelTab.classList.remove("active");

    flightForm.classList.remove("hidden");
    hotelForm.classList.add("hidden");

    statusMessage.textContent = "항공권 정보를 입력하고 검색해 보세요!";
});


// 숙소 탭
hotelTab.addEventListener("click", function () {
    hotelTab.classList.add("active");
    flightTab.classList.remove("active");

    hotelForm.classList.remove("hidden");
    flightForm.classList.add("hidden");

    statusMessage.textContent = "숙소 정보를 입력하고 검색해 보세요!";
});


// 검색 결과를 화면에 표시
function renderResults(items) {
    results.innerHTML = "";
    resultCount.textContent = items.length + "개";

    if (items.length === 0) {
        statusMessage.textContent = "검색 결과가 없어요.";
        return;
    }

    statusMessage.textContent =
        "가격이 저렴한 순서로 표시했어요. 아래 가격은 테스트용 예시예요.";

    items.forEach(function (item, index) {
        const card = document.createElement("article");

        card.className = "result-card";

        if (index === 0) {
            card.classList.add("best");
        }

        card.innerHTML = `
            <div class="card-info">
                ${index === 0
                    ? '<span class="best-label">최저가 예시</span>'
                    : ""}
                <h3>${escapeHTML(item.title)}</h3>
                <p>📅 ${escapeHTML(item.travel_date)}</p>
                <p>판매처: ${escapeHTML(item.provider)}</p>
            </div>

            <div class="card-actions">
                <div class="price">${formatPrice(item.price)}</div>
                <button class="secondary-button save-button" type="button">
                    가격 저장
                </button>
            </div>
        `;

        const saveButton = card.querySelector(".save-button");

        saveButton.addEventListener("click", async function () {
            saveButton.disabled = true;

            try {
                await apiRequest("/api/history", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(item)
                });

                alert("가격을 저장했어요! 😊");
                await loadHistory();
            } catch (error) {
                alert(error.message);
            } finally {
                saveButton.disabled = false;
            }
        });

        results.appendChild(card);
    });
}


// 항공권 검색
flightForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const button = flightForm.querySelector(".primary-button");
    button.disabled = true;
    button.textContent = "검색 중...";

    results.innerHTML = "";
    resultCount.textContent = "0개";
    statusMessage.textContent = "항공권을 검색하고 있어요.";

    const searchData = {
        origin: document.getElementById("origin").value.trim(),
        destination: document.getElementById("flightDestination").value.trim(),
        date: document.getElementById("flightDate").value
    };

    try {
        currentResults = await apiRequest("/api/search/flights", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(searchData)
        });

        renderResults(currentResults);
    } catch (error) {
        statusMessage.textContent = error.message;
    } finally {
        button.disabled = false;
        button.textContent = "항공권 검색";
    }
});


// 숙소 검색
hotelForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const button = hotelForm.querySelector(".primary-button");
    button.disabled = true;
    button.textContent = "검색 중...";

    results.innerHTML = "";
    resultCount.textContent = "0개";
    statusMessage.textContent = "숙소를 검색하고 있어요.";

    const searchData = {
        destination: document.getElementById("hotelDestination").value.trim(),
        checkin: document.getElementById("checkin").value,
        checkout: document.getElementById("checkout").value
    };

    try {
        currentResults = await apiRequest("/api/search/hotels", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(searchData)
        });

        renderResults(currentResults);
    } catch (error) {
        statusMessage.textContent = error.message;
    } finally {
        button.disabled = false;
        button.textContent = "숙소 검색";
    }
});


// 저장된 가격 기록 표시
async function loadHistory() {
    historyMessage.textContent = "저장 기록을 불러오는 중...";
    historyList.innerHTML = "";

    try {
        const items = await apiRequest("/api/history");

        if (items.length === 0) {
            historyMessage.textContent =
                "아직 저장한 가격이 없어요. 검색 결과에서 가격을 저장해 보세요!";
            return;
        }

        historyMessage.textContent = "저장한 가격: " + items.length + "개";

        items.forEach(function (item) {
            const card = document.createElement("article");

            card.className = "history-card";

            const typeName = item.kind === "flight" ? "✈️ 항공권" : "🏨 숙소";

            card.innerHTML = `
                <div class="card-info">
                    <p>${typeName}</p>
                    <h3>${escapeHTML(item.title)}</h3>
                    <p>📅 ${escapeHTML(item.travel_date)}</p>
                    <p>판매처: ${escapeHTML(item.provider)}</p>
                    <p>저장 시각: ${escapeHTML(item.created_at)}</p>
                </div>

                <div class="card-actions">
                    <div class="price">${formatPrice(item.price)}</div>
                    <button class="delete-button" type="button">
                        삭제
                    </button>
                </div>
            `;

            const deleteButton = card.querySelector(".delete-button");

            deleteButton.addEventListener("click", async function () {
                const confirmed = confirm("이 가격 기록을 삭제할까요?");

                if (!confirmed) {
                    return;
                }

                deleteButton.disabled = true;

                try {
                    await apiRequest("/api/history/" + item.id, {
                        method: "DELETE"
                    });

                    await loadHistory();
                } catch (error) {
                    alert(error.message);
                    deleteButton.disabled = false;
                }
            });

            historyList.appendChild(card);
        });
    } catch (error) {
        historyMessage.textContent =
            "기록을 불러오지 못했어요. 서버가 실행 중인지 확인해 주세요.";
    }
}


// 기록 새로고침 버튼
refreshHistory.addEventListener("click", loadHistory);


// 페이지를 열 때 저장 기록 불러오기
loadHistory();
