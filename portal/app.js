/**
 * UPSC Prelims Canonical Microtheme Master Hub — Application Logic
 * Fast, standalone, zero-dependency SPA for microtheme-based study.
 */

// Application State
let DB = null;
let currentSubject = "All";
let currentMicrotheme = null;
let currentTab = "cse"; // "cse", "cross", "all"
let isPracticeMode = false;
let globalSearchQuery = "";
let currentSort = "freq-desc";
let currentYieldFilter = "all";

// ============================================
// Initialization
// ============================================
document.addEventListener("DOMContentLoaded", () => {
    initData();
    setupEventListeners();
});

function initData() {
    if (typeof PORTAL_DATA !== "undefined") {
        DB = PORTAL_DATA;
        onDataReady();
    } else {
        fetch("data/portal_data.json")
            .then(res => res.json())
            .then(data => {
                DB = data;
                onDataReady();
            })
            .catch(err => {
                console.error("Failed to load portal data:", err);
            });
    }
}

function onDataReady() {
    renderSubjectBar();
    renderSidebarList();
    
    // Check URL hash for direct microtheme link (e.g. #mt-001 or #Political Theory)
    const hash = window.location.hash.replace("#", "").trim();
    if (hash) {
        const targetTheme = DB.microthemes.find(m => m.id === hash || encodeURIComponent(m.theme_name) === hash);
        if (targetTheme) {
            selectMicrotheme(targetTheme);
            return;
        }
    }
    
    // Default select first high-yield microtheme
    if (DB.microthemes.length > 0) {
        selectMicrotheme(DB.microthemes[0]);
    }
}

// ============================================
// Event Listeners
// ============================================
function setupEventListeners() {
    // Global Search
    const searchInput = document.getElementById("global-search");
    const clearBtn = document.getElementById("clear-search");
    
    searchInput.addEventListener("input", (e) => {
        globalSearchQuery = e.target.value.toLowerCase().trim();
        clearBtn.style.display = globalSearchQuery ? "block" : "none";
        renderSidebarList();
    });

    clearBtn.addEventListener("click", () => {
        searchInput.value = "";
        globalSearchQuery = "";
        clearBtn.style.display = "none";
        renderSidebarList();
    });

    // Sorting & Filters
    document.getElementById("sort-select").addEventListener("change", (e) => {
        currentSort = e.target.value;
        renderSidebarList();
    });

    document.getElementById("yield-filter").addEventListener("change", (e) => {
        currentYieldFilter = e.target.value;
        renderSidebarList();
    });

    // Mode Toggle
    document.getElementById("mode-study").addEventListener("click", () => setMode(false));
    document.getElementById("mode-practice").addEventListener("click", () => setMode(true));

    // Question Tabs
    document.querySelectorAll(".q-tab").forEach(tab => {
        tab.addEventListener("click", (e) => {
            document.querySelectorAll(".q-tab").forEach(t => t.classList.remove("active"));
            e.currentTarget.classList.add("active");
            currentTab = e.currentTarget.dataset.tab;
            renderQuestions();
        });
    });

    // Toggle All Explanations
    document.getElementById("btn-toggle-all-exp").addEventListener("click", () => {
        const boxes = document.querySelectorAll(".qc-explanation-box");
        const allVisible = Array.from(boxes).every(b => b.style.display !== "none");
        boxes.forEach(b => b.style.display = allVisible ? "none" : "block");
        document.getElementById("btn-toggle-all-exp").textContent = allVisible ? "👁️ Expand All Explanations" : "🙈 Hide All Explanations";
    });

    // Mobile Drawer Controls
    const openPickerBtn = document.getElementById("mab-open-picker");
    const closeDrawerBtn = document.getElementById("drawer-close-btn");
    const backdrop = document.getElementById("sidebar-backdrop");

    if (openPickerBtn) openPickerBtn.addEventListener("click", openDrawer);
    if (closeDrawerBtn) closeDrawerBtn.addEventListener("click", closeDrawer);
    if (backdrop) backdrop.addEventListener("click", closeDrawer);

    // Theory Guide Modal
    document.getElementById("btn-theory-guide").addEventListener("click", openTheoryModal);
    document.getElementById("btn-close-modal").addEventListener("click", closeTheoryModal);
    document.getElementById("theory-modal").addEventListener("click", (e) => {
        if (e.target.id === "theory-modal") closeTheoryModal();
    });
}

function openDrawer() {
    const sidebar = document.getElementById("sidebar-pane");
    const backdrop = document.getElementById("sidebar-backdrop");
    if (sidebar) sidebar.classList.add("drawer-open");
    if (backdrop) backdrop.classList.add("active");
    document.body.style.overflow = "hidden"; // Prevent background scroll when drawer is open
}

function closeDrawer() {
    const sidebar = document.getElementById("sidebar-pane");
    const backdrop = document.getElementById("sidebar-backdrop");
    if (sidebar) sidebar.classList.remove("drawer-open");
    if (backdrop) backdrop.classList.remove("active");
    document.body.style.overflow = "";
}

function setMode(practice) {
    isPracticeMode = practice;
    document.getElementById("mode-study").classList.toggle("active", !practice);
    document.getElementById("mode-practice").classList.toggle("active", practice);
    renderQuestions();
}

// ============================================
// Render Subject Tabs Bar
// ============================================
function renderSubjectBar() {
    const container = document.getElementById("subject-tabs-container");
    container.innerHTML = "";

    // "All Subjects" Tab
    const allTab = document.createElement("button");
    allTab.className = `subject-tab ${currentSubject === "All" ? "active" : ""}`;
    allTab.innerHTML = `<span>📚 All Subjects</span> <span class="subject-tab-badge">${DB.metadata.total_microthemes}</span>`;
    allTab.addEventListener("click", () => {
        currentSubject = "All";
        updateActiveSubjectTab();
        renderSidebarList();
    });
    container.appendChild(allTab);

    // Subject Tabs
    DB.subjects.forEach(subj => {
        const tab = document.createElement("button");
        tab.className = `subject-tab ${currentSubject === subj.subject_name ? "active" : ""}`;
        tab.dataset.subject = subj.subject_name;
        tab.innerHTML = `<span>${subj.icon} ${subj.subject_name}</span> <span class="subject-tab-badge">${subj.microthemes.length}</span>`;
        tab.addEventListener("click", () => {
            currentSubject = subj.subject_name;
            updateActiveSubjectTab();
            renderSidebarList();
        });
        container.appendChild(tab);
    });
}

function updateActiveSubjectTab() {
    document.querySelectorAll(".subject-tab").forEach(tab => {
        const isMatch = (currentSubject === "All" && tab.textContent.includes("All Subjects")) ||
                        (tab.dataset.subject === currentSubject);
        tab.classList.toggle("active", isMatch);
    });
}

// ============================================
// Render Left Pane Microthemes
// ============================================
function renderSidebarList() {
    const container = document.getElementById("microtheme-cards-container");
    container.innerHTML = "";

    // Filter by subject
    let list = currentSubject === "All" ? [...DB.microthemes] : DB.microthemes.filter(m => m.subject === currentSubject);

    // Filter by yield
    if (currentYieldFilter !== "all") {
        list = list.filter(m => {
            if (currentYieldFilter === "high") return m.yield_class === "yield-high";
            if (currentYieldFilter === "medium") return m.yield_class === "yield-medium";
            if (currentYieldFilter === "standard") return m.yield_class === "yield-standard";
            return true;
        });
    }

    // Filter by search query
    if (globalSearchQuery) {
        list = list.filter(m => 
            m.theme_name.toLowerCase().includes(globalSearchQuery) ||
            m.subject.toLowerCase().includes(globalSearchQuery) ||
            m.cse_questions.some(q => q.question.toLowerCase().includes(globalSearchQuery))
        );
    }

    // Sort
    if (currentSort === "freq-desc") {
        list.sort((a, b) => b.total_cse_questions - a.total_cse_questions);
    } else if (currentSort === "recent-desc") {
        list.sort((a, b) => b.recent_count_last_7_yrs - a.recent_count_last_7_yrs || b.total_cse_questions - a.total_cse_questions);
    } else if (currentSort === "alpha-asc") {
        list.sort((a, b) => a.theme_name.localeCompare(b.theme_name));
    } else if (currentSort === "total-all") {
        list.sort((a, b) => b.total_all_questions - a.total_all_questions);
    }

    document.getElementById("current-subject-title").textContent = currentSubject === "All" ? "All Microthemes" : currentSubject;
    document.getElementById("theme-count-badge").textContent = `${list.length} Themes`;

    if (list.length === 0) {
        container.innerHTML = `<div style="text-align:center; padding: 2rem; color: var(--text-muted); font-size: 0.85rem;">No microthemes found matching the criteria.</div>`;
        return;
    }

    list.forEach(m => {
        const card = document.createElement("div");
        card.className = `mt-card ${currentMicrotheme && currentMicrotheme.id === m.id ? "active" : ""}`;
        card.dataset.id = m.id;
        
        card.innerHTML = `
            <div class="mt-card-top">
                <span class="mt-yield-badge ${m.yield_class}">${m.yield_badge.split(' ')[0]} ${m.yield_badge.split(' ')[1]}</span>
                <span class="mt-q-count">${m.total_cse_questions} CSE PYQs</span>
            </div>
            <div class="mt-card-title">${escapeHtml(m.theme_name)}</div>
            <div class="mt-card-footer">
                <span>${m.subject}</span>
                <span class="mt-years-span">${m.years_appeared.slice(0, 4).join(', ')}${m.years_appeared.length > 4 ? '...' : ''}</span>
            </div>
        `;

        card.addEventListener("click", () => selectMicrotheme(m));
        container.appendChild(card);
    });
}

// ============================================
// Select Microtheme
// ============================================
function selectMicrotheme(m) {
    currentMicrotheme = m;
    window.location.hash = m.id;

    // Update active state in sidebar
    document.querySelectorAll(".mt-card").forEach(c => {
        c.classList.toggle("active", c.dataset.id === m.id);
    });

    // Update Mobile Active Bar
    const mabSubject = document.getElementById("mab-subject");
    const mabTitle = document.getElementById("mab-theme-title");
    const mabCount = document.getElementById("mab-count");
    if (mabSubject) mabSubject.textContent = m.subject;
    if (mabTitle) mabTitle.textContent = m.theme_name;
    if (mabCount) mabCount.textContent = `${m.total_cse_questions} Qs`;

    renderHeroBanner(m);
    renderQuestions();

    // Close drawer on mobile if open
    closeDrawer();

    // Scroll to top of questions smoothly
    if (window.innerWidth <= 1024) {
        const detailPane = document.getElementById("detail-pane");
        if (detailPane) {
            detailPane.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    }
}

function renderHeroBanner(m) {
    document.getElementById("hero-subject-badge").textContent = m.subject;
    
    const yieldEl = document.getElementById("hero-yield-badge");
    yieldEl.className = `yield-badge-pill ${m.yield_class}`;
    yieldEl.textContent = m.yield_badge;

    document.getElementById("hero-freq-stat").textContent = `${m.total_cse_questions} CSE Occurrences`;
    document.getElementById("hero-theme-title").textContent = m.theme_name;
    document.getElementById("hero-theme-desc").textContent = 
        `Mastering "${m.theme_name}" gives you direct coverage over ${m.total_cse_questions} historical UPSC CSE questions, plus ${m.total_cross_exam_questions} practice questions from CDS & CAPF.`;

    document.getElementById("hsb-cse-count").textContent = m.total_cse_questions;
    document.getElementById("hsb-cross-count").textContent = m.total_cross_exam_questions;
    document.getElementById("hsb-years-span").textContent = `${m.years_appeared.length} Years`;
    document.getElementById("hsb-recent-rate").textContent = `${m.recent_count_last_7_yrs} Qs (2018–2025)`;

    // Render Year timeline pills
    const yearsContainer = document.getElementById("hero-years-pills");
    yearsContainer.innerHTML = m.years_appeared.map(y => `<span class="yt-pill">${y}</span>`).join("");

    // Update Tab count badges
    document.getElementById("tab-cse-count").textContent = m.total_cse_questions;
    document.getElementById("tab-cross-count").textContent = m.total_cross_exam_questions;
    document.getElementById("tab-all-count").textContent = m.total_all_questions;
}

// ============================================
// Render Questions
// ============================================
function renderQuestions() {
    const container = document.getElementById("questions-stream");
    container.innerHTML = "";

    if (!currentMicrotheme) return;

    let questionsToRender = [];
    if (currentTab === "cse") {
        questionsToRender = currentMicrotheme.cse_questions;
    } else if (currentTab === "cross") {
        questionsToRender = currentMicrotheme.cross_exam_questions;
    } else {
        questionsToRender = [...currentMicrotheme.cse_questions, ...currentMicrotheme.cross_exam_questions];
    }

    if (questionsToRender.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 3rem; background: var(--bg-surface); border-radius: var(--radius-md); border: 1px solid var(--border-subtle); color: var(--text-muted);">
                <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">No questions available in this tab.</p>
                <p style="font-size: 0.8rem;">Try switching to the "UPSC CSE Prelims" or "All Questions" tab.</p>
            </div>
        `;
        return;
    }

    questionsToRender.forEach((q, idx) => {
        const card = createQuestionCard(q, idx + 1);
        container.appendChild(card);
    });
}

function createQuestionCard(q, index) {
    const card = document.createElement("div");
    card.className = "question-card-portal";

    const isCSE = q.paper === "GS";
    const examClass = isCSE ? "exam-cse" : q.paper === "GK" ? "exam-cds" : "exam-capf";
    const examName = q.exam || (isCSE ? "UPSC CSE GS" : q.paper === "GK" ? "UPSC CDS GK" : "UPSC CAPF GAI");

    const isAnsA = q.correct_answer === "A" || q.correct_answer === "Option A";
    const isAnsB = q.correct_answer === "B" || q.correct_answer === "Option B";
    const isAnsC = q.correct_answer === "C" || q.correct_answer === "Option C";
    const isAnsD = q.correct_answer === "D" || q.correct_answer === "Option D";

    card.innerHTML = `
        <div class="qc-header">
            <div class="qc-badges">
                <span class="exam-pill ${examClass}">${q.year} ${examName}</span>
                <span style="font-size: 0.72rem; color: var(--text-muted); font-family: 'JetBrains Mono', monospace;">Q#${index}</span>
            </div>
            ${q.correct_answer ? `<span class="correct-tag" style="${isPracticeMode ? 'display:none;' : ''}">Ans: Option ${q.correct_answer}</span>` : ''}
        </div>

        <div class="qc-question-body">${formatQuestionText(q.question)}</div>

        ${q.option_a ? `
        <div class="qc-options-grid">
            <div class="qc-option ${(!isPracticeMode && isAnsA) ? 'is-correct' : ''}" data-opt="A">
                <span class="qc-option-badge">A</span>
                <span class="qc-option-text">${escapeHtml(q.option_a)}</span>
                ${(!isPracticeMode && isAnsA) ? '<span class="correct-tag">✓ Correct</span>' : ''}
            </div>
            <div class="qc-option ${(!isPracticeMode && isAnsB) ? 'is-correct' : ''}" data-opt="B">
                <span class="qc-option-badge">B</span>
                <span class="qc-option-text">${escapeHtml(q.option_b)}</span>
                ${(!isPracticeMode && isAnsB) ? '<span class="correct-tag">✓ Correct</span>' : ''}
            </div>
            <div class="qc-option ${(!isPracticeMode && isAnsC) ? 'is-correct' : ''}" data-opt="C">
                <span class="qc-option-badge">C</span>
                <span class="qc-option-text">${escapeHtml(q.option_c)}</span>
                ${(!isPracticeMode && isAnsC) ? '<span class="correct-tag">✓ Correct</span>' : ''}
            </div>
            <div class="qc-option ${(!isPracticeMode && isAnsD) ? 'is-correct' : ''}" data-opt="D">
                <span class="qc-option-badge">D</span>
                <span class="qc-option-text">${escapeHtml(q.option_d)}</span>
                ${(!isPracticeMode && isAnsD) ? '<span class="correct-tag">✓ Correct</span>' : ''}
            </div>
        </div>
        ` : ''}

        ${q.explanation ? `
        <div class="qc-explanation-box" style="${isPracticeMode ? 'display:none;' : ''}">
            <div class="qc-exp-header">
                <span class="qc-exp-title">💡 Official Concept Explanation</span>
            </div>
            <div class="qc-exp-content">${formatExplanationText(q.explanation)}</div>
        </div>
        ` : ''}

        <div class="qc-action-bar">
            ${isPracticeMode ? `<button class="btn-toggle-answer">👁️ Reveal Answer & Explanation</button>` : `<span></span>`}
            <span style="font-size:0.7rem; color:var(--text-dim);">${escapeHtml(q.tags || currentMicrotheme.theme_name)}</span>
        </div>
    `;

    // Interactive Option Selection in Practice Mode
    if (isPracticeMode) {
        const optionEls = card.querySelectorAll(".qc-option");
        optionEls.forEach(optEl => {
            optEl.addEventListener("click", () => {
                const selectedOpt = optEl.dataset.opt;
                const correctOpt = q.correct_answer;

                optionEls.forEach(o => {
                    o.classList.remove("is-correct", "is-selected-wrong");
                    if (o.dataset.opt === correctOpt) o.classList.add("is-correct");
                });

                if (selectedOpt !== correctOpt) {
                    optEl.classList.add("is-selected-wrong");
                }

                // Reveal explanation
                const expBox = card.querySelector(".qc-explanation-box");
                if (expBox) expBox.style.display = "block";
            });
        });

        const revealBtn = card.querySelector(".btn-toggle-answer");
        if (revealBtn) {
            revealBtn.addEventListener("click", () => {
                const expBox = card.querySelector(".qc-explanation-box");
                if (expBox) expBox.style.display = expBox.style.display === "none" ? "block" : "none";
                optionEls.forEach(o => {
                    if (o.dataset.opt === q.correct_answer) o.classList.add("is-correct");
                });
            });
        }
    }

    return card;
}

// ============================================
// Text & Formatting Helpers
// ============================================
function formatQuestionText(text) {
    if (!text) return "";
    let clean = escapeHtml(text);
    clean = clean.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    clean = clean.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Statements formatting
    clean = clean.replace(/(\b[1-4]\.\s+[^1-4]+)/g, '<div class="statement-row">• $1</div>');
    clean = clean.replace(/(Statement[\s-]*[I|1|2|II]+:?\s*)/gi, '<strong style="color:var(--accent-amber)">$1</strong>');
    return clean;
}

function formatExplanationText(text) {
    if (!text) return "";
    let clean = escapeHtml(text);
    clean = clean.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    clean = clean.replace(/\*(.*?)\*/g, '<em>$1</em>');
    clean = clean.replace(/\n\s*\*\s+/g, '<br>• ');
    clean = clean.replace(/\n\n/g, '<br><br>');
    clean = clean.replace(/\n/g, '<br>');
    return clean;
}

function escapeHtml(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// Political Theory Modal
// ============================================
function openTheoryModal() {
    const modal = document.getElementById("theory-modal");
    const content = document.getElementById("theory-modal-content");
    
    if (DB && DB.theory_guides && DB.theory_guides.political_theory) {
        content.innerHTML = parseSimpleMarkdown(DB.theory_guides.political_theory);
    } else {
        content.innerHTML = "<p>Loading Political Theory Guide...</p>";
    }
    
    modal.style.display = "flex";
}

function closeTheoryModal() {
    document.getElementById("theory-modal").style.display = "none";
}

function parseSimpleMarkdown(md) {
    let html = escapeHtml(md);
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>');
    html = html.replace(/^\> (.*$)/gim, '<blockquote style="border-left: 3px solid var(--accent-indigo); padding-left: 1rem; color: var(--accent-indigo-light); margin: 1rem 0;">$1</blockquote>');
    html = html.replace(/\n\n/g, '<br><br>');
    return html;
}
