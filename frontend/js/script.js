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


  /*
     materialId is actually the PDF filename.

     Example:

     Python_Complete_Notes.pdf

     We explicitly include the material name
     in the workflow query.
  */

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

      summary:
        "Generate a clear and concise summary",

      notes:
        "Generate detailed exam-ready notes",

      quiz:
        "Generate a quiz with questions and answers",

      flashcards:
        "Generate useful study flashcards",

      content:
        "Generate educational learning content",

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
      }),
    }
  );
}


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

function renderStats() {

  const grid =
    document.getElementById(
      "statsGrid"
    );


  if (!grid) return;


  const stats = [

    {
      icon: "▥",
      label: "Materials uploaded",
      value: state.materials.length,
      trend: "From your library",
    },

    {
      icon: "≣",
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
        () => {

          const action =
            button.dataset.action;


          const id =
            button.dataset.id;


          selectMaterialEverywhere(id);


          const selectMap = {

            summary:
              "summaryMaterialSelect",

            quiz:
              "quizMaterialSelect",

            flashcards:
              "flashMaterialSelect",
          };


          const select =
            document.getElementById(
              selectMap[action]
            );


          if (select)
            select.value = id;


          goToView(action);
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


        setup.style.display =
          "none";


        if (quizBox)
          quizBox.hidden = false;


        if (resultBox)
          resultBox.hidden = true;


        if (quizBox) {

          quizBox.innerHTML = `

                        <div class="output-card">

                            <h4>
                                ${escapeHtml(
            data.title ||
            "AI Quiz"
          )}
                            </h4>

                            <div style="margin-top:1rem;">
                                ${renderMarkdown(content)}
                            </div>

                            <div class="output-foot">

                                <button
                                    class="btn btn-ghost"
                                    id="quizCopyBtn"
                                >
                                    Copy quiz
                                </button>

                            </div>

                        </div>
                    `;


          document
            .getElementById(
              "quizCopyBtn"
            )
            ?.addEventListener(
              "click",
              () =>
                copyToClipboard(
                  content,
                  "Quiz"
                )
            );
        }


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

  const select =
    document.getElementById(
      "flashMaterialSelect"
    );


  const button =
    document.getElementById(
      "flashGenerateBtn"
    );


  const deck =
    document.getElementById(
      "flashDeck"
    );


  if (!select || !button)
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


      try {

        const data =
          await apiGenerateFlashcards(
            materialId
          );


        const content =
          data.output ||
          data.content ||
          data.response ||
          "No flashcards returned.";


        if (deck) {

          deck.hidden = false;


          deck.innerHTML = `

                        <div class="output-card">

                            <h4>
                                ${escapeHtml(
            data.title ||
            "Flashcards"
          )}
                            </h4>

                            <div style="margin-top:1rem;">
                                ${renderMarkdown(content)}
                            </div>

                            <div class="output-foot">

                                <button
                                    class="btn btn-ghost"
                                    id="flashCopyBtn"
                                >
                                    Copy flashcards
                                </button>

                            </div>

                        </div>
                    `;


          document
            .getElementById(
              "flashCopyBtn"
            )
            ?.addEventListener(
              "click",
              () =>
                copyToClipboard(
                  content,
                  "Flashcards"
                )
            );
        }


        showToast(
          "success",
          "Flashcards ready",
          "Your workflow generated the flashcards."
        );


      } catch (error) {

        showToast(
          "error",
          "Flashcards failed",
          error.message
        );


      } finally {

        button.disabled = false;

        button.textContent =
          "Generate deck";
      }
    }
  );
}


/* ============================================================
   30. CHAT
   ============================================================ */

function initChat() {

  const form =
    document.getElementById(
      "chatForm"
    );


  const input =
    document.getElementById(
      "chatInput"
    );


  const windowElement =
    document.getElementById(
      "chatWindow"
    );


  const typing =
    document.getElementById(
      "chatTyping"
    );


  if (!form || !input || !windowElement)
    return;


  if (!state.chatHistory.length) {

    state.chatHistory.push({

      role: "ai",

      text:
        "Hi! I'm PadhAi. " +
        "Select a material and ask me something about it.",
    });
  }


  renderChat();


  form.addEventListener(
    "submit",
    async event => {

      event.preventDefault();


      const text =
        input.value.trim();


      if (!text)
        return;


      state.chatHistory.push({

        role: "user",

        text: text,
      });


      input.value = "";


      renderChat();


      if (typing)
        typing.hidden = false;


      try {

        const data =
          await apiSendChatMessage(
            text,
            state.chatHistory,
            state.selectedMaterial
          );


        state.chatHistory.push({

          role: "ai",

          text:
            data.reply ||
            data.response ||
            data.output ||
            "No response received.",
        });


      } catch (error) {

        state.chatHistory.push({

          role: "ai",

          text:
            `Error: ${error.message}`,
        });

      } finally {

        if (typing)
          typing.hidden = true;


        renderChat();
      }
    }
  );


  function renderChat() {

    windowElement.innerHTML =
      state.chatHistory
        .map(message => `

                    <div
                        class="msg ${message.role === "user"
            ? "msg-user"
            : "msg-ai"
          }"
                    >
                        ${escapeHtml(
            message.text
          )}
                    </div>

                `)
        .join("");


    windowElement.scrollTop =
      windowElement.scrollHeight;
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