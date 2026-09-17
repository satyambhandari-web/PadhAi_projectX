/* ============================================================
   PADHAI — FINAL CORRECTED FRONTEND
   ============================================================

   BACKEND:
   http://localhost:8000

   MATERIALS:
   GET  /api/materials
   POST /api/upload

   WORKFLOW:
   POST /api/workflow

   CHAT:
   POST /api/chat

   TTS:
   POST /api/tts
   ============================================================ */


/* ============================================================
   1. CONFIG
   ============================================================ */

const API_BASE_URL = "http://localhost:8000";


/* ============================================================
   2. GLOBAL STATE
   ============================================================ */

const state = {
  theme: "light",
  compactSidebar: false,
  currentView: "dashboard",

  materials: [],

  selectedMaterial: null,

  chatHistory: [],

  activeChatAgent: "chat",
};


/* ============================================================
   3. API HELPER
   ============================================================ */

async function apiRequest(path, options = {}) {

  const config = {
    ...options,

    headers: {
      ...(options.body instanceof FormData
        ? {}
        : {
          "Content-Type": "application/json",
        }),

      ...(options.headers || {}),
    },
  };

  let response;

  try {

    response = await fetch(
      `${API_BASE_URL}${path}`,
      config
    );

  } catch (error) {

    throw new Error(
      "Cannot connect to FastAPI backend. " +
      "Make sure your backend is running on port 8000."
    );
  }


  let data = null;

  try {

    data = await response.json();

  } catch (_) {

    data = null;
  }


  if (!response.ok) {

    const message =
      data?.detail ||
      data?.message ||
      `Request failed (${response.status})`;

    throw new Error(message);
  }


  return data;
}


/* ============================================================
   4. MATERIALS
   ============================================================ */

async function apiListMaterials() {

  /*
     IMPORTANT:

     Your backend returns:

     [
       {
         "id": "Python_Complete_Notes.pdf",
         "name": "Python_Complete_Notes.pdf",
         "filename": "Python_Complete_Notes.pdf",
         ...
       }
     ]
  */

  return apiRequest("/api/materials");
}


/* ============================================================
   5. UPLOAD
   ============================================================ */

async function apiUploadMaterial(file, onProgress) {

  const formData = new FormData();

  formData.append("file", file);


  return new Promise((resolve, reject) => {

    const xhr = new XMLHttpRequest();


    xhr.open(
      "POST",
      `${API_BASE_URL}/api/upload`
    );


    xhr.upload.addEventListener(
      "progress",
      (event) => {

        if (event.lengthComputable) {

          const percentage =
            Math.round(
              (event.loaded / event.total) * 100
            );

          onProgress?.(percentage);
        }
      }
    );


    xhr.addEventListener(
      "load",
      () => {

        let data = null;

        try {

          data =
            JSON.parse(
              xhr.responseText
            );

        } catch (_) {

          data = null;
        }


        if (
          xhr.status >= 200 &&
          xhr.status < 300
        ) {

          onProgress?.(100);

          resolve(data);

        } else {

          reject(
            new Error(
              data?.detail ||
              `Upload failed (${xhr.status})`
            )
          );
        }
      }
    );


    xhr.addEventListener(
      "error",
      () => {

        reject(
          new Error(
            "Network error during upload."
          )
        );
      }
    );


    xhr.addEventListener(
      "abort",
      () => {

        reject(
          new Error(
            "Upload was cancelled."
          )
        );
      }
    );


    xhr.send(formData);
  });
}


/* ============================================================
   6. WORKFLOW API
   ============================================================ */

async function apiRunWorkflow(
  task,
  materialId,
  customQuery = ""
) {

  if (!materialId) {
    throw new Error(
      "Please select a material first."
    );
  }

  const material =
    state.materials.find(
      item =>
        String(item.id) ===
        String(materialId)
    );

  const filename =
    material?.filename ||
    material?.name ||
    materialId;

  let query;

  if (customQuery && customQuery.trim()) {
    query =
      `${customQuery.trim()}\n\n` +
      `Selected study material: ${filename}`;
  } else {
    const taskText = {
      summary: "Generate a clear and concise summary",
      notes: "Generate detailed exam-ready notes",
      quiz: "Generate a quiz with questions and answers",
      flashcards: "Generate useful study flashcards",
      content: "Generate educational learning content",
    };

    query =
      `${taskText[task] || "Generate educational content"} ` +
      `from the selected study material: ${filename}`;
  }

  return apiRequest(
    "/api/workflow",
    {
      method: "POST",

      body: JSON.stringify({
        task: task,
        query: query,
        material_id: filename,
      }),
    }
  );
}


/* ============================================================
   7. SUMMARY
   ============================================================ */

async function apiGenerateSummary(
  materialId,
  query = ""
) {

  return apiRunWorkflow(
    "summary",
    materialId,
    query
  );
}


/* ============================================================
   8. NOTES
   ============================================================ */

async function apiGenerateNotes(
  materialId,
  query = ""
) {

  return apiRunWorkflow(
    "notes",
    materialId,
    query
  );
}


/* ============================================================
   9. QUIZ
   ============================================================ */

async function apiGenerateQuiz(
  materialId,
  query = ""
) {

  return apiRunWorkflow(
    "quiz",
    materialId,
    query
  );
}


/* ============================================================
   10. FLASHCARDS
   ============================================================ */

async function apiGenerateFlashcards(
  materialId,
  query = ""
) {

  return apiRunWorkflow(
    "flashcards",
    materialId,
    query
  );
}


/* ============================================================
   11. CONTENT
   ============================================================ */

async function apiGenerateContent(
  materialId,
  query = ""
) {

  return apiRunWorkflow(
    "content",
    materialId,
    query
  );
}


/* ============================================================
   12. CHAT
   ============================================================ */

async function apiSendChatMessage(
  message,
  history,
  materialId
) {

  const material =
    state.materials.find(
      item =>
        String(item.id) ===
        String(materialId)
    );

  const filename =
    material?.filename ||
    material?.name ||
    materialId ||
    null;

  return apiRequest(
    "/api/chat",
    {
      method: "POST",

      body: JSON.stringify({
        message: message,
        filename: filename,
        material_id: filename,
      }),
    }
  );
}

/* ============================================================
   TTS & VECTOR PROCESS API & HELPERS
   ============================================================ */

async function apiGenerateTTS(text, language = "en") {
  return apiRequest("/api/tts", {
    method: "POST",
    body: JSON.stringify({
      text: text,
      language: language,
    }),
  });
}

async function apiProcessPDF(filename) {
  return apiRequest(`/api/process-pdf?filename=${encodeURIComponent(filename)}`, {
    method: "POST",
  });
}

async function apiGetStats() {
  try {
    return await apiRequest("/api/stats");
  } catch (_) {
    return null;
  }
}

function renderTTSBar(text, containerId) {
  return "";
}

async function handleTTSPlay(textVarName, containerId) {
  const text = window[textVarName];
  const langSelect = document.getElementById(`tts-lang-${containerId}`);
  const lang = langSelect ? langSelect.value : "en";
  const playerBox = document.getElementById(`tts-player-box-${containerId}`);
  const playBtn = document.querySelector(`#tts-bar-${containerId} .tts-btn`);

  if (!text) return;

  if (playBtn) {
    playBtn.disabled = true;
    playBtn.innerHTML = `<span>⏳ Generating audio...</span>`;
  }

  try {
    const data = await apiGenerateTTS(text, lang);
    if (data && data.audio_url) {
      const audioUrl = `${API_BASE_URL}${data.audio_url}`;
      if (playerBox) {
        playerBox.innerHTML = `<audio class="tts-player" controls autoplay src="${audioUrl}"></audio>`;
      }
      showToast("success", "Audio Ready", "Playing generated speech audio.");
    }
  } catch (error) {
    showToast("error", "TTS Failed", error.message);
  } finally {
    if (playBtn) {
      playBtn.disabled = false;
      playBtn.innerHTML = `<span>▶ Listen / Play Speech</span>`;
    }
  }
}

window.handleTTSPlay = handleTTSPlay;


/* ============================================================
   13. ESCAPE HTML
   ============================================================ */

function escapeHtml(value = "") {

  const div =
    document.createElement("div");

  div.textContent =
    String(value);

  return div.innerHTML;
}


/* ============================================================
   14. MARKDOWN
   ============================================================ */

function renderMarkdown(markdown = "") {

  const escaped =
    escapeHtml(markdown);


  const lines =
    escaped.split(/\r?\n/);


  let html = "";

  let listOpen = false;


  function closeList() {

    if (listOpen) {

      html += "</ul>";

      listOpen = false;
    }
  }


  function inlineFormat(text) {

    return text

      .replace(
        /\*\*(.+?)\*\*/g,
        "<strong>$1</strong>"
      )

      .replace(
        /\*(.+?)\*/g,
        "<em>$1</em>"
      )

      .replace(
        /`(.+?)`/g,
        "<code>$1</code>"
      );
  }


  for (const rawLine of lines) {

    const line =
      rawLine.trim();


    if (!line) {

      closeList();

      continue;
    }


    const heading =
      line.match(
        /^(#{1,6})\s+(.*)$/
      );


    const bullet =
      line.match(
        /^[-*]\s+(.*)$/
      );


    const numbered =
      line.match(
        /^\d+[.)]\s+(.*)$/
      );


    if (heading) {

      closeList();


      const level =
        Math.min(
          heading[1].length,
          6
        );


      html +=
        `<h${level}>` +
        inlineFormat(
          heading[2]
        ) +
        `</h${level}>`;

      continue;
    }


    if (bullet || numbered) {

      if (!listOpen) {

        html += "<ul>";

        listOpen = true;
      }


      const text =
        bullet
          ? bullet[1]
          : numbered[1];


      html +=
        `<li>${inlineFormat(text)}</li>`;

      continue;
    }


    if (line === "---") {

      closeList();

      html += "<hr>";

      continue;
    }


    closeList();


    html +=
      `<p>${inlineFormat(line)}</p>`;
  }


  closeList();


  return html;
}


/* ============================================================
   15. TOAST
   ============================================================ */

function showToast(
  type,
  title,
  message
) {

  const stack =
    document.getElementById(
      "toastStack"
    );


  if (!stack) return;


  const icons = {

    success: "✓",

    error: "⚠",

    info: "ℹ",
  };


  const toast =
    document.createElement("div");


  toast.className =
    `toast ${type}`;


  toast.innerHTML = `

        <span class="toast-icon">
            ${icons[type] || "ℹ"}
        </span>

        <div class="toast-body">

            <strong>
                ${escapeHtml(title)}
            </strong>

            <p>
                ${escapeHtml(message)}
            </p>

        </div>
    `;


  stack.appendChild(toast);


  setTimeout(
    () => {

      toast.classList.add(
        "is-leaving"
      );


      setTimeout(
        () => toast.remove(),
        250
      );

    },
    3800
  );
}


/* ============================================================
   16. VIEW META
   ============================================================ */

const viewMeta = {

  dashboard: {
    title: "Dashboard",
    subtitle:
      "Your learning, distilled by AI.",
  },

  materials: {
    title: "Materials",
    subtitle:
      "Upload and manage your study documents.",
  },

  summary: {
    title: "Summary",
    subtitle:
      "Turn any chapter into a clear, quick brief.",
  },

  notes: {
    title: "Notes",
    subtitle:
      "Structured, exam-ready notes on demand.",
  },

  quiz: {
    title: "Quiz",
    subtitle:
      "Test yourself with AI-generated questions.",
  },

  flashcards: {
    title: "Flashcards",
    subtitle:
      "Study using AI-generated flashcards.",
  },

  chat: {
    title: "AI Chat",
    subtitle:
      "Ask PadhAi about your materials.",
  },

  settings: {
    title: "Settings",
    subtitle:
      "Manage your profile and preferences.",
  },
};


/* ============================================================
   17. VIEW NAVIGATION
   ============================================================ */

function goToView(view) {

  state.currentView =
    view;


  document
    .querySelectorAll(".view")
    .forEach(
      element =>
        element.classList.remove(
          "is-active"
        )
    );


  document
    .getElementById(
      `view-${view}`
    )
    ?.classList.add(
      "is-active"
    );


  document
    .querySelectorAll(".nav-item")
    .forEach(
      button => {

        button.classList.toggle(
          "is-active",
          button.dataset.view === view
        );
      }
    );


  const meta =
    viewMeta[view];


  if (meta) {

    const title =
      document.getElementById(
        "viewTitle"
      );


    const subtitle =
      document.getElementById(
        "viewSubtitle"
      );


    if (title)
      title.textContent =
        meta.title;


    if (subtitle)
      subtitle.textContent =
        meta.subtitle;
  }


  document.body.classList.remove(
    "sidebar-open"
  );
}


/* ============================================================
   18. THEME
   ============================================================ */

function applyTheme(theme) {

  state.theme =
    theme;


  document.body.setAttribute(
    "data-theme",
    theme
  );


  const switchElement =
    document.getElementById(
      "settingsThemeSwitch"
    );


  switchElement?.classList.toggle(
    "is-on",
    theme === "dark"
  );


  switchElement?.setAttribute(
    "aria-checked",
    String(theme === "dark")
  );


  localStorage.setItem(
    "padhai-theme",
    theme
  );
}


function toggleTheme() {

  applyTheme(
    state.theme === "light"
      ? "dark"
      : "light"
  );
}


/* ============================================================
   19. MATERIAL SELECTS
   ============================================================ */

function populateMaterialSelects() {

  const selectIds = [

    "summaryMaterialSelect",

    "notesMaterialSelect",

    "quizMaterialSelect",

    "flashMaterialSelect",

    "chatMaterialSelect",
  ];


  selectIds.forEach(id => {

    const select =
      document.getElementById(id);


    if (!select) return;


    if (!state.materials.length) {

      select.innerHTML =
        `<option value="">
                    No materials uploaded yet
                </option>`;

      return;
    }


    select.innerHTML = `

            <option value="">
                Select a material
            </option>

            ${state.materials
        .map(material => {

          const id =
            material.id ||
            material.filename ||
            material.name;

          const name =
            material.name ||
            material.filename ||
            material.id;


          return `
                        <option value="${escapeHtml(id)}">
                            ${escapeHtml(name)}
                        </option>
                    `;
        })
        .join("")}
        `;


    select.addEventListener(
      "change",
      () => {

        if (select.value) {

          state.selectedMaterial =
            select.value;
        }
      }
    );
  });
}


/* ============================================================
   20. REFRESH MATERIALS
   ============================================================ */

async function refreshMaterials() {

  try {

    const materials =
      await apiListMaterials();


    state.materials =
      Array.isArray(materials)
        ? materials
        : [];


    populateMaterialSelects();

    renderStats();

    renderRecentMaterials();

    renderMaterials();


  } catch (error) {

    console.error(
      "[MATERIAL ERROR]",
      error
    );


    state.materials = [];


    populateMaterialSelects();

    renderStats();

    renderRecentMaterials();

    renderMaterials();


    showToast(
      "error",
      "Could not load materials",
      error.message
    );
  }
}


/* ============================================================
   21. STATS
   ============================================================ */

async function renderStats() {

  const grid =
    document.getElementById(
      "statsGrid"
    );

  if (!grid) return;

  let totalAudio = 0;
  let backendStatus = "Connected";

  try {
    const statsData = await apiGetStats();
    if (statsData && statsData.stats) {
      totalAudio = statsData.stats.total_audio || 0;
    }
  } catch (_) {
    backendStatus = "Offline";
  }

  const stats = [
    {
      icon: "▥",
      label: "Materials uploaded",
      value: state.materials.length,
      trend: "From your library",
    },
    {
      icon: "☰",
      label: "Study materials ready",
      value: state.materials.length,
      trend: "Available now",
    },
    {
      icon: "◈",
      label: "AI tools available",
      value: "5",
      trend: "Summary · Notes · Quiz",
    },
    {
      icon: "▭",
      label: "Learning mode",
      value: "AI",
      trend: "Powered by your workflow",
    },
  ];

  grid.innerHTML =
    stats
      .map(item => `

                <div class="stat-card">

                    <div class="stat-top">

                        <span class="stat-icon">
                            ${item.icon}
                        </span>

                        <span class="stat-trend">
                            ${escapeHtml(item.trend)}
                        </span>

                    </div>

                    <div class="stat-value">
                        ${escapeHtml(String(item.value))}
                    </div>

                    <div class="stat-label">
                        ${escapeHtml(item.label)}
                    </div>

                </div>

            `)
      .join("");
}


/* ============================================================
   22. RECENT MATERIALS
   ============================================================ */

function renderRecentMaterials() {

  const list =
    document.getElementById(
      "recentList"
    );


  if (!list) return;


  if (!state.materials.length) {

    list.innerHTML = `

            <div class="empty-state">

                <div class="empty-icon">
                    ▥
                </div>

                <h4>
                    No materials yet
                </h4>

                <p>
                    Upload a PDF to get started.
                </p>

            </div>
        `;

    return;
  }


  list.innerHTML =
    state.materials
      .slice(0, 5)
      .map(material => `

                <div class="recent-item">

                    <span class="recent-icon">
                        PDF
                    </span>

                    <div class="recent-meta">

                        <strong>
                            ${escapeHtml(
        material.name ||
        material.filename ||
        material.id
      )}
                        </strong>

                        <small>
                            ${material.pages || 0}
                            pages
                            ·
                            ${formatRelativeTime(
        material.uploadedAt
      )}
                        </small>

                    </div>

                    <span class="recent-status ready">
                        Ready
                    </span>

                </div>

            `)
      .join("");
}


/* ============================================================
   23. MATERIALS PAGE
   ============================================================ */

function renderMaterials() {

  const grid =
    document.getElementById(
      "materialsGrid"
    );


  const empty =
    document.getElementById(
      "materialsEmpty"
    );


  const count =
    document.getElementById(
      "materialsCount"
    );


  if (!grid) return;


  if (count) {

    count.textContent =
      `${state.materials.length} file${state.materials.length === 1
        ? ""
        : "s"
      }`;
  }


  if (!state.materials.length) {

    grid.innerHTML = "";

    if (empty)
      empty.hidden = false;

    return;
  }


  if (empty)
    empty.hidden = true;


  grid.innerHTML =
    state.materials
      .map(material => {

        const id =
          material.id ||
          material.filename ||
          material.name;

        const name =
          material.name ||
          material.filename ||
          material.id;


        const sizeMb =
          material.sizeKb
            ? (
              material.sizeKb / 1024
            ).toFixed(1)
            : (
              (material.size || 0) /
              (1024 * 1024)
            ).toFixed(1);


        return `

                    <div class="material-card">

                        <div class="material-top">

                            <span class="material-icon">
                                PDF
                            </span>

                            <span class="recent-status ready">
                                Ready
                            </span>

                        </div>

                        <h4>
                            ${escapeHtml(name)}
                        </h4>

                        <p>
                            ${material.pages || 0}
                            pages
                            ·
                            ${sizeMb}
                            MB
                            ·
                            ${formatRelativeTime(
          material.uploadedAt
        )}
                        </p>

                        <div class="material-actions">

                            <button
                                class="pill-btn"
                                data-action="summary"
                                data-id="${escapeHtml(id)}"
                            >
                                Summarise
                            </button>

                            <button
                                class="pill-btn"
                                data-action="quiz"
                                data-id="${escapeHtml(id)}"
                            >
                                Quiz me
                            </button>

                            <button
                                class="pill-btn"
                                data-action="flashcards"
                                data-id="${escapeHtml(id)}"
                            >
                                Flashcards
                            </button>

                            <button
                                class="pill-btn pill-btn-vector"
                                data-action="process-pdf"
                                data-id="${escapeHtml(id)}"
                            >
                                ⚡ Index Vector DB
                            </button>

                        </div>

                    </div>
                `;
      })
      .join("");


  grid
    .querySelectorAll(".pill-btn")
    .forEach(button => {
      button.addEventListener(
        "click",
        async () => {
          const action = button.dataset.action;
          const id = button.dataset.id;

          if (action === "process-pdf") {
            button.disabled = true;
            button.textContent = "Indexing...";
            try {
              const data = await apiProcessPDF(id);
              showToast("success", "Vector DB Indexed", `Created ${data.chunks || 0} embeddings for ${id}`);
            } catch (err) {
              showToast("error", "Indexing Failed", err.message);
            } finally {
              button.disabled = false;
              button.textContent = "⚡ Index Vector DB";
            }
            return;
          }

          state.selectedMaterial = id;

          const selectMap = {
            summary: "summaryMaterialSelect",
            quiz: "quizMaterialSelect",
            flashcards: "flashMaterialSelect",
          };

          const select = document.getElementById(selectMap[action]);
          if (select) select.value = id;

          if (selectMap[action]) {
            goToView(action);
          }
        }
      );
    });
}


/* ============================================================
   24. UPLOAD
   ============================================================ */

function initUpload() {

  const dropzone =
    document.getElementById(
      "dropzone"
    );


  const fileInput =
    document.getElementById(
      "fileInput"
    );


  const browseBtn =
    document.getElementById(
      "browseBtn"
    );


  const progressWrap =
    document.getElementById(
      "uploadProgress"
    );


  const progressFill =
    document.getElementById(
      "uploadProgressFill"
    );


  const progressLabel =
    document.getElementById(
      "uploadProgressLabel"
    );


  if (!dropzone || !fileInput)
    return;


  browseBtn?.addEventListener(
    "click",
    () => fileInput.click()
  );


  fileInput.addEventListener(
    "change",
    event => {

      handleFiles(
        event.target.files
      );
    }
  );


  [
    "dragenter",
    "dragover",
  ].forEach(eventName => {

    dropzone.addEventListener(
      eventName,
      event => {

        event.preventDefault();

        dropzone.classList.add(
          "is-dragover"
        );
      }
    );
  });


  [
    "dragleave",
    "drop",
  ].forEach(eventName => {

    dropzone.addEventListener(
      eventName,
      event => {

        event.preventDefault();

        dropzone.classList.remove(
          "is-dragover"
        );
      }
    );
  });


  dropzone.addEventListener(
    "drop",
    event => {

      handleFiles(
        event.dataTransfer.files
      );
    }
  );


  async function handleFiles(fileList) {

    const files =
      Array.from(
        fileList || []
      );


    if (!files.length)
      return;


    for (const file of files) {

      if (
        !file.name
          .toLowerCase()
          .endsWith(".pdf")
      ) {

        showToast(
          "error",
          "Invalid file",
          `${file.name} is not a PDF.`
        );

        continue;
      }


      if (progressWrap)
        progressWrap.hidden = false;


      if (progressLabel)
        progressLabel.textContent =
          `Uploading ${file.name}...`;


      if (progressFill)
        progressFill.style.width =
          "0%";


      try {

        const result =
          await apiUploadMaterial(
            file,
            percentage => {

              if (progressFill)
                progressFill.style.width =
                  `${percentage}%`;
            }
          );


        showToast(
          "success",
          "Upload complete",
          `${file.name} is ready.`
        );


        await refreshMaterials();


        /*
           IMPORTANT:

           Backend upload may return:

           {
               filename: "...",
               name: "...",
               id: "..."
           }

           We use whichever exists.
        */

        const newId =
          result?.id ||
          result?.filename ||
          result?.name ||
          file.name;


        selectMaterialEverywhere(
          newId
        );


      } catch (error) {

        console.error(
          "[UPLOAD ERROR]",
          error
        );


        showToast(
          "error",
          "Upload failed",
          error.message
        );
      }
    }


    if (progressWrap)
      progressWrap.hidden = true;


    fileInput.value = "";
  }
}


/* ============================================================
   25. SELECT MATERIAL EVERYWHERE
   ============================================================ */

function selectMaterialEverywhere(materialId) {

  if (!materialId)
    return;


  state.selectedMaterial =
    materialId;


  [
    "summaryMaterialSelect",
    "notesMaterialSelect",
    "quizMaterialSelect",
    "flashMaterialSelect",
  ].forEach(id => {

    const select =
      document.getElementById(id);


    if (select)
      select.value =
        materialId;
  });
}


/* ============================================================
   26. SUMMARY
   ============================================================ */

function initSummary() {

  const button =
    document.getElementById(
      "summaryGenerateBtn"
    );


  const select =
    document.getElementById(
      "summaryMaterialSelect"
    );


  const output =
    document.getElementById(
      "summaryOutput"
    );


  if (!button || !select || !output)
    return;


  button.addEventListener(
    "click",
    async () => {

      const materialId =
        select.value;


      if (!materialId) {

        showToast(
          "error",
          "Select a material",
          "Choose a PDF first."
        );

        return;
      }


      state.selectedMaterial =
        materialId;


      button.disabled = true;

      button.textContent =
        "Generating...";


      output.innerHTML =
        renderSkeleton(5);


      try {

        const data =
          await apiGenerateSummary(
            materialId
          );


        const content =
          data.output ||
          data.content ||
          data.response ||
          "No summary returned.";


        output.innerHTML = `

                    <div class="output-card">

                        <h4>
                            ${escapeHtml(
          data.title ||
          "Summary"
        )}
                        </h4>

                        <div style="margin-top:1rem;">
                            ${renderMarkdown(content)}
                        </div>

                        <div class="output-foot">

                            <button
                                class="btn btn-ghost"
                                id="copySummaryBtn"
                            >
                                Copy text
                            </button>

                            <button
                                class="btn btn-ghost"
                                id="regenSummaryBtn"
                            >
                                Regenerate
                            </button>

                        </div>

                    </div>
                `;


        document
          .getElementById(
            "copySummaryBtn"
          )
          ?.addEventListener(
            "click",
            () =>
              copyToClipboard(
                content,
                "Summary"
              )
          );


        document
          .getElementById(
            "regenSummaryBtn"
          )
          ?.addEventListener(
            "click",
            () => button.click()
          );


        showToast(
          "success",
          "Summary ready",
          "Your workflow generated the summary."
        );


      } catch (error) {

        output.innerHTML =
          renderErrorState(
            error.message
          );


        showToast(
          "error",
          "Summary failed",
          error.message
        );


      } finally {

        button.disabled = false;

        button.textContent =
          "Generate summary";
      }
    }
  );
}


/* ============================================================
   27. NOTES
   ============================================================ */

function initNotes() {

  const button =
    document.getElementById(
      "notesGenerateBtn"
    );


  const select =
    document.getElementById(
      "notesMaterialSelect"
    );


  const output =
    document.getElementById(
      "notesOutput"
    );


  if (!button || !select || !output)
    return;


  button.addEventListener(
    "click",
    async () => {

      const materialId =
        select.value;


      if (!materialId) {

        showToast(
          "error",
          "Select a material",
          "Choose a PDF first."
        );

        return;
      }


      state.selectedMaterial =
        materialId;


      button.disabled = true;

      button.textContent =
        "Generating...";


      output.innerHTML =
        renderSkeleton(5);


      try {

        const data =
          await apiGenerateNotes(
            materialId
          );


        const content =
          data.output ||
          data.content ||
          data.response ||
          "No notes returned.";


        output.innerHTML = `

                    <div class="output-card">

                        <h4>
                            ${escapeHtml(
          data.title ||
          "Notes"
        )}
                        </h4>

                        <div
                            class="note-block"
                        >
                            ${renderMarkdown(content)}
                        </div>

                        <div class="output-foot">

                            <button
                                class="btn btn-ghost"
                                id="copyNotesBtn"
                            >
                                Copy text
                            </button>

                            <button
                                class="btn btn-ghost"
                                id="regenNotesBtn"
                            >
                                Regenerate
                            </button>

                        </div>

                    </div>
                `;


        document
          .getElementById(
            "copyNotesBtn"
          )
          ?.addEventListener(
            "click",
            () =>
              copyToClipboard(
                content,
                "Notes"
              )
          );


        document
          .getElementById(
            "regenNotesBtn"
          )
          ?.addEventListener(
            "click",
            () => button.click()
          );


        showToast(
          "success",
          "Notes ready",
          "Your workflow generated the notes."
        );


      } catch (error) {

        output.innerHTML =
          renderErrorState(
            error.message
          );


        showToast(
          "error",
          "Notes failed",
          error.message
        );


      } finally {

        button.disabled = false;

        button.textContent =
          "Generate notes";
      }
    }
  );
}


/* ============================================================
   28. QUIZ
   ============================================================ */

function initQuiz() {

  const setup =
    document.getElementById(
      "quizSetup"
    );


  const select =
    document.getElementById(
      "quizMaterialSelect"
    );


  const button =
    document.getElementById(
      "quizGenerateBtn"
    );


  const quizBox =
    document.getElementById(
      "quizBox"
    );


  const resultBox =
    document.getElementById(
      "quizResult"
    );


  if (!setup || !select || !button)
    return;

  let questions = [];
  let currentQuestion = 0;
  let selectedAnswers = [];

  const progressLabel = document.getElementById("quizProgressLabel");
  const progressFill = document.getElementById("quizProgressFill");
  const questionElement = document.getElementById("quizQuestion");
  const optionsElement = document.getElementById("quizOptions");
  const previousButton = document.getElementById("quizPrevBtn");
  const nextButton = document.getElementById("quizNextBtn");
  const changeMaterialBtn = document.getElementById("quizChangeMaterialBtn");
  const reviewList = document.getElementById("quizReviewList");

  function escapeHtml(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function parseQuizContent(text) {
    const parsed = [];
    const blocks = String(text || "")
      .split(/(?=^\s*#{1,6}\s+Question\s+\d+\b|^\s*(?:Question\s*)?\d+\s*[:.)-])/im)
      .map(block => block.trim())
      .filter(Boolean);

    blocks.forEach(block => {
      const questionMatch = block.match(/\*\*Question:\*\*\s*(.+?)(?=\n|$)/i)
        || block.match(/^(?:#{1,6}\s*)?(?:Question\s*)?\d+\s*[:.)-]\s*(.+?)(?=\n|$)/i);
      if (!questionMatch) return;

      const options = [];
      const optionPattern = /^\s*\*{0,2}([A-D])\s*[).:-]\s*\*{0,2}\s*(.+?)\s*$/gim;
      let optionMatch;
      while ((optionMatch = optionPattern.exec(block))) {
        options.push({ letter: optionMatch[1].toUpperCase(), text: optionMatch[2].trim() });
      }
      if (options.length < 2) return;

      const answerMatch = block.match(/(?:correct\s*(?:answer|option)|answer)\s*:\s*\*{0,2}\s*([A-D])/i);
      const explanationMatch = block.match(/(?:explanation|reason)\s*:\s*\*{0,2}\s*(.+?)(?=\n\n|\n[A-Z]\)|\nQuestion|$)/is);

      parsed.push({
        question: questionMatch[1].trim(),
        options: options.slice(0, 4),
        answer: answerMatch ? answerMatch[1].toUpperCase() : "",
        explanation: explanationMatch ? explanationMatch[1].trim() : "",
      });
    });

    return parsed;
  }

  function renderQuestion() {
    const question = questions[currentQuestion];
    if (!question || !questionElement || !optionsElement) return;

    if (progressLabel) progressLabel.textContent = `Question ${currentQuestion + 1} of ${questions.length}`;
    if (progressFill) progressFill.style.width = `${((currentQuestion + 1) / questions.length) * 100}%`;
    questionElement.textContent = question.question;

    optionsElement.innerHTML = question.options.map(option => `
      <label class="quiz-option${selectedAnswers[currentQuestion] === option.letter ? " is-selected" : ""}">
        <input type="checkbox" name="quiz-answer" value="${option.letter}" ${selectedAnswers[currentQuestion] === option.letter ? "checked" : ""}>
        <span class="opt-letter">${option.letter}</span>
        <span>${escapeHtml(option.text)}</span>
      </label>
    `).join("");

    optionsElement.querySelectorAll("input").forEach(input => {
      input.addEventListener("change", () => {
        optionsElement.querySelectorAll("input").forEach(other => {
          if (other !== input) other.checked = false;
          other.closest(".quiz-option")?.classList.toggle("is-selected", other.checked);
        });
        selectedAnswers[currentQuestion] = input.checked ? input.value : "";
      });
    });

    if (previousButton) previousButton.disabled = currentQuestion === 0;
    if (nextButton) nextButton.textContent = currentQuestion === questions.length - 1 ? "Finish quiz" : "Next question";
  }

  function showQuizResult() {
    const score = questions.reduce((total, question, index) => total + (selectedAnswers[index] === question.answer ? 1 : 0), 0);
    if (quizBox) quizBox.hidden = true;
    if (resultBox) resultBox.hidden = false;
    const percent = Math.round((score / questions.length) * 100);

    const scoreTitle = document.getElementById("scoreTitle");
    if (scoreTitle) {
      if (percent === 100) scoreTitle.textContent = "Perfect Score! 🌟";
      else if (percent >= 80) scoreTitle.textContent = "Great Job! 🎉";
      else if (percent >= 50) scoreTitle.textContent = "Good Effort! 👍";
      else scoreTitle.textContent = "Keep Practicing! 💪";
    }

    document.getElementById("scorePercent")?.replaceChildren(document.createTextNode(`${percent}%`));
    document.getElementById("scoreFraction")?.replaceChildren(document.createTextNode(`${score} / ${questions.length}`));
    document.getElementById("scoreMessage")?.replaceChildren(document.createTextNode(`You answered ${score} of ${questions.length} questions correctly.`));
    const ring = document.getElementById("scoreRingCircle");
    if (ring) ring.style.strokeDashoffset = String(377 - (377 * percent / 100));

    if (reviewList) {
      reviewList.innerHTML = questions.map((q, idx) => {
        const userAns = selectedAnswers[idx] || "None";
        const isCorrect = userAns === q.answer;
        const badgeHtml = isCorrect
          ? `<span class="quiz-review-badge badge-correct">✓ Correct</span>`
          : `<span class="quiz-review-badge badge-incorrect">✕ Incorrect</span>`;

        const optionsReviewHtml = q.options.map(opt => {
          let optClass = "";
          let labelExtra = "";
          if (opt.letter === userAns && isCorrect) {
            optClass = "opt-user-correct";
            labelExtra = " (Your answer - Correct)";
          } else if (opt.letter === userAns && !isCorrect) {
            optClass = "opt-user-wrong";
            labelExtra = " (Your answer)";
          } else if (opt.letter === q.answer && !isCorrect) {
            optClass = "opt-target-correct";
            labelExtra = " (Correct answer)";
          }

          return `<div class="quiz-review-opt ${optClass}">
            <strong class="opt-letter">${opt.letter}</strong>
            <span>${escapeHtml(opt.text)}${labelExtra}</span>
          </div>`;
        }).join("");

        const expHtml = q.explanation
          ? `<div class="quiz-review-exp"><strong>Explanation:</strong> ${escapeHtml(q.explanation)}</div>`
          : "";

        return `
          <div class="quiz-review-item">
            <div class="quiz-review-header">
              <span class="quiz-review-q">Q${idx + 1}. ${escapeHtml(q.question)}</span>
              ${badgeHtml}
            </div>
            <div class="quiz-review-opts">${optionsReviewHtml}</div>
            ${expHtml}
          </div>
        `;
      }).join("");
    }
  }

  previousButton?.addEventListener("click", () => {
    if (currentQuestion > 0) {
      currentQuestion -= 1;
      renderQuestion();
    }
  });

  nextButton?.addEventListener("click", () => {
    if (!selectedAnswers[currentQuestion]) {
      showToast("info", "Select an answer", "Please choose an option with the checkbox before moving forward.");
      return;
    }
    if (currentQuestion === questions.length - 1) showQuizResult();
    else {
      currentQuestion += 1;
      renderQuestion();
    }
  });

  document.getElementById("quizRetakeBtn")?.addEventListener("click", () => {
    currentQuestion = 0;
    selectedAnswers = [];
    if (resultBox) resultBox.hidden = true;
    if (quizBox) quizBox.hidden = false;
    renderQuestion();
  });

  changeMaterialBtn?.addEventListener("click", () => {
    currentQuestion = 0;
    selectedAnswers = [];
    questions = [];
    if (resultBox) resultBox.hidden = true;
    if (quizBox) quizBox.hidden = true;
    if (setup) setup.style.display = "flex";
  });


  button.addEventListener(
    "click",
    async () => {

      const materialId =
        select.value;


      if (!materialId) {

        showToast(
          "error",
          "Select a material",
          "Choose a PDF first."
        );

        return;
      }


      state.selectedMaterial =
        materialId;


      button.disabled = true;

      button.textContent =
        "Generating...";


      try {

        const data =
          await apiGenerateQuiz(
            materialId
          );


        const content =
          data.output ||
          data.content ||
          data.response ||
          "No quiz returned.";

        questions = parseQuizContent(content);
        if (!questions.length) {
          throw new Error("The generated quiz could not be read. Please try again.");
        }
        currentQuestion = 0;
        selectedAnswers = [];


        setup.style.display =
          "none";


        if (quizBox)
          quizBox.hidden = false;


        if (resultBox)
          resultBox.hidden = true;


        renderQuestion();


        showToast(
          "success",
          "Quiz ready",
          "Your workflow generated the quiz."
        );


      } catch (error) {

        showToast(
          "error",
          "Quiz failed",
          error.message
        );


      } finally {

        button.disabled = false;

        button.textContent =
          "Start quiz";
      }
    }
  );
}


/* ============================================================
   29. FLASHCARDS
   ============================================================ */

function initFlashcards() {
  const select = document.getElementById("flashMaterialSelect");
  const button = document.getElementById("flashGenerateBtn");
  const deck = document.getElementById("flashDeck");
  const staticGrid = document.getElementById("flashcardGrid");
  const deckGrid = document.getElementById("flashDeckGrid");
  const shuffleBtn = document.getElementById("flashShuffleBtn");

  // Enable flip interactivity for static initial cards
  if (staticGrid) {
    attachGridFlipEvents(staticGrid);
  }

  function attachGridFlipEvents(gridContainer) {
    if (!gridContainer) return;
    const cards = gridContainer.querySelectorAll(".flashcard-grid-item");
    cards.forEach(card => {
      card.onclick = function () {
        this.classList.toggle("is-flipped");
      };
    });
  }

  if (shuffleBtn) {
    shuffleBtn.addEventListener("click", () => {
      const activeGrid = (deck && !deck.hidden && deckGrid) ? deckGrid : staticGrid;
      if (!activeGrid) return;
      const cards = Array.from(activeGrid.querySelectorAll(".flashcard-grid-item"));
      cards.forEach(card => {
        card.style.transition = "transform 0.25s ease, opacity 0.25s ease";
        card.style.opacity = "0";
        card.style.transform = "scale(0.85)";
      });
      setTimeout(() => {
        cards.sort(() => Math.random() - 0.5);
        cards.forEach(card => {
          card.classList.remove("is-flipped");
          activeGrid.appendChild(card);
        });
        setTimeout(() => {
          cards.forEach(card => {
            card.style.opacity = "1";
            card.style.transform = "none";
          });
        }, 50);
      }, 250);
    });
  }

  if (!select || !button) return;

  button.addEventListener("click", async () => {
    const materialId = select.value;
    if (!materialId) {
      showToast("error", "Select a material", "Choose a PDF first.");
      return;
    }

    state.selectedMaterial = materialId;
    button.disabled = true;
    button.textContent = "Generating...";

    try {
      const data = await apiGenerateFlashcards(materialId);
      const rawContent = data.output || data.content || data.response || "";

      if (deck && deckGrid) {
        const parsedCards = parseFlashcardsContent(rawContent);

        if (parsedCards.length > 0) {
          deckGrid.innerHTML = parsedCards.map(c => `
            <div class="flashcard-grid-item">
              <div class="flashcard-inner">
                <div class="flashcard-face flashcard-front">
                  <span class="flashcard-tag">${escapeHtml(c.tag || "Generated")}</span>
                  <p>${escapeHtml(c.term)}</p>
                  <span class="flashcard-hint">Tap to flip ↺</span>
                </div>
                <div class="flashcard-face flashcard-back">
                  <span class="flashcard-tag">Answer</span>
                  <p>${escapeHtml(c.answer)}</p>
                  <span class="flashcard-hint">Tap to flip back ↺</span>
                </div>
              </div>
            </div>
          `).join("");

          attachGridFlipEvents(deckGrid);
          deck.hidden = false;
          const countBadge = document.getElementById("flashCardCount");
          if (countBadge) countBadge.textContent = `${parsedCards.length} cards`;
        } else {
          deckGrid.innerHTML = `
            <div class="output-card" style="grid-column: 1 / -1;">
              <h4>${escapeHtml(data.title || "Generated Flashcards")}</h4>
              <div style="margin-top:1rem;">${renderMarkdown(rawContent)}</div>
            </div>
          `;
          deck.hidden = false;
        }
      }

      showToast("success", "Flashcards ready", "Your rounded flashcard deck was generated.");
    } catch (error) {
      showToast("error", "Flashcards failed", error.message);
    } finally {
      button.disabled = false;
      button.textContent = "Generate deck";
    }
  });

  function parseFlashcardsContent(text) {
    if (!text) return [];
    const results = [];
    const lines = text.split("\n");
    let currentTerm = "";
    let currentAns = "";

    for (let line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      const termMatch = trimmed.match(/^(\*\*|\*)?(Q|Term|Card\s*\d+)?[\:\-\s]*([^\:\-]+)[\:\-]\s*(.+)?/i);

      if (trimmed.toLowerCase().includes("q:") || trimmed.toLowerCase().includes("term:")) {
        if (currentTerm && currentAns) {
          results.push({ term: currentTerm, answer: currentAns, tag: "Study Term" });
          currentTerm = "";
          currentAns = "";
        }
        currentTerm = trimmed.replace(/^(\*\*|\*)?(q|term|card \d+)[\:\s]*/i, "").replace(/(\*\*|\*)$/, "").trim();
      } else if (trimmed.toLowerCase().includes("a:") || trimmed.toLowerCase().includes("answer:")) {
        currentAns = trimmed.replace(/^(\*\*|\*)?(a|answer)[\:\s]*/i, "").replace(/(\*\*|\*)$/, "").trim();
      } else if (currentTerm && !currentAns) {
        currentTerm += " " + trimmed;
      } else if (currentAns) {
        currentAns += " " + trimmed;
      }
    }
    if (currentTerm && currentAns) {
      results.push({ term: currentTerm, answer: currentAns, tag: "Study Term" });
    }

    if (results.length === 0) {
      const items = text.split(/\n\s*\n/);
      items.forEach((chunk, i) => {
        const parts = chunk.split(/[\:\n]/);
        if (parts.length >= 2) {
          results.push({
            term: parts[0].replace(/^[\#\*\-\d\.\s]+/, "").trim(),
            answer: parts.slice(1).join(" ").trim(),
            tag: `Card ${i + 1}`
          });
        }
      });
    }
    return results;
  }
}


/* ============================================================
   30. CHAT
   ============================================================ */

const agentMap = {
  chat: {
    name: "General AI Agent",
    icon: "🤖",
    placeholder: "Ask about your materials, request a summary, or quiz yourself…",
    systemPrefix: "",
  },
  summary: {
    name: "Summary Agent",
    icon: "≣",
    placeholder: "Ask Summary Agent to summarize your materials or specific sections…",
    systemPrefix: "[Task: Summary Agent] Please provide a clear, structured summary of: ",
  },
  notes: {
    name: "Notes Agent",
    icon: "✎",
    placeholder: "Ask Notes Agent for exam-ready structured study notes…",
    systemPrefix: "[Task: Notes Agent] Please generate structured study notes with key terms for: ",
  },
  quiz: {
    name: "Quiz Agent",
    icon: "◈",
    placeholder: "Ask Quiz Agent to create questions or test your knowledge…",
    systemPrefix: "[Task: Quiz Agent] Please create a multiple-choice quiz with explanations for: ",
  },
  flashcards: {
    name: "Flashcards Agent",
    icon: "▭",
    placeholder: "Ask Flashcards Agent to create revision cards and key concepts…",
    systemPrefix: "[Task: Flashcards Agent] Please generate key flashcard Q&A pairs for: ",
  },
};

function initChat() {
  const form = document.getElementById("chatForm");
  const input = document.getElementById("chatInput");
  const windowElement = document.getElementById("chatWindow");
  const typing = document.getElementById("chatTyping");
  const chatPanel = document.getElementById("chatPanel");
  const fullscreenBtn = document.getElementById("chatFullscreenBtn");
  const agentSelector = document.getElementById("chatAgentSelector");

  if (!form || !input || !windowElement) return;

  // Agent switcher chip handlers
  if (agentSelector) {
    agentSelector.querySelectorAll(".agent-chip").forEach(chip => {
      chip.addEventListener("click", () => {
        agentSelector.querySelectorAll(".agent-chip").forEach(c => c.classList.remove("is-active"));
        chip.classList.add("is-active");
        const agentKey = chip.dataset.agent || "chat";
        state.activeChatAgent = agentKey;

        const agentInfo = agentMap[agentKey] || agentMap.chat;
        input.placeholder = agentInfo.placeholder;

        const typingName = document.getElementById("typingAgentName");
        if (typingName) {
          typingName.textContent = agentInfo.name;
        }

        showToast("info", `${agentInfo.icon} ${agentInfo.name} Active`, `Switched to ${agentInfo.name}.`);
      });
    });
  }

  // Full-screen mode toggle logic for agent chatbox
  if (fullscreenBtn && chatPanel) {
    fullscreenBtn.addEventListener("click", () => {
      const isFS = chatPanel.classList.toggle("is-fullscreen");
      document.body.classList.toggle("chat-fullscreen-active", isFS);

      const expandIcon = fullscreenBtn.querySelector(".fs-icon-expand");
      const compressIcon = fullscreenBtn.querySelector(".fs-icon-compress");

      if (expandIcon && compressIcon) {
        expandIcon.style.display = isFS ? "none" : "inline";
        compressIcon.style.display = isFS ? "inline" : "none";
      }

      fullscreenBtn.title = isFS ? "Exit full browser screen chat" : "Toggle full browser screen chat";
      showToast("info", isFS ? "Full Browser Screen Enabled" : "Full Screen Exited", isFS ? "Chatbox is occupying the full browser screen." : "Returned to default layout.");

      if (windowElement) {
        setTimeout(() => {
          windowElement.scrollTop = windowElement.scrollHeight;
        }, 100);
      }
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && chatPanel.classList.contains("is-fullscreen")) {
        chatPanel.classList.remove("is-fullscreen");
        document.body.classList.remove("chat-fullscreen-active");
        const expandIcon = fullscreenBtn.querySelector(".fs-icon-expand");
        const compressIcon = fullscreenBtn.querySelector(".fs-icon-compress");
        if (expandIcon && compressIcon) {
          expandIcon.style.display = "inline";
          compressIcon.style.display = "none";
        }
        fullscreenBtn.title = "Toggle full browser screen chat";
      }
    });
  }

  renderChat();

  form.addEventListener("submit", async event => {
    event.preventDefault();
    const text = input.value.trim();
    if (!text) return;

    const currentAgent = state.activeChatAgent || "chat";
    const agentInfo = agentMap[currentAgent] || agentMap.chat;

    state.chatHistory.push({
      role: "user",
      text: text,
      agent: currentAgent,
    });

    input.value = "";
    renderChat();

    const typingName = document.getElementById("typingAgentName");
    if (typingName) {
      typingName.textContent = agentInfo.name;
    }
    if (typing) typing.hidden = false;

    const chatSelect = document.getElementById("chatMaterialSelect");
    const activeMaterialId = (chatSelect && chatSelect.value) ? chatSelect.value : state.selectedMaterial;

    const promptText = agentInfo.systemPrefix ? `${agentInfo.systemPrefix}${text}` : text;

    try {
      const data = await apiSendChatMessage(promptText, state.chatHistory, activeMaterialId);
      state.chatHistory.push({
        role: "ai",
        text: data.reply || data.response || data.output || "No response received.",
        agent: currentAgent,
      });
    } catch (error) {
      state.chatHistory.push({
        role: "ai",
        text: `Error: ${error.message}`,
        agent: currentAgent,
      });
    } finally {
      if (typing) typing.hidden = true;
      renderChat();
    }
  });

  function renderChat() {
    if (!state.chatHistory.length) {
      windowElement.innerHTML = `
        <div class="chat-welcome-box">
          <div class="chat-welcome-icon">🤖</div>
          <h3>Welcome to PadhAi AI Chat</h3>
          <p>Select any AI Agent from the toolbar above and ask about your study materials.</p>
          <div class="chat-starter-grid">
            <button class="starter-pill" data-agent="summary" data-prompt="Summarize my uploaded study material in detail.">
              <span class="starter-pill-icon">≣</span>
              <span>Summarize study material</span>
            </button>
            <button class="starter-pill" data-agent="quiz" data-prompt="Generate a 5-question multiple choice quiz from my study material.">
              <span class="starter-pill-icon">◈</span>
              <span>Create 5-question quiz</span>
            </button>
            <button class="starter-pill" data-agent="notes" data-prompt="Generate exam-ready structured study notes with key terms.">
              <span class="starter-pill-icon">✎</span>
              <span>Generate structured notes</span>
            </button>
            <button class="starter-pill" data-agent="flashcards" data-prompt="Create key flashcards for revision.">
              <span class="starter-pill-icon">▭</span>
              <span>Create revision flashcards</span>
            </button>
          </div>
        </div>
      `;

      windowElement.querySelectorAll(".starter-pill").forEach(pill => {
        pill.addEventListener("click", () => {
          const agentKey = pill.dataset.agent;
          const prompt = pill.dataset.prompt;

          if (agentKey && agentSelector) {
            const targetChip = agentSelector.querySelector(`.agent-chip[data-agent="${agentKey}"]`);
            if (targetChip) targetChip.click();
          }

          if (prompt && input) {
            input.value = prompt;
            form.dispatchEvent(new Event("submit"));
          }
        });
      });
      return;
    }

    windowElement.innerHTML = state.chatHistory
      .map((message) => {
        const isUser = message.role === "user";
        const agentKey = message.agent || "chat";
        const agentInfo = agentMap[agentKey] || agentMap.chat;
        const formattedContent = isUser ? escapeHtml(message.text) : renderMarkdown(message.text);

        if (isUser) {
          return `
            <div class="msg-wrapper msg-user-wrapper">
              <div class="msg msg-user">
                <div>${formattedContent}</div>
              </div>
              <div class="msg-avatar user-avatar" title="You">U</div>
            </div>
          `;
        } else {
          return `
            <div class="msg-wrapper msg-ai-wrapper">
              <div class="msg-avatar ai-avatar" title="${escapeHtml(agentInfo.name)}">${agentInfo.icon}</div>
              <div class="msg msg-ai">
                <div class="msg-agent-tag">
                  <span>${agentInfo.icon}</span>
                  <span>${escapeHtml(agentInfo.name)}</span>
                </div>
                <div>${formattedContent}</div>
              </div>
            </div>
          `;
        }
      })
      .join("");

    windowElement.scrollTop = windowElement.scrollHeight;
  }
}


/* ============================================================
   31. SETTINGS
   ============================================================ */

function initSettings() {

  const themeSwitch =
    document.getElementById(
      "settingsThemeSwitch"
    );


  const compactSwitch =
    document.getElementById(
      "compactSwitch"
    );


  const digestSwitch =
    document.getElementById(
      "digestSwitch"
    );


  const saveButton =
    document.getElementById(
      "saveProfileBtn"
    );


  themeSwitch?.addEventListener(
    "click",
    toggleTheme
  );


  compactSwitch?.addEventListener(
    "click",
    () => {

      state.compactSidebar =
        !state.compactSidebar;


      compactSwitch.classList.toggle(
        "is-on",
        state.compactSidebar
      );


      compactSwitch.setAttribute(
        "aria-checked",
        String(
          state.compactSidebar
        )
      );


      document
        .querySelector(".sidebar")
        ?.classList.toggle(
          "is-compact",
          state.compactSidebar
        );
    }
  );


  digestSwitch?.addEventListener(
    "click",
    () => {

      const isOn =
        digestSwitch.classList.toggle(
          "is-on"
        );


      digestSwitch.setAttribute(
        "aria-checked",
        String(isOn)
      );
    }
  );


  saveButton?.addEventListener(
    "click",
    () => {

      showToast(
        "success",
        "Profile saved",
        "Your changes have been saved."
      );
    }
  );
}


/* ============================================================
   32. NAVIGATION
   ============================================================ */

function initNav() {

  document
    .querySelectorAll(".nav-item")
    .forEach(button => {

      button.addEventListener(
        "click",
        () => {

          goToView(
            button.dataset.view
          );
        }
      );
    });


  document
    .querySelectorAll("[data-goto]")
    .forEach(button => {

      button.addEventListener(
        "click",
        () => {

          goToView(
            button.dataset.goto
          );
        }
      );
    });
}


/* ============================================================
   33. SIDEBAR
   ============================================================ */

function initSidebarToggle() {

  const menuButton =
    document.getElementById(
      "menuBtn"
    );


  const closeButton =
    document.getElementById(
      "sidebarClose"
    );


  const scrim =
    document.getElementById(
      "sidebarScrim"
    );


  menuButton?.addEventListener(
    "click",
    () =>
      document.body.classList.add(
        "sidebar-open"
      )
  );


  closeButton?.addEventListener(
    "click",
    () =>
      document.body.classList.remove(
        "sidebar-open"
      )
  );


  scrim?.addEventListener(
    "click",
    () =>
      document.body.classList.remove(
        "sidebar-open"
      )
  );
}


/* ============================================================
   34. THEME INITIALIZATION
   ============================================================ */

function initThemeToggle() {

  document
    .getElementById(
      "themeToggle"
    )
    ?.addEventListener(
      "click",
      toggleTheme
    );


  const saved =
    localStorage.getItem(
      "padhai-theme"
    );


  const prefersDark =
    window
      .matchMedia?.(
        "(prefers-color-scheme: dark)"
      )
      .matches;


  applyTheme(
    saved ||
    (
      prefersDark
        ? "dark"
        : "light"
    )
  );
}


/* ============================================================
   35. SKELETON
   ============================================================ */

function renderSkeleton(count = 5) {

  const widths = [
    95,
    88,
    92,
    75,
    85,
  ];


  return `

        <div class="skeleton">

            ${Array.from(
    { length: count }
  )
      .map(
        (_, index) => `

                        <div
                            class="skeleton-line"
                            style="width:${widths[
          index %
          widths.length
          ]
          }%"
                        ></div>

                    `
      )
      .join("")}

        </div>
    `;
}


/* ============================================================
   36. ERROR STATE
   ============================================================ */

function renderErrorState(message) {

  return `

        <div class="empty-state">

            <div class="empty-icon">
                ⚠
            </div>

            <h4>
                Something went wrong
            </h4>

            <p>
                ${escapeHtml(message)}
            </p>

        </div>
    `;
}


/* ============================================================
   37. CLIPBOARD
   ============================================================ */

async function copyToClipboard(
  text,
  label
) {

  try {

    await navigator.clipboard.writeText(
      text
    );


    showToast(
      "success",
      "Copied",
      `${label} copied to clipboard.`
    );


  } catch (error) {

    showToast(
      "error",
      "Copy failed",
      "Clipboard access was blocked."
    );
  }
}


/* ============================================================
   38. TIME FORMAT
   ============================================================ */

function formatRelativeTime(value) {

  if (!value)
    return "Recently";


  const date =
    new Date(value);


  if (
    Number.isNaN(
      date.getTime()
    )
  )
    return "Recently";


  const difference =
    Date.now() -
    date.getTime();


  const minutes =
    Math.floor(
      difference /
      (1000 * 60)
    );


  if (minutes < 1)
    return "Just now";


  if (minutes < 60)
    return `${minutes} min ago`;


  const hours =
    Math.floor(
      minutes / 60
    );


  if (hours < 24)
    return `${hours} hr ago`;


  const days =
    Math.floor(
      hours / 24
    );


  if (days === 1)
    return "Yesterday";


  if (days < 7)
    return `${days} days ago`;


  return date.toLocaleDateString();
}


/* ============================================================
   39. INITIALIZATION
   ============================================================ */

document.addEventListener(
  "DOMContentLoaded",
  async () => {

    console.log(
      "PadhAi frontend starting..."
    );


    initThemeToggle();

    initNav();

    initSidebarToggle();

    initUpload();

    initSummary();

    initNotes();

    initQuiz();

    initFlashcards();

    initChat();

    initSettings();


    goToView(
      "dashboard"
    );


    await refreshMaterials();


    /*
       Automatically select first material
       if one exists.
    */

    if (state.materials.length) {

      const first =
        state.materials[0];


      const firstId =
        first.id ||
        first.filename ||
        first.name;


      selectMaterialEverywhere(
        firstId
      );


      showToast(
        "info",
        "Welcome back",
        `${state.materials.length} material${state.materials.length === 1
          ? ""
          : "s"
        } available.`
      );

    } else {

      showToast(
        "info",
        "Get started",
        "Upload a PDF to begin studying."
      );
    }


    console.log(
      "PadhAi frontend ready."
    );
  }
);