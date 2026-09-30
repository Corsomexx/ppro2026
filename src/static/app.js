// Stav aplikace
let equipmentList = [];
let currentSearch = "";
let currentCategory = "";
let currentStatus = "";

// Inicializace po načtení DOM
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  loadDashboardData();
});

function setupEventListeners() {
  // Vyhledávání s debounce
  const searchInput = document.getElementById("search-input");
  let searchTimeout;
  searchInput.addEventListener("input", (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      currentSearch = e.target.value.trim();
      loadEquipment();
    }, 250);
  });

  // Filtry
  document.getElementById("filter-category").addEventListener("change", (e) => {
    currentCategory = e.target.value;
    loadEquipment();
  });

  document.getElementById("filter-status").addEventListener("change", (e) => {
    currentStatus = e.target.value;
    loadEquipment();
  });

  document.getElementById("btn-refresh").addEventListener("click", () => {
    loadDashboardData();
    showToast("Data byla obnovena", "success");
  });

  // Modály - otevření / zavření
  document.getElementById("btn-add-item").addEventListener("click", () => {
    openModal("modal-add");
  });

  document.querySelectorAll(".close-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const modalId = btn.getAttribute("data-modal");
      closeModal(modalId);
    });
  });

  // Zavření klikem mimo okno
  window.addEventListener("click", (e) => {
    if (e.target.classList.contains("modal-overlay")) {
      e.target.classList.remove("active");
    }
  });

  // Formulář: Zaevidovat kus
  document.getElementById("form-add-item").addEventListener("submit", handleAddItem);

  // Formulář: Servis
  document.getElementById("form-service").addEventListener("submit", handleServiceSubmit);
}

// Načtení dat dashboardu
async function loadDashboardData() {
  await Promise.all([loadSummaryMetrics(), loadEquipment()]);
}

async function loadSummaryMetrics() {
  try {
    const res = await fetch("/api/equipment/summary");
    if (!res.ok) throw new Error("Chyba při načítání souhrnu");
    const data = await res.json();

    document.getElementById("stat-total").textContent = data.total;
    document.getElementById("stat-available").textContent = data.available;
    document.getElementById("stat-rented").textContent = data.rented;
    document.getElementById("stat-service").textContent = data.in_service;
  } catch (err) {
    console.error("Chyba souhrnu:", err);
  }
}

async function loadEquipment() {
  const tbody = document.getElementById("equipment-table-body");
  
  try {
    const params = new URLSearchParams();
    if (currentStatus) params.append("status", currentStatus);
    if (currentCategory) params.append("category", currentCategory);
    if (currentSearch) params.append("search", currentSearch);

    const res = await fetch(`/api/equipment?${params.toString()}`);
    if (!res.ok) throw new Error("Chyba při stahování seznamu vybavení");
    equipmentList = await res.json();

    renderEquipmentTable(equipmentList);
  } catch (err) {
    console.error("Chyba načítání:", err);
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align: center; color: var(--accent-rose); padding: 2rem;">
          Chyba načítání dat z backendu. Ujistěte se, že server běží.
        </td>
      </tr>
    `;
  }
}

function renderEquipmentTable(items) {
  const tbody = document.getElementById("equipment-table-body");

  if (!items || items.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align: center; color: var(--text-muted); padding: 2.5rem;">
          Žádné kusy neodpovídají zadaným filtrům.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = items
    .map((item) => {
      const statusBadge = getStatusBadge(item.status);
      const actionButtons = getActionButtons(item);

      return `
        <tr>
          <td>
            <span class="badge badge-inv">${escapeHtml(item.inventory_number)}</span>
          </td>
          <td>
            <strong>${escapeHtml(item.name)}</strong>
            ${item.note ? `<div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 2px;">${escapeHtml(item.note)}</div>` : ""}
          </td>
          <td>${escapeHtml(item.category)}</td>
          <td>${escapeHtml(item.size)}</td>
          <td>${escapeHtml(item.condition)} (${item.year_of_purchase})</td>
          <td><strong>${item.daily_rate.toFixed(0)} Kč</strong> / den</td>
          <td>${statusBadge}</td>
          <td>
            <div style="display: flex; gap: 0.4rem; align-items: center;">
              ${actionButtons}
            </div>
          </td>
        </tr>
      `;
    })
    .join("");
}

function getStatusBadge(status) {
  switch (status) {
    case "Dostupné":
      return '<span class="badge badge-avail">● Volné na pultu</span>';
    case "Vypůjčeno":
      return '<span class="badge badge-rented">● U zákazníka</span>';
    case "V servisu":
      return '<span class="badge badge-service">● V dílně / servisu</span>';
    case "Vyřazeno":
      return '<span class="badge badge-retired">● Vyřazeno</span>';
    default:
      return `<span class="badge">${escapeHtml(status)}</span>`;
  }
}

function getActionButtons(item) {
  let buttons = "";

  if (item.status === "Dostupné") {
    buttons += `
      <button class="btn btn-secondary btn-sm" onclick="openServiceModal(${item.id}, 'send')" title="Odeslat na servis">
        🔧 Servis
      </button>
      <button class="btn btn-secondary btn-sm" onclick="toggleRent(${item.id}, 'Vypůjčeno')" title="Půjčit zákazníkovi">
        🎿 Půjčit
      </button>
    `;
  } else if (item.status === "V servisu") {
    buttons += `
      <button class="btn btn-primary btn-sm" onclick="openServiceModal(${item.id}, 'return')" title="Vrátit ze servisu">
        ✅ Ukončit servis
      </button>
    `;
  } else if (item.status === "Vypůjčeno") {
    buttons += `
      <button class="btn btn-secondary btn-sm" onclick="toggleRent(${item.id}, 'Dostupné')" title="Vrátit na pult">
        📥 Vrátit
      </button>
    `;
  }

  return buttons;
}

// Odeslání nového kusu
async function handleAddItem(e) {
  e.preventDefault();

  const payload = {
    inventory_number: document.getElementById("add-inv").value.trim().toUpperCase(),
    category: document.getElementById("add-category").value,
    name: document.getElementById("add-name").value.trim(),
    size: document.getElementById("add-size").value.trim(),
    year_of_purchase: parseInt(document.getElementById("add-year").value),
    daily_rate: parseFloat(document.getElementById("add-rate").value),
    condition: document.getElementById("add-condition").value,
    status: "Dostupné",
    note: document.getElementById("add-note").value.trim() || null,
  };

  try {
    const res = await fetch("/api/equipment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Chyba při ukládání");
    }

    closeModal("modal-add");
    document.getElementById("form-add-item").reset();
    showToast(`Kus ${payload.inventory_number} byl úspěšně zaevidován`, "success");
    loadDashboardData();
  } catch (err) {
    showToast(err.message, "error");
  }
}

// Rychlé půjčení / vrácení pro demo
async function toggleRent(itemId, targetStatus) {
  try {
    const res = await fetch(`/api/equipment/${itemId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: targetStatus }),
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Chyba změny stavu");
    }

    showToast(`Stav změněn na: ${targetStatus}`, "success");
    loadDashboardData();
  } catch (err) {
    showToast(err.message, "error");
  }
}

// Obsluha modálu servisu
function openServiceModal(itemId, actionType) {
  const item = equipmentList.find((i) => i.id === itemId);
  if (!item) return;

  document.getElementById("service-item-id").value = itemId;
  document.getElementById("service-action-type").value = actionType;
  document.getElementById("service-item-info").textContent = `${item.inventory_number} – ${item.name} (${item.size})`;

  const modalTitle = document.getElementById("service-modal-title");
  const reasonLabel = document.getElementById("service-reason-label");
  const reasonInput = document.getElementById("service-reason");
  const conditionGroup = document.getElementById("service-condition-group");
  const submitBtn = document.getElementById("btn-submit-service");

  if (actionType === "send") {
    modalTitle.textContent = "Odeslat kus do servisu / dílny";
    reasonLabel.textContent = "Důvod odeslání (popis závady či úkonu)";
    reasonInput.placeholder = "např. Broušení skluznice, seřízení bezpečnostního vázání";
    conditionGroup.style.display = "none";
    submitBtn.textContent = "Odeslat do servisu";
  } else {
    modalTitle.textContent = "Ukončit servis a vrátit na pult";
    reasonLabel.textContent = "Provedené práce v servisu";
    reasonInput.placeholder = "např. Hrany nabroušeny, vosk Toko červený aplikován";
    conditionGroup.style.display = "block";
    submitBtn.textContent = "Vrátit na pult k výpůjčkám";
  }

  reasonInput.value = "";
  openModal("modal-service");
}

async function handleServiceSubmit(e) {
  e.preventDefault();

  const itemId = document.getElementById("service-item-id").value;
  const actionType = document.getElementById("service-action-type").value;
  const reason = document.getElementById("service-reason").value.trim();

  try {
    let url = "";
    let payload = {};

    if (actionType === "send") {
      url = `/api/equipment/${itemId}/send-to-service`;
      payload = { reason_or_work: reason };
    } else {
      url = `/api/equipment/${itemId}/return-from-service`;
      payload = {
        reason_or_work: reason,
        condition_after: document.getElementById("service-condition").value,
      };
    }

    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Chyba servisu");
    }

    closeModal("modal-service");
    showToast(
      actionType === "send" ? "Kus byl odeslán do servisu" : "Kus byl vrácen ze servisu jako volný",
      "success"
    );
    loadDashboardData();
  } catch (err) {
    showToast(err.message, "error");
  }
}

// Helpers
function openModal(id) {
  document.getElementById(id).classList.add("active");
}

function closeModal(id) {
  document.getElementById(id).classList.remove("active");
}

function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span>${type === "success" ? "✓" : "⚠️"}</span>
    <div>${escapeHtml(message)}</div>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 3500);
}

function escapeHtml(text) {
  if (!text) return "";
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
