const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
const $ = (s) => document.querySelector(s);

let token = null; // token tylko w pamięci (nie w localStorage), mniejsza szkoda przy ewentualnym XSS
let tripId = null;
let entries = [];

/* ---------- renderery: tu rozstrzyga się XSS ---------- */
function renderEntryUnsafe(entry, el) {
  el.innerHTML = `<p class="note">${entry.note}</p>`; // PODATNE: dane użytkownika jako HTML
}

function renderEntrySafe(entry, el) {
  const p = document.createElement("p");
  p.className = "note";
  p.textContent = entry.note; // BEZPIECZNE: znaki < i > zostają tekstem
  el.replaceChildren(p);
}

const CODE = {
  safe: `function renderEntrySafe(entry, el) {
  const p = document.createElement("p");
  p.className = "note";
  p.textContent = entry.note;   // <- tu dzieje się ochrona
  el.replaceChildren(p);
}`,
  unsafe: `function renderEntryUnsafe(entry, el) {
  el.innerHTML = \`<p class="note">\${entry.note}</p>\`;   // <- tu jest luka
}`,
};

function renderAll() {
  const mode = $("#mode").value;
  const ul = $("#entries");
  ul.replaceChildren();
  ul.className = "mode-" + mode;
  for (const entry of entries) {
    const li = document.createElement("li");
    (mode === "safe" ? renderEntrySafe : renderEntryUnsafe)(entry, li);
    ul.appendChild(li);
  }
  $("#code").textContent = CODE[mode];
}

/* ---------- API ---------- */
async function login(email, password) {
  await fetch(`${API}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  }); // 409 (konto już istnieje) ignorujemy
  const r = await fetch(`${API}/auth/login`, {
    method: "POST",
    body: new URLSearchParams({ username: email, password }),
  });
  if (!r.ok) throw new Error(`Logowanie nieudane (${r.status})`);
  token = (await r.json()).access_token;
}

async function api(path, options = {}) {
  const r = await fetch(API + path, {
    ...options,
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
  });
  if (!r.ok) throw new Error(`${r.status} ${path}`);
  return r.status === 204 ? null : r.json();
}

async function ensureTrip() {
  const trips = await api("/trips");
  tripId = trips.length ? trips[0].id : (await api("/trips", { method: "POST", body: JSON.stringify({ title: "Wyprawa testowa" }) })).id;
}

async function loadEntries() {
  entries = await api(`/trips/${tripId}/entries`);
  renderAll();
}

/* ---------- UI ---------- */
$("#preset").onchange = () => ($("#note").value = $("#preset").value);
$("#note").value = $("#preset").value;
$("#mode").onchange = renderAll;

$("#login").onclick = async () => {
  try {
    await login($("#email").value, $("#password").value);
    await ensureTrip();
    $("#status").textContent = `Zalogowano, wyprawa #${tripId}.`;
    $("#add").disabled = false;
    await loadEntries();
  } catch (e) {
    $("#status").textContent = String(e.message); // textContent, nigdy innerHTML
  }
};

$("#add").onclick = async () => {
  await api(`/trips/${tripId}/entries`, { method: "POST", body: JSON.stringify({ note: $("#note").value }) });
  await loadEntries();
};

renderAll();
