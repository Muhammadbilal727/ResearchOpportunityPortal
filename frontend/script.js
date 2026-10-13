const API = "http://127.0.0.1:5000/api/opportunities";

const listEl = document.getElementById("list");
const messageEl = document.getElementById("message");
const detailsModal = new bootstrap.Modal(document.getElementById("detailsModal"));
const formModal = new bootstrap.Modal(document.getElementById("formModal"));

const FIELDS = ["title", "description", "research_area", "faculty_name",
  "department", "required_skills", "available_positions",
  "application_deadline", "status"];

// Prevent HTML injection from user-entered text
function esc(text) {
  const d = document.createElement("div");
  d.textContent = text;
  return d.innerHTML;
}

function showMessage(text, type = "success") {
  messageEl.innerHTML =
    `<div class="alert alert-${type} alert-dismissible fade show">${esc(text)}
     <button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>`;
  setTimeout(() => (messageEl.innerHTML = ""), 4000);
}

// ---------- READ all ----------
async function loadOpportunities() {
  try {
    const res = await fetch(API);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to load");
    renderList(data);
  } catch (err) {
    showMessage("Could not load opportunities. Is the backend running?", "danger");
  }
}

function renderList(items) {
  if (items.length === 0) {
    listEl.innerHTML = `<p class="text-muted">No opportunities yet. Click "+ Add Opportunity".</p>`;
    return;
  }
  listEl.innerHTML = items.map(o => `
    <div class="col-md-6 col-lg-4 mb-4">
      <div class="card h-100 shadow-sm">
        <div class="card-body">
          <h5 class="card-title">${esc(o.title)}</h5>
          <p class="mb-1"><strong>Faculty:</strong> ${esc(o.faculty_name)}</p>
          <p class="mb-1"><strong>Department:</strong> ${esc(o.department)}</p>
          <p class="mb-1"><strong>Deadline:</strong> ${esc(o.application_deadline)}</p>
          <span class="badge ${o.status === "Open" ? "bg-success" : "bg-secondary"}">${esc(o.status)}</span>
        </div>
        <div class="card-footer bg-white d-flex flex-wrap gap-1">
          <button class="btn btn-sm btn-outline-primary" onclick="viewOpportunity(${o.id})">View</button>
          <button class="btn btn-sm btn-outline-secondary" onclick="openEdit(${o.id})">Edit</button>
          ${o.status === "Open"
            ? `<button class="btn btn-sm btn-outline-warning" onclick="closeOpportunity(${o.id})">Close</button>`
            : ""}
          <button class="btn btn-sm btn-outline-danger" onclick="deleteOpportunity(${o.id})">Delete</button>
        </div>
      </div>
    </div>`).join("");
}

// ---------- READ one ----------
async function fetchOne(id) {
  const res = await fetch(`${API}/${id}`);
  const data = await res.json();
  if (!res.ok) {
    showMessage(data.error || "Opportunity not found.", "danger");
    loadOpportunities();
    return null;
  }
  return data;
}

async function viewOpportunity(id) {
  const o = await fetchOne(id);
  if (!o) return;
  document.getElementById("detailsTitle").textContent = o.title;
  document.getElementById("detailsBody").innerHTML = `
    <p><strong>Description:</strong> ${esc(o.description)}</p>
    <p><strong>Research Area:</strong> ${esc(o.research_area)}</p>
    <p><strong>Faculty Member:</strong> ${esc(o.faculty_name)}</p>
    <p><strong>Department:</strong> ${esc(o.department)}</p>
    <p><strong>Required Skills:</strong> ${esc(o.required_skills)}</p>
    <p><strong>Available Positions:</strong> ${esc(o.available_positions)}</p>
    <p><strong>Application Deadline:</strong> ${esc(o.application_deadline)}</p>
    <p><strong>Status:</strong> ${esc(o.status)}</p>`;
  detailsModal.show();
}

// ---------- CREATE / UPDATE form ----------
function clearForm() {
  document.getElementById("oppId").value = "";
  document.getElementById("formError").textContent = "";
  FIELDS.forEach(f => (document.getElementById(f).value = ""));
  document.getElementById("status").value = "Open";
}

function openAdd() {
  clearForm();
  document.getElementById("formTitle").textContent = "Add Opportunity";
  formModal.show();
}

async function openEdit(id) {
  const o = await fetchOne(id);
  if (!o) return;
  clearForm();
  document.getElementById("oppId").value = o.id;
  FIELDS.forEach(f => (document.getElementById(f).value = o[f]));
  document.getElementById("formTitle").textContent = "Edit Opportunity";
  formModal.show();
}

function validateForm(data) {
  const names = {
    title: "Research title", description: "Description",
    research_area: "Research area", faculty_name: "Faculty member name",
    department: "Department", required_skills: "Required skills",
    application_deadline: "Application deadline"
  };
  for (const key in names) {
    if (!data[key]) return `${names[key]} is required.`;
  }
  if (data.available_positions === "" || isNaN(data.available_positions)
      || Number(data.available_positions) < 0) {
    return "Available positions must be a number, 0 or more.";
  }
  return null;
}

async function saveOpportunity() {
  const id = document.getElementById("oppId").value;
  const data = {};
  FIELDS.forEach(f => (data[f] = document.getElementById(f).value.trim()));

  const problem = validateForm(data);
  if (problem) {
    document.getElementById("formError").textContent = problem;
    return;
  }
  data.available_positions = Number(data.available_positions);

  try {
    const res = await fetch(id ? `${API}/${id}` : API, {
      method: id ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    const result = await res.json();
    if (!res.ok) {
      document.getElementById("formError").textContent = result.error || "Something went wrong.";
      return;
    }
    formModal.hide();
    showMessage(result.message || "Saved successfully.");
    loadOpportunities();
  } catch (err) {
    document.getElementById("formError").textContent = "Cannot reach the server.";
  }
}

// ---------- Change Open -> Closed ----------
async function closeOpportunity(id) {
  const o = await fetchOne(id);
  if (!o) return;
  o.status = "Closed";
  delete o.id;
  const res = await fetch(`${API}/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(o)
  });
  const result = await res.json();
  showMessage(res.ok ? "Opportunity closed successfully." : (result.error || "Failed to close."),
              res.ok ? "success" : "danger");
  loadOpportunities();
}

// ---------- DELETE ----------
async function deleteOpportunity(id) {
  if (!confirm("Are you sure you want to delete this opportunity?")) return;
  const res = await fetch(`${API}/${id}`, { method: "DELETE" });
  const result = await res.json();
  showMessage(res.ok ? "Opportunity deleted successfully." : (result.error || "Failed to delete."),
              res.ok ? "success" : "danger");
  loadOpportunities();
}

// ---------- Start ----------
document.getElementById("addBtn").addEventListener("click", openAdd);
document.getElementById("saveBtn").addEventListener("click", saveOpportunity);
loadOpportunities();