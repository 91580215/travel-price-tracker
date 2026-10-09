
const $ = (selector) => document.querySelector(selector);

let currentCategory = "flight";
let currentResults = [];
let currentNights = 1;

function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[char]);
}

function setLocalDate(input, daysFromToday) {
  const d = new Date();
  d.setDate(d.getDate() + daysFromToday);

  const localDate = [
    d.getFullYear(),
    String(d.getMonth() + 1).padStart(2, "0"),
    String(d.getDate()).padStart(2, "0")
  ].join("-");

  input.value = localDate;
  input.min = $("#today-placeholder")?.value || "";
}

function showStatus(message, isError = false) {
  const status = $("#status");
  status.textContent = message;
  status.style.color = isError ? "#c0392b" : "#173b65";
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "요청을 처리하지 못했어요.");
  }

  return data;
}

// 항공권 / 숙소 탭 전환
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    currentCategory = tab.dataset.tab;

    document.querySelectorAll(".tab").forEach((item) => {
      item.classList.toggle("active", item === tab);
    });

    $("#flight-form").classList.toggle(
      "hidden",
      currentCategory !== "flight"
    );

    $("#hotel-form").classList.toggle(
      "hidden",
      currentCategory !== "hotel"
    );

    $("#results-title").textContent =
      currentCategory === "flight"
        ? "항공권 검색 결과"
        : "숙소 검색 결과";

    $("#results").innerHTML = `
      <div class="empty-state">
        <span>🌍</span>
        <p>여행 정보를 입력하고 검색해 보세요!</p>
      </div>
    `;

    showStatus("");
  });
});

// 검색 결과 표시
function renderResults(results, category) {
  currentResults = results;

  const isHotel = category === "hotel";
  const icon = isHotel ? "🏨" : "✈️";

  if (results.length === 0) {
    $("#results").innerHTML = `
      <div class="empty-state">검색 결과가 없습니다.</div>
    `;
    return;
  }

  $("#results").innerHTML = results.map((item, index) => {
    const totalPrice = isHotel
      ? item.price * currentNights
      : item.price;

    return `
      <article class="result-card">
        <div class="result-icon">${icon}</div>
        <h3>${escapeHTML(item.name)}</h3>
        <p class="muted">
          ${isHotel ? `${currentNights}박 총액 · 예시 가격` : "예시 항공권 가격"}
        </p>
        <p class="price">${totalPrice.toLocaleString("ko-KR")}원</p>
        <button class="save-button" data-save-index="${index}">
          ♡ 가격 기록하기
        </button>
      </article>
    `;
  }).join("");

  $("#results").querySelectorAll("[data-save-index]").forEach((button) => {
    button.addEventListener("click", async () => {
      const item = currentResults[Number(button.dataset.saveIndex)];

      const price = isHotel
        ? item.price * currentNights
        : item.price;

      try {
        await apiRequest("/api/history", {
          method: "POST",
          body: JSON.stringify({
            category: isHotel ? "숙소" : "항공권",
            item_name: item.name,
            price
          })
        });

        showStatus("✅ 가격을 기록했어요!");
        await loadHistory();
      } catch (error) {
        showStatus(error.message, true);
      }
    });
  });
}

// 항공권 검색
$("#flight-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const origin = $("#origin").value.trim();
  const destination = $("#destination").value.trim();
  const departDate = $("#depart-date").value;

  if (origin === destination) {
    showStatus("출발지와 도착지를 다르게 입력해 주세요.", true);
    return;
  }

  showStatus("항공권 검색 중...");

  try {
    const data = await apiRequest("/api/search/flights", {
      method: "POST",
      body: JSON.stringify({
        origin,
        destination,
        depart_date: departDate
      })
    });

    $("#results-title").textContent =
      `${data.route} 항공권 검색 결과`;

    renderResults(data.results, "flight");

    showStatus(`ℹ️ ${data.message}`);
  } catch (error) {
    showStatus(error.message, true);
  }
});

// 숙소 검색
$("#hotel-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const city = $("#city").value.trim();
  const checkin = $("#checkin").value;
  const checkout = $("#checkout").value;

  if (!city || !checkin || !checkout) {
    showStatus("도시와 숙박 날짜를 모두 입력해 주세요.", true);
    return;
  }

  if (checkout <= checkin) {
    showStatus("체크아웃 날짜는 체크인 이후여야 해요.", true);
    return;
  }

  showStatus("숙소 검색 중...");

  try {
    const data = await apiRequest("/api/search/hotels", {
      method: "POST",
      body: JSON.stringify({ city, checkin, checkout })
    });

    currentNights = data.nights;

    $("#results-title").textContent =
      `${data.city} 숙소 검색 결과`;

    renderResults(data.results, "hotel");

    showStatus(`ℹ️ ${data.message}`);
  } catch (error) {
    showStatus(error.message, true);
  }
});

// 가격 기록 불러오기
async function loadHistory() {
  try {
    const records = await apiRequest("/api/history");

    if (records.length === 0) {
      $("#history-chart").innerHTML =
        '<p class="muted">저장한 가격이 여기에 표시됩니다.</p>';
      $("#history-list").innerHTML = "";
      return;
    }

    const maxPrice = Math.max(...records.map((item) => item.price), 1);

    $("#history-chart").innerHTML = records.map((item) => {
      const width = Math.max(3, (item.price / maxPrice) * 100);

      return `
        <div class="bar-row">
          <span>${escapeHTML(item.item_name)}</span>
          <div class="bar-track">
            <div class="bar-fill" style="width:${width}%"></div>
          </div>
          <strong class="bar-value">
            ${Number(item.price).toLocaleString("ko-KR")}원
          </strong>
        </div>
      `;
    }).join("");

    $("#history-list").innerHTML = records.map((item) => `
      <div class="history-item">
        <div>
          <strong>${escapeHTML(item.item_name)}</strong>
          <div class="muted">
            ${escapeHTML(item.category)} ·
            ${escapeHTML(item.created_at)}
          </div>
          <strong>${Number(item.price).toLocaleString("ko-KR")}원</strong>
        </div>
        <button class="delete-button" data-delete-id="${item.id}">
          삭제
        </button>
      </div>
    `).join("");

    $("#history-list").querySelectorAll("[data-delete-id]").forEach((button) => {
      button.addEventListener("click", async () => {
        try {
          await apiRequest(
            `/api/history/${button.dataset.deleteId}`,
            { method: "DELETE" }
          );

          showStatus("가격 기록을 삭제했어요.");
          await loadHistory();
        } catch (error) {
          showStatus(error.message, true);
        }
      });
    });
  } catch (error) {
    showStatus("가격 기록을 불러오지 못했어요.", true);
  }
}

// 날짜 기본값 설정
const today = new Date();
today.setMinutes(today.getMinutes() - today.getTimezoneOffset());
const todayString = today.toISOString().slice(0, 10);

const plusDays = (days) => {
  const d = new Date(`${todayString}T12:00:00`);
  d.setDate(d.getDate() + days);

  return [
    d.getFullYear(),
    String(d.getMonth() + 1).padStart(2, "0"),
    String(d.getDate()).padStart(2, "0")
  ].join("-");
};

$("#depart-date").min = todayString;
$("#depart-date").value = plusDays(30);

$("#checkin").min = todayString;
$("#checkin").value = plusDays(30);

$("#checkout").min = plusDays(31);
$("#checkout").value = plusDays(33);

$("#checkin").addEventListener("change", () => {
  const nextDay = new Date(`${$("#checkin").value}T12:00:00`);
  nextDay.setDate(nextDay.getDate() + 1);

  const minCheckout = [
    nextDay.getFullYear(),
    String(nextDay.getMonth() + 1).padStart(2, "0"),
    String(nextDay.getDate()).padStart(2, "0")
  ].join("-");

  $("#checkout").min = minCheckout;

  if ($("#checkout").value < minCheckout) {
    $("#checkout").value = minCheckout;
  }
});

$("#refresh-history").addEventListener("click", loadHistory);

loadHistory();
