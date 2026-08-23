/* =========================================================
   PadhAi — script.js
   Vanilla JS. Organized as:
   1. Config & API layer (FastAPI-ready, mocked for now)
   2. Mock data
   3. State
   4. Utilities (toast, view routing, theme)
   5. Feature modules (materials, summary, notes, quiz, flashcards, chat, settings)
   6. Init
   ========================================================= */

/* =========================================================
   1. CONFIG & API LAYER
   ========================================================= */
const API_BASE_URL = "http://localhost:8000";
const USE_MOCK_API = true; // flip to false once the FastAPI backend is live

/** Simulates network latency for demo/mock responses. */
function mockDelay(min = 500, max = 1100) {
  const ms = Math.floor(Math.random() * (max - min)) + min;
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Thin wrapper around fetch() for the future FastAPI backend.
 * Every feature module below calls one of these functions instead of
 * touching fetch() directly, so swapping mock -> real API is a one-line change.
 */
async function apiRequest(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${res.statusText}`);
  return res.json();
}

/* ---- upload ---- */
async function apiUploadMaterial(file, onProgress) {
  if (USE_MOCK_API) {
    for (let p = 0; p <= 100; p += 20) {
      await mockDelay(90, 160);
      onProgress?.(p);
    }
    return {
      id: `mat_${Date.now()}`,
      name: file.name,
      pages: Math.floor(Math.random() * 40) + 8,
      sizeKb: Math.round(file.size / 1024) || Math.floor(Math.random() * 900) + 200,
      uploadedAt: new Date().toISOString(),
      status: "ready",
    };
  }
  // Real implementation (FastAPI, multipart/form-data):
  // const formData = new FormData();
  // formData.append("file", file);
  // const res = await fetch(`${API_BASE_URL}/upload`, { method: "POST", body: formData });
  // return res.json();
}

/* ---- summary ---- */
async function apiGenerateSummary(materialId) {
  if (USE_MOCK_API) {
    await mockDelay(900, 1500);
    return getMockSummary(materialId);
  }
  // return apiRequest(`/summary/${materialId}`, { method: "POST" });
}

/* ---- notes ---- */
async function apiGenerateNotes(materialId) {
  if (USE_MOCK_API) {
    await mockDelay(900, 1500);
    return getMockNotes(materialId);
  }
  // return apiRequest(`/notes/${materialId}`, { method: "POST" });
}

/* ---- quiz ---- */
async function apiGenerateQuiz(materialId) {
  if (USE_MOCK_API) {
    await mockDelay(800, 1300);
    return getMockQuiz(materialId);
  }
  // return apiRequest(`/quiz/${materialId}`, { method: "POST" });
}

/* ---- flashcards ---- */
async function apiGenerateFlashcards(materialId) {
  if (USE_MOCK_API) {
    await mockDelay(800, 1300);
    return getMockFlashcards(materialId);
  }
  // return apiRequest(`/flashcards/${materialId}`, { method: "POST" });
}

/* ---- chat ---- */
async function apiSendChatMessage(message, history) {
  if (USE_MOCK_API) {
    await mockDelay(700, 1400);
    return { reply: getMockChatReply(message) };
  }
  // return apiRequest("/chat", { method: "POST", body: JSON.stringify({ message, history }) });
}

/* =========================================================
   2. MOCK DATA
   ========================================================= */
const state = {
  theme: "light",
  compactSidebar: false,
  currentView: "dashboard",
  materials: [
    { id: "mat_1", name: "Thermodynamics — Chapter 4.pdf", pages: 32, sizeKb: 1840, uploadedAt: daysAgo(1), status: "ready" },
    { id: "mat_2", name: "Data Structures — Trees & Graphs.docx", pages: 18, sizeKb: 640, uploadedAt: daysAgo(2), status: "ready" },
    { id: "mat_3", name: "Microeconomics Notes — Unit 3.pdf", pages: 24, sizeKb: 980, uploadedAt: daysAgo(4), status: "ready" },
    { id: "mat_4", name: "Organic Chemistry — Reactions.pdf", pages: 41, sizeKb: 2210, uploadedAt: daysAgo(6), status: "ready" },
  ],
  quiz: { questions: [], index: 0, answers: [], materialName: "" },
  flashcards: { cards: [], index: 0, materialName: "" },
  chatHistory: [],
};

function daysAgo(n) {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toISOString();
}

function formatRelativeTime(iso) {
  const diffMs = Date.now() - new Date(iso).getTime();
  const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (days <= 0) return "Today";
  if (days === 1) return "Yesterday";
  return `${days} days ago`;
}

function getMaterialById(id) {
  return state.materials.find((m) => m.id === id);
}

function getMockSummary(materialId) {
  const material = getMaterialById(materialId);
  const topic = topicFromName(material?.name);
  return {
    title: `Summary — ${material?.name || "Untitled material"}`,
    readTime: `${Math.max(2, Math.round((material?.pages || 20) / 10))} min read`,
    paragraphs: [
      `This ${topic.subject} material walks through the core ideas of ${topic.focus}, starting from first principles before building up to the more applied problems typically seen in exams.`,
      `The key thread running through the chapter is how ${topic.focus} connects to the broader syllabus — each section builds directly on the previous one, so it's worth working through in order rather than skipping ahead.`,
      `A handful of worked examples anchor the theory to numbers you can actually check by hand, which is the fastest way to catch a shaky concept before it shows up on a test.`,
    ],
    keyPoints: topic.keyPoints,
  };
}

function getMockNotes(materialId) {
  const material = getMaterialById(materialId);
  const topic = topicFromName(material?.name);
  return {
    title: `Notes — ${material?.name || "Untitled material"}`,
    sections: [
      { heading: "Core definitions", items: topic.definitions },
      { heading: "Key formulas & relationships", items: topic.formulas },
      { heading: "Common exam traps", items: topic.traps },
    ],
  };
}

function getMockQuiz(materialId) {
  const material = getMaterialById(materialId);
  const topic = topicFromName(material?.name);
  return { materialName: material?.name || "Untitled material", questions: topic.quiz };
}

function getMockFlashcards(materialId) {
  const material = getMaterialById(materialId);
  const topic = topicFromName(material?.name);
  return { materialName: material?.name || "Untitled material", cards: topic.flashcards };
}

function getMockChatReply(message) {
  const lower = message.toLowerCase();
  if (lower.includes("summar")) {
    return "Head to the Summary tab and pick a material — I'll condense it into a short, readable brief with the key points pulled out.";
  }
  if (lower.includes("quiz") || lower.includes("test")) {
    return "I can put together a quick MCQ quiz from any of your uploaded materials. Open the Quiz tab, choose a file, and I'll start you off with five questions.";
  }
  if (lower.includes("flashcard")) {
    return "Flashcards work well for definitions and formulas. Try the Flashcards tab — I'll generate a deck you can flip through and shuffle.";
  }
  if (lower.includes("hello") || lower.includes("hi ")) {
    return "Hey! I'm PadhAi — I can summarise your materials, build notes, quiz you, or just answer questions about what you've uploaded. What are we studying today?";
  }
  return "Good question. Once this is connected to your materials, I'll answer directly from what you've uploaded — for now, try asking me to summarise, quiz, or explain a topic and I'll point you to the right tool.";
}

/** Generates topic-flavoured mock content based on the material's file name. */
function topicFromName(name = "") {
  const lower = name.toLowerCase();
  if (lower.includes("thermo")) {
    return {
      subject: "physics",
      focus: "the laws of thermodynamics",
      keyPoints: [
        "The First Law is energy conservation applied to heat and work — ΔU = Q − W.",
        "Entropy (the Second Law) explains why heat flows from hot to cold, never the reverse, without external work.",
        "Reversible vs irreversible processes determine how much useful work a system can extract.",
      ],
      definitions: ["Internal energy (U): total kinetic + potential energy of a system's particles.", "Entropy (S): a measure of disorder or unavailable energy in a system.", "Adiabatic process: no heat exchange with the surroundings."],
      formulas: ["ΔU = Q − W (First Law of Thermodynamics)", "η = 1 − (T_cold / T_hot) — Carnot efficiency", "ΔS ≥ 0 for an isolated system (Second Law)"],
      traps: ["Mixing up sign conventions for work done on vs by the system.", "Forgetting that Carnot efficiency needs temperatures in Kelvin.", "Assuming all real processes are reversible — most aren't."],
      quiz: [
        { q: "Which law states that entropy of an isolated system never decreases?", options: ["Zeroth Law", "First Law", "Second Law", "Third Law"], answer: 2 },
        { q: "In ΔU = Q − W, what does W represent?", options: ["Heat added to the system", "Work done by the system", "Total internal energy", "Weight of the system"], answer: 1 },
        { q: "Carnot efficiency depends only on:", options: ["Pressure of the gas", "Volume of the container", "Temperatures of the two reservoirs", "Type of gas used"], answer: 2 },
        { q: "An adiabatic process is one with:", options: ["No change in volume", "No heat exchange", "No work done", "Constant temperature"], answer: 1 },
        { q: "As a system approaches absolute zero, its entropy approaches:", options: ["Infinity", "Zero", "A negative value", "The Carnot limit"], answer: 1 },
      ],
      flashcards: [
        { front: "First Law of Thermodynamics", back: "Energy cannot be created or destroyed: ΔU = Q − W." },
        { front: "Entropy", back: "A measure of disorder; increases in any isolated, irreversible process." },
        { front: "Carnot efficiency formula", back: "η = 1 − (T_cold / T_hot), using absolute temperature." },
        { front: "Adiabatic process", back: "A process with zero heat transfer to or from the system." },
        { front: "Isothermal process", back: "A process that occurs at constant temperature." },
        { front: "Second Law of Thermodynamics", back: "Entropy of an isolated system never decreases over time." },
      ],
    };
  }
  if (lower.includes("data structure") || lower.includes("tree") || lower.includes("graph")) {
    return {
      subject: "computer science",
      focus: "trees and graph traversal",
      keyPoints: [
        "Binary search trees keep left < root < right, giving O(log n) lookup when balanced.",
        "DFS uses a stack (or recursion); BFS uses a queue — the choice changes which paths you find first.",
        "A graph with V vertices needs at most V−1 edges to form a spanning tree.",
      ],
      definitions: ["Binary Search Tree (BST): a tree where each node's left subtree holds smaller values, right holds larger.", "Adjacency list: a graph representation storing each vertex's neighbours in a list.", "Topological sort: a linear ordering of a DAG's vertices respecting edge direction."],
      formulas: ["Height of a balanced BST: O(log n)", "DFS/BFS time complexity: O(V + E)", "Number of edges in a tree with V vertices: V − 1"],
      traps: ["Forgetting a BST can degrade to O(n) if it becomes unbalanced (like a linked list).", "Mixing up when to use a stack (DFS) vs a queue (BFS).", "Not checking for cycles before running topological sort."],
      quiz: [
        { q: "What data structure does BFS traversal rely on?", options: ["Stack", "Queue", "Heap", "Hash map"], answer: 1 },
        { q: "In a balanced BST, search time complexity is:", options: ["O(1)", "O(n)", "O(log n)", "O(n²)"], answer: 2 },
        { q: "A tree with V vertices has how many edges?", options: ["V", "V + 1", "V − 1", "2V"], answer: 2 },
        { q: "Which traversal is typically implemented with recursion or an explicit stack?", options: ["BFS", "DFS", "Dijkstra's", "Topological only"], answer: 1 },
        { q: "Topological sort is only valid on:", options: ["Any graph", "Directed acyclic graphs", "Undirected graphs", "Binary trees only"], answer: 1 },
      ],
      flashcards: [
        { front: "Binary Search Tree (BST)", back: "Left subtree < node < right subtree, enabling fast ordered search." },
        { front: "DFS", back: "Depth-First Search — explores as far as possible before backtracking, uses a stack." },
        { front: "BFS", back: "Breadth-First Search — explores neighbours level by level, uses a queue." },
        { front: "Adjacency list", back: "Graph representation storing each vertex's neighbours in a list — space efficient for sparse graphs." },
        { front: "Topological sort", back: "Orders DAG vertices so every edge points from earlier to later in the ordering." },
        { front: "Balanced tree height", back: "O(log n) — keeps search, insert, and delete efficient." },
      ],
    };
  }
  if (lower.includes("econ")) {
    return {
      subject: "economics",
      focus: "market structures and pricing",
      keyPoints: [
        "In perfect competition, firms are price takers and earn zero economic profit long-run.",
        "A monopolist maximises profit where marginal revenue equals marginal cost, then prices off the demand curve.",
        "Elasticity determines how much a price change shifts quantity demanded.",
      ],
      definitions: ["Marginal cost (MC): the cost of producing one additional unit.", "Price elasticity of demand: % change in quantity demanded ÷ % change in price.", "Consumer surplus: the gap between what buyers are willing to pay and what they actually pay."],
      formulas: ["Profit-maximising rule: MR = MC", "Price elasticity: Ed = %ΔQd / %ΔP", "Total revenue: TR = P × Q"],
      traps: ["Confusing a shift in demand with a movement along the demand curve.", "Assuming MR = P outside of perfect competition (it doesn't hold for a monopoly).", "Forgetting elasticity is usually negative for demand — compare magnitudes, not sign."],
      quiz: [
        { q: "A profit-maximising firm produces where:", options: ["Price = Average cost", "Marginal revenue = Marginal cost", "Total revenue is maximised", "Fixed cost = Variable cost"], answer: 1 },
        { q: "In perfect competition, long-run economic profit is:", options: ["Always positive", "Always negative", "Zero", "Undefined"], answer: 2 },
        { q: "If demand is elastic, a price increase will:", options: ["Increase total revenue", "Decrease total revenue", "Not affect revenue", "Double total revenue"], answer: 1 },
        { q: "Consumer surplus is the area:", options: ["Below supply, above price", "Above demand, below price", "Below demand, above price", "Above supply, below price"], answer: 2 },
        { q: "A monopolist's price is set:", options: ["Equal to marginal cost", "Off the demand curve at the profit-maximising quantity", "At the market equilibrium price", "Equal to average variable cost"], answer: 1 },
      ],
      flashcards: [
        { front: "Marginal Revenue = Marginal Cost", back: "The profit-maximising output rule for any firm." },
        { front: "Price elasticity of demand", back: "Ed = %ΔQd / %ΔP — measures responsiveness of demand to price." },
        { front: "Perfect competition (long run)", back: "Firms are price takers; economic profit is driven to zero by entry/exit." },
        { front: "Consumer surplus", back: "The value consumers gain from paying less than their maximum willingness to pay." },
        { front: "Monopoly pricing", back: "Set where MR = MC, then priced off the demand curve — above marginal cost." },
        { front: "Total revenue", back: "TR = Price × Quantity sold." },
      ],
    };
  }
  // default / organic chemistry / generic
  return {
    subject: "chemistry",
    focus: "core reaction mechanisms",
    keyPoints: [
      "Nucleophilic substitution (SN1/SN2) depends heavily on the substrate's structure and the solvent used.",
      "Reaction mechanisms are best learned by tracking electron movement with curved arrows, not by memorising outcomes.",
      "Reaction rate and stereochemistry both hinge on whether a mechanism goes through a carbocation intermediate.",
    ],
    definitions: ["Nucleophile: an electron-rich species that donates a pair of electrons to form a bond.", "SN1 reaction: substitution proceeding via a carbocation intermediate, first-order kinetics.", "SN2 reaction: single-step substitution with backside attack, second-order kinetics."],
    formulas: ["Rate (SN1) = k[substrate]", "Rate (SN2) = k[substrate][nucleophile]", "Markovnikov's rule: H adds to the carbon with more existing H atoms"],
    traps: ["Assuming all substitution reactions follow the same mechanism.", "Forgetting solvent polarity favours SN1 (polar protic) vs SN2 (polar aprotic).", "Mixing up Markovnikov and anti-Markovnikov addition."],
    quiz: [
      { q: "SN2 reactions proceed via:", options: ["A carbocation intermediate", "A single concerted step with backside attack", "Free radical formation", "Two separate transition states"], answer: 1 },
      { q: "SN1 reaction rate depends on:", options: ["Substrate concentration only", "Nucleophile concentration only", "Both substrate and nucleophile", "Neither — it's constant"], answer: 0 },
      { q: "Polar protic solvents tend to favour:", options: ["SN2 reactions", "SN1 reactions", "No substitution", "Elimination only"], answer: 1 },
      { q: "A nucleophile is best described as:", options: ["Electron-poor and seeking electrons", "Electron-rich, donates electron pairs", "Always negatively charged", "Always a halogen"], answer: 1 },
      { q: "Markovnikov's rule predicts that H adds to:", options: ["The more substituted carbon", "The carbon with more existing hydrogens", "Either carbon randomly", "The carbon nearest a halogen"], answer: 1 },
    ],
    flashcards: [
      { front: "SN1 reaction", back: "Substitution via a carbocation intermediate; rate depends only on substrate concentration." },
      { front: "SN2 reaction", back: "Single-step substitution with backside attack; rate depends on both substrate and nucleophile." },
      { front: "Nucleophile", back: "An electron-rich species that donates an electron pair to form a new bond." },
      { front: "Markovnikov's rule", back: "In addition reactions, H bonds to the carbon that already has more hydrogens." },
      { front: "Polar protic solvent", back: "Favours SN1 reactions by stabilising the carbocation intermediate." },
      { front: "Leaving group", back: "The substituent that departs with the bonding electron pair during substitution." },
    ],
  };
}

/* =========================================================
   4. UTILITIES
   ========================================================= */

/* ---- Toasts ---- */
function showToast(type, title, message) {
  const stack = document.getElementById("toastStack");
  const icons = { success: "✓", error: "⚠", info: "ℹ" };
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span class="toast-icon">${icons[type] || icons.info}</span>
    <div class="toast-body"><strong>${title}</strong><p>${message}</p></div>
  `;
  stack.appendChild(toast);
  setTimeout(() => {
    toast.classList.add("is-leaving");
    setTimeout(() => toast.remove(), 250);
  }, 3800);
}

/* ---- View routing ---- */
const viewMeta = {
  dashboard: { title: "Dashboard", subtitle: "Your learning, distilled by AI." },
  materials: { title: "Materials", subtitle: "Upload and manage your study documents." },
  summary: { title: "Summary", subtitle: "Turn any chapter into a clear, quick brief." },
  notes: { title: "Notes", subtitle: "Structured, exam-ready notes on demand." },
  quiz: { title: "Quiz", subtitle: "Test yourself with AI-generated MCQs." },
  flashcards: { title: "Flashcards", subtitle: "Spaced-repetition ready study cards." },
  chat: { title: "AI Chat", subtitle: "Ask PadhAi anything about your materials." },
  settings: { title: "Settings", subtitle: "Manage your profile and preferences." },
};

function goToView(view) {
  state.currentView = view;
  document.querySelectorAll(".view").forEach((el) => el.classList.remove("is-active"));
  document.getElementById(`view-${view}`)?.classList.add("is-active");
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.classList.toggle("is-active", btn.dataset.view === view);
  });
  const meta = viewMeta[view];
  if (meta) {
    document.getElementById("viewTitle").textContent = meta.title;
    document.getElementById("viewSubtitle").textContent = meta.subtitle;
  }
  document.body.classList.remove("sidebar-open");
  document.getElementById("content").scrollTo({ top: 0, behavior: "smooth" });
}

/* ---- Theme ---- */
function applyTheme(theme) {
  state.theme = theme;
  document.body.setAttribute("data-theme", theme);
  document.getElementById("settingsThemeSwitch")?.classList.toggle("is-on", theme === "dark");
  document.getElementById("settingsThemeSwitch")?.setAttribute("aria-checked", theme === "dark");
  localStorage.setItem("padhai-theme", theme);
}

function toggleTheme() {
  applyTheme(state.theme === "light" ? "dark" : "light");
}

/* ---- Select population ---- */
function populateMaterialSelects() {
  const selects = [
    document.getElementById("summaryMaterialSelect"),
    document.getElementById("notesMaterialSelect"),
    document.getElementById("quizMaterialSelect"),
    document.getElementById("flashMaterialSelect"),
  ];
  const options = state.materials
    .map((m) => `<option value="${m.id}">${m.name}</option>`)
    .join("");
  selects.forEach((sel) => {
    if (!sel) return;
    sel.innerHTML = state.materials.length
      ? options
      : `<option value="">No materials uploaded yet</option>`;
  });
}

/* =========================================================
   5. FEATURE MODULES
   ========================================================= */

/* ---- Dashboard ---- */
function renderStats() {
  const grid = document.getElementById("statsGrid");
  const stats = [
    { icon: "▥", label: "Materials uploaded", value: state.materials.length, trend: "+2 this week" },
    { icon: "≣", label: "Summaries generated", value: 18, trend: "+5 this week" },
    { icon: "◈", label: "Quizzes taken", value: 11, trend: "82% avg score" },
    { icon: "▭", label: "Flashcards reviewed", value: 146, trend: "+34 this week" },
  ];
  grid.innerHTML = stats
    .map(
      (s) => `
    <div class="stat-card">
      <div class="stat-top">
        <span class="stat-icon">${s.icon}</span>
        <span class="stat-trend up">${s.trend}</span>
      </div>
      <div class="stat-value">${s.value}</div>
      <div class="stat-label">${s.label}</div>
    </div>`
    )
    .join("");
}

function renderRecentMaterials() {
  const list = document.getElementById("recentList");
  if (!state.materials.length) {
    list.innerHTML = `<div class="empty-state"><div class="empty-icon">▥</div><h4>Nothing here yet</h4><p>Upload a material to see it appear in your recent list.</p></div>`;
    return;
  }
  list.innerHTML = state.materials
    .slice(0, 4)
    .map(
      (m) => `
    <div class="recent-item">
      <span class="recent-icon">${fileExt(m.name)}</span>
      <div class="recent-meta">
        <strong>${m.name}</strong>
        <small>${formatRelativeTime(m.uploadedAt)} · ${m.pages} pages</small>
      </div>
      <span class="recent-status ready">Ready</span>
    </div>`
    )
    .join("");
}

function fileExt(name) {
  const ext = name.split(".").pop().toUpperCase();
  return ext.length <= 4 ? ext : "DOC";
}

/* ---- Materials / Upload ---- */
function renderMaterials() {
  const grid = document.getElementById("materialsGrid");
  const empty = document.getElementById("materialsEmpty");
  const count = document.getElementById("materialsCount");
  count.textContent = `${state.materials.length} file${state.materials.length === 1 ? "" : "s"}`;

  if (!state.materials.length) {
    grid.innerHTML = "";
    empty.hidden = false;
    return;
  }
  empty.hidden = true;
  grid.innerHTML = state.materials
    .map(
      (m) => `
    <div class="material-card">
      <div class="material-top">
        <span class="material-icon">${fileExt(m.name)}</span>
        <span class="recent-status ready">Ready</span>
      </div>
      <h4>${m.name}</h4>
      <p>${m.pages} pages · ${(m.sizeKb / 1024).toFixed(1)} MB · ${formatRelativeTime(m.uploadedAt)}</p>
      <div class="material-actions">
        <button class="pill-btn" data-action="summary" data-id="${m.id}">Summarise</button>
        <button class="pill-btn" data-action="quiz" data-id="${m.id}">Quiz me</button>
        <button class="pill-btn" data-action="flashcards" data-id="${m.id}">Flashcards</button>
      </div>
    </div>`
    )
    .join("");

  grid.querySelectorAll(".pill-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const { action, id } = btn.dataset;
      goToView(action);
      const selectId = { summary: "summaryMaterialSelect", quiz: "quizMaterialSelect", flashcards: "flashMaterialSelect" }[action];
      const sel = document.getElementById(selectId);
      if (sel) sel.value = id;
    });
  });
}

function initUpload() {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const browseBtn = document.getElementById("browseBtn");
  const progressWrap = document.getElementById("uploadProgress");
  const progressFill = document.getElementById("uploadProgressFill");
  const progressLabel = document.getElementById("uploadProgressLabel");

  browseBtn.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", (e) => handleFiles(e.target.files));

  ["dragenter", "dragover"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.add("is-dragover");
    })
  );
  ["dragleave", "drop"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.remove("is-dragover");
    })
  );
  dropzone.addEventListener("drop", (e) => handleFiles(e.dataTransfer.files));

  async function handleFiles(fileList) {
    const files = Array.from(fileList || []);
    if (!files.length) return;

    for (const file of files) {
      progressWrap.hidden = false;
      progressLabel.textContent = `Uploading ${file.name}…`;
      progressFill.style.width = "0%";
      try {
        const material = await apiUploadMaterial(file, (pct) => {
          progressFill.style.width = `${pct}%`;
        });
        state.materials.unshift(material);
        renderMaterials();
        renderRecentMaterials();
        renderStats();
        populateMaterialSelects();
        showToast("success", "Upload complete", `${file.name} is ready to use.`);
      } catch (err) {
        showToast("error", "Upload failed", "Something went wrong — please try again.");
      }
    }
    progressWrap.hidden = true;
    fileInput.value = "";
  }
}

/* ---- Summary ---- */
function initSummary() {
  const btn = document.getElementById("summaryGenerateBtn");
  const output = document.getElementById("summaryOutput");
  const select = document.getElementById("summaryMaterialSelect");

  btn.addEventListener("click", async () => {
    if (!select.value) {
      showToast("error", "Pick a material", "Upload or select a file before generating a summary.");
      return;
    }
    btn.disabled = true;
    btn.textContent = "Generating…";
    output.innerHTML = renderSkeleton(4);
    try {
      const data = await apiGenerateSummary(select.value);
      output.innerHTML = `
        <div class="output-card">
          <h4>${data.title}</h4>
          <span class="chip">${data.readTime}</span>
          <div style="margin-top:1rem;">
            ${data.paragraphs.map((p) => `<p>${p}</p>`).join("")}
          </div>
          <div class="note-block">
            <h5>Key points</h5>
            <ul>${data.keyPoints.map((k) => `<li>${k}</li>`).join("")}</ul>
          </div>
          <div class="output-foot">
            <button class="btn btn-ghost" id="copySummaryBtn">Copy text</button>
            <button class="btn btn-ghost" id="regenSummaryBtn">Regenerate</button>
          </div>
        </div>`;
      document.getElementById("regenSummaryBtn").addEventListener("click", () => btn.click());
      document.getElementById("copySummaryBtn").addEventListener("click", () =>
        copyToClipboard(data.paragraphs.join("\n\n"), "Summary")
      );
      showToast("success", "Summary ready", "Your AI summary has been generated.");
    } catch (err) {
      output.innerHTML = renderErrorState("We couldn't generate this summary. Please try again.");
      showToast("error", "Generation failed", "Please try again in a moment.");
    } finally {
      btn.disabled = false;
      btn.textContent = "Generate summary";
    }
  });
}

/* ---- Notes ---- */
function initNotes() {
  const btn = document.getElementById("notesGenerateBtn");
  const output = document.getElementById("notesOutput");
  const select = document.getElementById("notesMaterialSelect");

  btn.addEventListener("click", async () => {
    if (!select.value) {
      showToast("error", "Pick a material", "Upload or select a file before generating notes.");
      return;
    }
    btn.disabled = true;
    btn.textContent = "Generating…";
    output.innerHTML = renderSkeleton(5);
    try {
      const data = await apiGenerateNotes(select.value);
      output.innerHTML = `
        <div class="output-card">
          <h4>${data.title}</h4>
          ${data.sections
            .map(
              (s) => `
            <div class="note-block">
              <h5>${s.heading}</h5>
              <ul>${s.items.map((i) => `<li>${i}</li>`).join("")}</ul>
            </div>`
            )
            .join("")}
          <div class="output-foot">
            <button class="btn btn-ghost" id="copyNotesBtn">Copy text</button>
            <button class="btn btn-ghost" id="regenNotesBtn">Regenerate</button>
          </div>
        </div>`;
      document.getElementById("regenNotesBtn").addEventListener("click", () => btn.click());
      document.getElementById("copyNotesBtn").addEventListener("click", () =>
        copyToClipboard(data.sections.map((s) => `${s.heading}\n${s.items.join("\n")}`).join("\n\n"), "Notes")
      );
      showToast("success", "Notes ready", "Your structured notes have been generated.");
    } catch (err) {
      output.innerHTML = renderErrorState("We couldn't generate these notes. Please try again.");
      showToast("error", "Generation failed", "Please try again in a moment.");
    } finally {
      btn.disabled = false;
      btn.textContent = "Generate notes";
    }
  });
}

/* ---- Quiz ---- */
function initQuiz() {
  const setup = document.getElementById("quizSetup");
  const select = document.getElementById("quizMaterialSelect");
  const generateBtn = document.getElementById("quizGenerateBtn");
  const quizBox = document.getElementById("quizBox");
  const resultBox = document.getElementById("quizResult");
  const questionEl = document.getElementById("quizQuestion");
  const optionsEl = document.getElementById("quizOptions");
  const progressLabel = document.getElementById("quizProgressLabel");
  const progressFill = document.getElementById("quizProgressFill");
  const prevBtn = document.getElementById("quizPrevBtn");
  const nextBtn = document.getElementById("quizNextBtn");
  const retakeBtn = document.getElementById("quizRetakeBtn");

  generateBtn.addEventListener("click", async () => {
    if (!select.value) {
      showToast("error", "Pick a material", "Choose a file to generate a quiz from.");
      return;
    }
    generateBtn.disabled = true;
    generateBtn.textContent = "Preparing quiz…";
    try {
      const data = await apiGenerateQuiz(select.value);
      state.quiz = { questions: data.questions, index: 0, answers: new Array(data.questions.length).fill(null), materialName: data.materialName };
      setup.style.display = "none";
      resultBox.hidden = true;
      quizBox.hidden = false;
      renderQuizQuestion();
      showToast("success", "Quiz ready", `${data.questions.length} questions generated.`);
    } catch (err) {
      showToast("error", "Couldn't build quiz", "Please try again.");
    } finally {
      generateBtn.disabled = false;
      generateBtn.textContent = "Start quiz";
    }
  });

  function renderQuizQuestion() {
    const { questions, index, answers } = state.quiz;
    const q = questions[index];
    progressLabel.textContent = `Question ${index + 1} of ${questions.length}`;
    progressFill.style.width = `${((index + 1) / questions.length) * 100}%`;
    questionEl.textContent = q.q;
    const letters = ["A", "B", "C", "D"];
    optionsEl.innerHTML = q.options
      .map(
        (opt, i) => `
      <button class="quiz-option ${answers[index] === i ? "is-selected" : ""}" data-i="${i}">
        <span class="opt-letter">${letters[i]}</span><span>${opt}</span>
      </button>`
      )
      .join("");
    optionsEl.querySelectorAll(".quiz-option").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.quiz.answers[index] = Number(btn.dataset.i);
        renderQuizQuestion();
      });
    });
    prevBtn.disabled = index === 0;
    nextBtn.textContent = index === questions.length - 1 ? "See results" : "Next question";
  }

  prevBtn.addEventListener("click", () => {
    if (state.quiz.index > 0) {
      state.quiz.index -= 1;
      renderQuizQuestion();
    }
  });

  nextBtn.addEventListener("click", () => {
    const { questions, index, answers } = state.quiz;
    if (answers[index] === null || answers[index] === undefined) {
      showToast("error", "Select an answer", "Choose an option before continuing.");
      return;
    }
    if (index < questions.length - 1) {
      state.quiz.index += 1;
      renderQuizQuestion();
    } else {
      finishQuiz();
    }
  });

  function finishQuiz() {
    const { questions, answers } = state.quiz;
    const correct = answers.filter((a, i) => a === questions[i].answer).length;
    const pct = Math.round((correct / questions.length) * 100);
    quizBox.hidden = true;
    resultBox.hidden = false;
    document.getElementById("scorePercent").textContent = `${pct}%`;
    document.getElementById("scoreFraction").textContent = `${correct} / ${questions.length}`;
    const circle = document.getElementById("scoreRingCircle");
    const circumference = 377;
    circle.style.strokeDashoffset = String(circumference - (circumference * pct) / 100);
    const msg =
      pct >= 80 ? "Excellent grasp of the material — keep this up." : pct >= 50 ? "Solid effort. Review the questions you missed and try again." : "Worth another pass through the material before your next attempt.";
    document.getElementById("scoreMessage").textContent = msg;
    showToast(pct >= 50 ? "success" : "info", "Quiz complete", `You scored ${correct} out of ${questions.length}.`);
  }

  retakeBtn.addEventListener("click", () => {
    setup.style.display = "flex";
    resultBox.hidden = true;
    quizBox.hidden = true;
  });
}

/* ---- Flashcards ---- */
function initFlashcards() {
  const select = document.getElementById("flashMaterialSelect");
  const generateBtn = document.getElementById("flashGenerateBtn");
  const deckWrap = document.getElementById("flashDeck");
  const card = document.getElementById("flashcard");
  const frontText = document.getElementById("flashFrontText");
  const backText = document.getElementById("flashBackText");
  const counter = document.getElementById("flashCounter");
  const prevBtn = document.getElementById("flashPrevBtn");
  const nextBtn = document.getElementById("flashNextBtn");
  const shuffleBtn = document.getElementById("flashShuffleBtn");

  generateBtn.addEventListener("click", async () => {
    if (!select.value) {
      showToast("error", "Pick a material", "Choose a file to generate flashcards from.");
      return;
    }
    generateBtn.disabled = true;
    generateBtn.textContent = "Generating…";
    try {
      const data = await apiGenerateFlashcards(select.value);
      state.flashcards = { cards: data.cards, index: 0, materialName: data.materialName };
      deckWrap.hidden = false;
      renderCard();
      showToast("success", "Deck ready", `${data.cards.length} flashcards generated.`);
    } catch (err) {
      showToast("error", "Couldn't build deck", "Please try again.");
    } finally {
      generateBtn.disabled = false;
      generateBtn.textContent = "Generate deck";
    }
  });

  function renderCard() {
    const { cards, index } = state.flashcards;
    card.classList.remove("is-flipped");
    frontText.textContent = cards[index].front;
    backText.textContent = cards[index].back;
    counter.textContent = `Card ${index + 1} of ${cards.length}`;
  }

  card.addEventListener("click", () => card.classList.toggle("is-flipped"));

  prevBtn.addEventListener("click", () => {
    const { cards, index } = state.flashcards;
    state.flashcards.index = index === 0 ? cards.length - 1 : index - 1;
    renderCard();
  });
  nextBtn.addEventListener("click", () => {
    const { cards, index } = state.flashcards;
    state.flashcards.index = index === cards.length - 1 ? 0 : index + 1;
    renderCard();
  });
  shuffleBtn.addEventListener("click", () => {
    const { cards } = state.flashcards;
    for (let i = cards.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [cards[i], cards[j]] = [cards[j], cards[i]];
    }
    state.flashcards.index = 0;
    renderCard();
    showToast("info", "Deck shuffled", "Card order has been randomised.");
  });
}

/* ---- Chat ---- */
function initChat() {
  const form = document.getElementById("chatForm");
  const input = document.getElementById("chatInput");
  const window_ = document.getElementById("chatWindow");
  const typing = document.getElementById("chatTyping");

  if (!state.chatHistory.length) {
    state.chatHistory.push({
      role: "ai",
      text: "Hi Ananya! I'm PadhAi. Ask me to summarise a chapter, quiz you, explain a concept, or anything else about your materials.",
    });
  }
  renderChat();

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    state.chatHistory.push({ role: "user", text });
    input.value = "";
    renderChat();
    typing.hidden = false;
    window_.scrollTop = window_.scrollHeight;

    try {
      const { reply } = await apiSendChatMessage(text, state.chatHistory);
      state.chatHistory.push({ role: "ai", text: reply });
    } catch (err) {
      state.chatHistory.push({ role: "ai", text: "Sorry, something went wrong on my end. Please try asking again." });
    } finally {
      typing.hidden = true;
      renderChat();
    }
  });

  function renderChat() {
    window_.innerHTML = state.chatHistory
      .map((m) => `<div class="msg ${m.role === "user" ? "msg-user" : "msg-ai"}">${escapeHtml(m.text)}</div>`)
      .join("");
    window_.scrollTop = window_.scrollHeight;
  }
}

/* ---- Settings ---- */
function initSettings() {
  const themeSwitch = document.getElementById("settingsThemeSwitch");
  const compactSwitch = document.getElementById("compactSwitch");
  const digestSwitch = document.getElementById("digestSwitch");
  const saveBtn = document.getElementById("saveProfileBtn");

  themeSwitch.addEventListener("click", toggleTheme);

  compactSwitch.addEventListener("click", () => {
    state.compactSidebar = !state.compactSidebar;
    compactSwitch.classList.toggle("is-on", state.compactSidebar);
    compactSwitch.setAttribute("aria-checked", state.compactSidebar);
    document.querySelector(".sidebar").classList.toggle("is-compact", state.compactSidebar);
  });

  digestSwitch.addEventListener("click", () => {
    const isOn = digestSwitch.classList.toggle("is-on");
    digestSwitch.setAttribute("aria-checked", isOn);
  });

  saveBtn.addEventListener("click", () => {
    showToast("success", "Profile saved", "Your changes have been saved.");
  });
}

/* ---- Shared render helpers ---- */
function renderSkeleton(lines) {
  const widths = [95, 88, 92, 70, 80, 60];
  return `<div class="skeleton">${Array.from({ length: lines })
    .map((_, i) => `<div class="skeleton-line" style="width:${widths[i % widths.length]}%"></div>`)
    .join("")}</div>`;
}

function renderErrorState(message) {
  return `<div class="empty-state"><div class="empty-icon">⚠</div><h4>Something went wrong</h4><p>${message}</p></div>`;
}

function copyToClipboard(text, label) {
  navigator.clipboard
    ?.writeText(text)
    .then(() => showToast("success", "Copied", `${label} copied to clipboard.`))
    .catch(() => showToast("error", "Copy failed", "Your browser blocked clipboard access."));
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

/* =========================================================
   6. INIT
   ========================================================= */
function initNav() {
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.addEventListener("click", () => goToView(btn.dataset.view));
  });
  document.querySelectorAll("[data-goto]").forEach((btn) => {
    btn.addEventListener("click", () => goToView(btn.dataset.goto));
  });
}

function initSidebarToggle() {
  const menuBtn = document.getElementById("menuBtn");
  const closeBtn = document.getElementById("sidebarClose");
  const scrim = document.getElementById("sidebarScrim");
  menuBtn.addEventListener("click", () => document.body.classList.add("sidebar-open"));
  closeBtn.addEventListener("click", () => document.body.classList.remove("sidebar-open"));
  scrim.addEventListener("click", () => document.body.classList.remove("sidebar-open"));
}

function initThemeToggle() {
  document.getElementById("themeToggle").addEventListener("click", toggleTheme);
  const saved = localStorage.getItem("padhai-theme");
  const prefersDark = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
  applyTheme(saved || (prefersDark ? "dark" : "light"));
}

document.addEventListener("DOMContentLoaded", () => {
  initThemeToggle();
  initNav();
  initSidebarToggle();
  populateMaterialSelects();
  renderStats();
  renderRecentMaterials();
  renderMaterials();
  initUpload();
  initSummary();
  initNotes();
  initQuiz();
  initFlashcards();
  initChat();
  initSettings();
  goToView("dashboard");

  setTimeout(() => {
    showToast("info", "Welcome back", "You have 4 materials ready to study.");
  }, 600);
});
