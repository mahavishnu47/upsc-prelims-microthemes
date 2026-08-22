/**
 * UPSC CSE 2024 PYQ Microtheme Dashboard — Application Logic
 * Loads analysis JSON and renders interactive charts + question table
 */

// Subject color map
const SUBJECT_COLORS = {
    "History": "#818cf8",
    "Polity & Governance": "#34d399",
    "Economy": "#fbbf24",
    "Geography": "#22d3ee",
    "Environment & Ecology": "#4ade80",
    "Science & Technology": "#f472b6",
    "International Relations": "#a78bfa",
    "Social Issues & Schemes": "#fb923c",
};

const EXAM_LABELS = {
    "GS": "UPSC CSE GS",
    "GAI": "CAPF GAI",
    "GK": "CDS GK",
};

const EXAM_COLORS = {
    "GS": "#818cf8",
    "GAI": "#fbbf24",
    "GK": "#22d3ee",
};

let DATA = null;
let allQuestionCards = [];

// ============================================
// Data Loading
// ============================================
async function loadData() {
    try {
        // Use inline data if available (loaded via data.js script tag)
        if (typeof ANALYSIS_DATA !== "undefined") {
            DATA = ANALYSIS_DATA;
            renderAll();
            return;
        }
        // Fallback to fetch (works when served via HTTP)
        const resp = await fetch("data/analysis_results.json");
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        DATA = await resp.json();
        renderAll();
    } catch (err) {
        console.error("Failed to load data:", err);
        document.getElementById("hero-pct").textContent = "Error";
        document.getElementById("insight-text").textContent =
            "Failed to load analysis data. Please open this page via http://localhost:8765 or ensure data.js exists.";
    }
}

// ============================================
// Render All Sections
// ============================================
function renderAll() {
    renderHero();
    renderSubjectChart();
    renderYearChart();
    renderExamChart();
    renderCoverageChart();
    renderInsight();
    renderQuestionTable();
    setupFilters();
}

// ============================================
// Hero Stats
// ============================================
function renderHero() {
    const agg = DATA.aggregate;

    animateNumber("hero-pct", agg.pct_any_match, "%");
    animateNumber("stat-any-match", agg.questions_with_any_pyq_match, "/100");
    document.getElementById("stat-any-pct").textContent = `${agg.pct_any_match}% coverage`;

    animateNumber("stat-strong-match", agg.questions_with_strong_match, "/100");
    document.getElementById("stat-strong-pct").textContent = `${agg.pct_strong_match}% strong overlap`;

    document.getElementById("stat-avg-matches").textContent = agg.avg_matches_per_question;
    document.getElementById("stat-corpus").textContent = DATA.pyq_corpus_size.toLocaleString();
    document.getElementById("corpus-size-badge").textContent = `${DATA.pyq_corpus_size.toLocaleString()} PYQs analyzed`;
}

function animateNumber(elementId, target, suffix = "") {
    const el = document.getElementById(elementId);
    const duration = 1500;
    const start = performance.now();
    const startVal = 0;

    function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(startVal + (target - startVal) * eased);
        el.textContent = current + suffix;
        if (progress < 1) requestAnimationFrame(update);
    }

    requestAnimationFrame(update);
}

// ============================================
// Subject Chart
// ============================================
function renderSubjectChart() {
    const ctx = document.getElementById("subjectChart").getContext("2d");
    const subjects = Object.entries(DATA.subject_breakdown);

    // Sort by total descending
    subjects.sort((a, b) => b[1].total - a[1].total);

    const labels = subjects.map(([name]) => name);
    const totalData = subjects.map(([, v]) => v.total);
    const matchedData = subjects.map(([, v]) => v.matched);
    const strongData = subjects.map(([, v]) => v.strong);

    new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [
                {
                    label: "Total Questions",
                    data: totalData,
                    backgroundColor: "rgba(255,255,255,0.08)",
                    borderColor: "rgba(255,255,255,0.15)",
                    borderWidth: 1,
                    borderRadius: 6,
                    barPercentage: 0.8,
                },
                {
                    label: "Any PYQ Match",
                    data: matchedData,
                    backgroundColor: "rgba(99,102,241,0.4)",
                    borderColor: "#6366f1",
                    borderWidth: 1,
                    borderRadius: 6,
                    barPercentage: 0.8,
                },
                {
                    label: "Strong Overlap (≥30%)",
                    data: strongData,
                    backgroundColor: "rgba(16,185,129,0.5)",
                    borderColor: "#10b981",
                    borderWidth: 1,
                    borderRadius: 6,
                    barPercentage: 0.8,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "top",
                    labels: { color: "#94a3b8", font: { size: 11, family: "Inter" }, padding: 16 },
                },
                tooltip: {
                    backgroundColor: "#1e293b",
                    titleColor: "#f1f5f9",
                    bodyColor: "#94a3b8",
                    borderColor: "#334155",
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12,
                },
            },
            scales: {
                x: {
                    ticks: { color: "#64748b", font: { size: 10 } },
                    grid: { display: false },
                },
                y: {
                    ticks: { color: "#64748b", font: { size: 10 } },
                    grid: { color: "rgba(255,255,255,0.04)" },
                },
            },
        },
    });
}

// ============================================
// Year Chart
// ============================================
function renderYearChart() {
    const ctx = document.getElementById("yearChart").getContext("2d");
    const years = Object.entries(DATA.year_heatmap).sort((a, b) => a[0].localeCompare(b[0]));

    const labels = years.map(([y]) => y);
    const values = years.map(([, v]) => v);
    const maxVal = Math.max(...values);

    // Color gradient based on value
    const bgColors = values.map((v) => {
        const intensity = v / maxVal;
        return `rgba(99, 102, 241, ${0.2 + intensity * 0.6})`;
    });

    new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [
                {
                    label: "Microtheme Matches",
                    data: values,
                    backgroundColor: bgColors,
                    borderColor: values.map((v) => {
                        const intensity = v / maxVal;
                        return `rgba(129, 140, 248, ${0.4 + intensity * 0.6})`;
                    }),
                    borderWidth: 1,
                    borderRadius: 6,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: "#1e293b",
                    titleColor: "#f1f5f9",
                    bodyColor: "#94a3b8",
                    borderColor: "#334155",
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: (ctx) => `${ctx.parsed.y} microtheme matches contributed`,
                    },
                },
            },
            scales: {
                x: {
                    ticks: { color: "#64748b", font: { size: 10, family: "JetBrains Mono" } },
                    grid: { display: false },
                },
                y: {
                    ticks: { color: "#64748b", font: { size: 10 } },
                    grid: { color: "rgba(255,255,255,0.04)" },
                },
            },
        },
    });
}

// ============================================
// Exam Contribution Doughnut
// ============================================
function renderExamChart() {
    const ctx = document.getElementById("examChart").getContext("2d");
    const exams = Object.entries(DATA.exam_contribution);

    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: exams.map(([k]) => EXAM_LABELS[k] || k),
            datasets: [
                {
                    data: exams.map(([, v]) => v),
                    backgroundColor: exams.map(([k]) => EXAM_COLORS[k] || "#6366f1"),
                    borderColor: "#0a0e1a",
                    borderWidth: 3,
                    hoverOffset: 8,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "65%",
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        color: "#94a3b8",
                        font: { size: 11, family: "Inter" },
                        padding: 16,
                        usePointStyle: true,
                        pointStyleWidth: 10,
                    },
                },
                tooltip: {
                    backgroundColor: "#1e293b",
                    titleColor: "#f1f5f9",
                    bodyColor: "#94a3b8",
                    borderColor: "#334155",
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: (ctx) => {
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = ((ctx.parsed / total) * 100).toFixed(1);
                            return `${ctx.label}: ${ctx.parsed} matches (${pct}%)`;
                        },
                    },
                },
            },
        },
    });
}

// ============================================
// Coverage Distribution Doughnut
// ============================================
function renderCoverageChart() {
    const ctx = document.getElementById("coverageChart").getContext("2d");
    const agg = DATA.aggregate;

    const strong = agg.questions_with_strong_match;
    const anyOnly = agg.questions_with_any_pyq_match - strong;
    const none = DATA.total_questions - agg.questions_with_any_pyq_match;

    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Strong Overlap (≥30%)", "Moderate Match", "No PYQ Match"],
            datasets: [
                {
                    data: [strong, anyOnly, none],
                    backgroundColor: ["#10b981", "#f59e0b", "#ef4444"],
                    borderColor: "#0a0e1a",
                    borderWidth: 3,
                    hoverOffset: 8,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "65%",
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        color: "#94a3b8",
                        font: { size: 11, family: "Inter" },
                        padding: 16,
                        usePointStyle: true,
                        pointStyleWidth: 10,
                    },
                },
                tooltip: {
                    backgroundColor: "#1e293b",
                    titleColor: "#f1f5f9",
                    bodyColor: "#94a3b8",
                    borderColor: "#334155",
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: (ctx) => `${ctx.label}: ${ctx.parsed} questions`,
                    },
                },
            },
        },
    });
}

// ============================================
// Key Insight
// ============================================
function renderInsight() {
    const agg = DATA.aggregate;
    const subj = DATA.subject_breakdown;

    // Find best covered subject
    let bestSubj = "";
    let bestPct = 0;
    for (const [name, stats] of Object.entries(subj)) {
        if (stats.pct_matched > bestPct && stats.total >= 3) {
            bestPct = stats.pct_matched;
            bestSubj = name;
        }
    }

    // Find year with most matches
    const yearEntries = Object.entries(DATA.year_heatmap).sort((a, b) => b[1] - a[1]);
    const topYear = yearEntries[0];

    document.getElementById("insight-text").innerHTML = `
        <strong>${agg.pct_any_match}% of UPSC CSE 2024 questions</strong> had microthemes that appeared in previous year questions.
        <strong>${bestSubj}</strong> had the highest PYQ coverage at <strong>${bestPct}%</strong>.
        The year <strong>${topYear[0]}</strong> contributed the most matching microthemes (${topYear[1]} matches).
        UPSC CSE PYQs alone contributed <strong>${DATA.exam_contribution.GS || 0}</strong> matches,
        while CDS GK added <strong>${DATA.exam_contribution.GK || 0}</strong> and CAPF GAI added <strong>${DATA.exam_contribution.GAI || 0}</strong>.
        This proves that a systematic PYQ-driven study plan covering all three exams can help you answer the vast majority of UPSC CSE Prelims questions.
    `;
}

// ============================================
// Question Table
// ============================================
function renderQuestionTable() {
    const container = document.getElementById("questions-table");
    container.innerHTML = "";
    allQuestionCards = [];

    // Populate subject filter
    const subjectSelect = document.getElementById("filter-subject");
    const subjects = [...new Set(DATA.questions.map((q) => q.normalized_subject))].sort();
    subjects.forEach((s) => {
        const opt = document.createElement("option");
        opt.value = s;
        opt.textContent = s;
        subjectSelect.appendChild(opt);
    });

    DATA.questions.forEach((q) => {
        const card = createQuestionCard(q);
        container.appendChild(card);
        allQuestionCards.push({ element: card, data: q });
    });
}

// ============================================
// Text and Markdown Formatter Helpers
// ============================================
function formatRichText(rawText) {
    if (!rawText) return "";
    let text = rawText.trim();

    // Check if text contains markdown table
    if (text.includes("|") && text.includes("---")) {
        const lines = text.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
        const tableLines = [];
        const otherLinesBefore = [];
        const otherLinesAfter = [];
        let inTable = false;
        let tableFinished = false;

        for (const line of lines) {
            if (line.startsWith("|") && line.endsWith("|")) {
                inTable = true;
                tableLines.push(line);
            } else {
                if (inTable) tableFinished = true;
                if (!tableFinished) otherLinesBefore.push(line);
                else otherLinesAfter.push(line);
            }
        }

        if (tableLines.length >= 2) {
            let htmlTable = '<div class="table-responsive"><table class="md-table">';
            const headerRow = tableLines[0].split("|").filter((c, i, a) => i > 0 && i < a.length - 1);
            htmlTable += '<thead><tr>' + headerRow.map(h => `<th>${escapeHtml(h.trim())}</th>`).join('') + '</tr></thead>';
            htmlTable += '<tbody>';
            for (let i = 2; i < tableLines.length; i++) {
                const cells = tableLines[i].split("|").filter((c, idx, a) => idx > 0 && idx < a.length - 1);
                htmlTable += '<tr>' + cells.map(c => `<td>${escapeHtml(c.trim())}</td>`).join('') + '</tr>';
            }
            htmlTable += '</tbody></table></div>';

            const beforeHtml = otherLinesBefore.map(l => formatInlineText(l)).join("<br>");
            const afterHtml = otherLinesAfter.map(l => formatInlineText(l)).join("<br>");
            return `${beforeHtml ? beforeHtml + '<br>' : ''}${htmlTable}${afterHtml ? '<br>' + afterHtml : ''}`;
        }
    }

    // Convert bullet points & numbered statements cleanly
    return formatStatementsAndPoints(text);
}

function formatStatementsAndPoints(text) {
    // Format bold text
    let formatted = escapeHtml(text);
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Format numbered statements like 1. ... 2. ... 3. ...
    formatted = formatted.replace(/(\b[1-4]\.\s+[^1-4]+)/g, '<div class="statement-item"><span class="stmt-badge">•</span> $1</div>');
    formatted = formatted.replace(/(Statement[\s-]*[I|1|2|II]+:?\s*)/gi, '<strong class="stmt-label">$1</strong>');

    return formatted;
}

function formatInlineText(text) {
    let formatted = escapeHtml(text);
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    return formatted;
}

function formatExplanation(text) {
    if (!text) return "";
    let formatted = escapeHtml(text);
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    // Clean bullet points
    formatted = formatted.replace(/\n\s*\*\s+/g, '<br>• ');
    formatted = formatted.replace(/\n\n/g, '<br><br>');
    formatted = formatted.replace(/\n/g, '<br>');
    return formatted;
}

function createQuestionCard(q) {
    const card = document.createElement("div");
    card.className = "question-card";
    card.dataset.subject = q.normalized_subject;
    card.dataset.coverage = q.has_strong_coverage ? "strong" : q.has_pyq_coverage ? "any" : "none";

    const subjectColor = SUBJECT_COLORS[q.normalized_subject] || "#6366f1";

    // Coverage badge
    let coverageClass, coverageText;
    if (q.has_strong_coverage) {
        coverageClass = "coverage-strong";
        coverageText = "Strong";
    } else if (q.has_pyq_coverage) {
        coverageClass = "coverage-any";
        coverageText = "Match";
    } else {
        coverageClass = "coverage-none";
        coverageText = "None";
    }

    // Main summary row
    const row = document.createElement("div");
    row.className = "question-row";
    row.innerHTML = `
        <div class="q-num">Q${q.question_number}</div>
        <div class="q-text">${escapeHtml(q.question_text)}</div>
        <div class="q-subject">
            <div class="subject-dot" style="background:${subjectColor}"></div>
            <span class="subject-name">${q.normalized_subject}</span>
        </div>
        <div class="q-matches" style="color:${q.total_pyq_matches > 0 ? '#10b981' : '#64748b'}">${q.total_pyq_matches} PYQs</div>
        <div class="q-coverage">
            <span class="coverage-badge ${coverageClass}">${coverageText}</span>
        </div>
        <div class="q-expand">▼</div>
    `;

    row.addEventListener("click", () => {
        card.classList.toggle("expanded");
    });

    const isAnsA = q.correct_answer === "A" || q.correct_answer === "Option A";
    const isAnsB = q.correct_answer === "B" || q.correct_answer === "Option B";
    const isAnsC = q.correct_answer === "C" || q.correct_answer === "Option C";
    const isAnsD = q.correct_answer === "D" || q.correct_answer === "Option D";

    // Detail section
    const detail = document.createElement("div");
    detail.className = "question-detail";
    detail.innerHTML = `
        <div class="detail-grid">
            <!-- Full Question with formatting -->
            <div class="detail-block detail-block-full question-main-box">
                <div class="detail-header-bar">
                    <span class="detail-label">Question Text</span>
                    <span class="diff-badge diff-${(q.difficulty || 'medium').toLowerCase()}">${(q.difficulty || 'medium').toUpperCase()}</span>
                </div>
                <div class="formatted-question-body">${formatRichText(q.question_text)}</div>
                
                <!-- Options Grid -->
                <div class="options-container">
                    <div class="options-title">OPTIONS</div>
                    <div class="options-grid">
                        <div class="option-item ${isAnsA ? 'option-correct' : ''}">
                            <div class="opt-badge">A</div>
                            <div class="opt-text">${escapeHtml(q.option_a || '—')}</div>
                            ${isAnsA ? '<span class="correct-check">✓ Correct Answer</span>' : ''}
                        </div>
                        <div class="option-item ${isAnsB ? 'option-correct' : ''}">
                            <div class="opt-badge">B</div>
                            <div class="opt-text">${escapeHtml(q.option_b || '—')}</div>
                            ${isAnsB ? '<span class="correct-check">✓ Correct Answer</span>' : ''}
                        </div>
                        <div class="option-item ${isAnsC ? 'option-correct' : ''}">
                            <div class="opt-badge">C</div>
                            <div class="opt-text">${escapeHtml(q.option_c || '—')}</div>
                            ${isAnsC ? '<span class="correct-check">✓ Correct Answer</span>' : ''}
                        </div>
                        <div class="option-item ${isAnsD ? 'option-correct' : ''}">
                            <div class="opt-badge">D</div>
                            <div class="opt-text">${escapeHtml(q.option_d || '—')}</div>
                            ${isAnsD ? '<span class="correct-check">✓ Correct Answer</span>' : ''}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Book Canonical Microtheme Banner -->
            <div class="detail-block detail-block-full canonical-theme-box">
                <div class="canonical-header">
                    <span class="canonical-badge">📚 Canonical Book Microtheme (2009–2025)</span>
                    <span class="theme-freq-badge">${q.theme_total_pyq_count || q.past_cse_same_theme_count} PYQs in this Theme</span>
                </div>
                <div class="canonical-theme-title">${escapeHtml(q.canonical_microtheme || q.subject)}</div>
                <div class="canonical-subject-sub">Subject Section: <strong>${q.canonical_subject || q.subject}</strong> &bull; Tested in Previous CSE Exams: <strong>${q.past_cse_same_theme_count || q.years_with_matches.length} times</strong> (${q.years_with_matches.join(', ')})</div>
            </div>

            <!-- Subject & Topics -->
            <div class="detail-block">
                <div class="detail-label">Subject / Sub-Theme</div>
                <div class="detail-value">
                    <strong style="color:#f1f5f9">${q.subject}</strong><br>
                    <span style="color:#94a3b8; font-size:0.8rem">${q.original_topics || 'General Topic'}</span>
                </div>
            </div>

            <!-- Years with Matches -->
            <div class="detail-block">
                <div class="detail-label">Years with Matches in PYQs</div>
                <div class="detail-value">
                    <div class="years-pills">
                        ${q.years_with_matches.map((y) => `<span class="year-pill">${y}</span>`).join("")}
                        ${q.years_with_matches.length === 0 ? '<span style="color:#64748b">No matches found in previous years</span>' : ''}
                    </div>
                </div>
            </div>

            <!-- Nuanced Microthemes -->
            <div class="detail-block detail-block-full microthemes-box">
                <div class="detail-label">Nuanced Microthemes (Core Concepts Tested)</div>
                <div class="microtheme-list">
                    ${q.nuanced_microthemes.map((mt) => `<span class="microtheme-tag">💡 ${escapeHtml(mt)}</span>`).join("")}
                </div>
            </div>

            <!-- Same-Theme Historical CSE Questions from Book -->
            ${q.past_cse_same_theme_questions && q.past_cse_same_theme_questions.length > 0 ? `
            <div class="detail-block detail-block-full same-theme-box">
                <div class="detail-label">Previous UPSC CSE Questions in this Exact Microtheme (${q.past_cse_same_theme_questions.length} Questions)</div>
                <div class="same-theme-list">
                    ${q.past_cse_same_theme_questions.map((pt) => `
                        <div class="same-theme-item">
                            <span class="same-theme-year">${pt.year} CSE</span>
                            <span class="same-theme-q">${escapeHtml(pt.text)}</span>
                        </div>
                    `).join("")}
                </div>
            </div>
            ` : ''}

            <!-- Official Explanation -->
            ${q.explanation ? `
            <div class="detail-block detail-block-full explanation-box">
                <div class="detail-label">Official Solution & Concept Explanation</div>
                <div class="explanation-content">${formatExplanation(q.explanation)}</div>
            </div>
            ` : ''}

            <!-- Matching PYQs Across Exams -->
            ${q.matching_pyqs.length > 0 ? `
            <div class="detail-block detail-block-full pyq-container-box">
                <div class="detail-label">Top Matching PYQs Across All Exams (${q.total_pyq_matches} Found in CSE, CDS, CAPF)</div>
                <div class="pyq-matches-list">
                    ${q.matching_pyqs.slice(0, 10).map((m, idx) => `
                        <div class="pyq-match-card">
                            <div class="pyq-meta">
                                <span class="pyq-year">${m.year}</span>
                                <span class="pyq-exam pyq-exam-${m.paper.toLowerCase()}">${m.paper}</span>
                                <div class="pyq-sim-badge">${(m.similarity * 100).toFixed(0)}% Match</div>
                            </div>
                            <div class="pyq-body-wrap">
                                <div class="pyq-question">${formatRichText(m.question)}</div>
                                
                                <!-- PYQ Options if present -->
                                ${m.option_a ? `
                                <div class="pyq-options-mini">
                                    <span class="pyq-opt ${m.correct_answer === 'A' ? 'pyq-opt-ans' : ''}"><strong>A:</strong> ${escapeHtml(m.option_a)}</span>
                                    <span class="pyq-opt ${m.correct_answer === 'B' ? 'pyq-opt-ans' : ''}"><strong>B:</strong> ${escapeHtml(m.option_b)}</span>
                                    <span class="pyq-opt ${m.correct_answer === 'C' ? 'pyq-opt-ans' : ''}"><strong>C:</strong> ${escapeHtml(m.option_c)}</span>
                                    <span class="pyq-opt ${m.correct_answer === 'D' ? 'pyq-opt-ans' : ''}"><strong>D:</strong> ${escapeHtml(m.option_d)}</span>
                                </div>
                                ` : ''}

                                <div class="pyq-keywords">
                                    <span class="kw-label">Overlapping Concepts:</span>
                                    ${m.matching_keywords.slice(0, 8).map((k) => `<span class="kw-tag">${k}</span>`).join("")}
                                </div>
                            </div>
                        </div>
                    `).join("")}
                </div>
            </div>
            ` : ''}
        </div>
    `;

    card.appendChild(row);
    card.appendChild(detail);
    return card;
}

// ============================================
// Filters
// ============================================
function setupFilters() {
    document.getElementById("filter-subject").addEventListener("change", applyFilters);
    document.getElementById("filter-coverage").addEventListener("change", applyFilters);
    document.getElementById("search-input").addEventListener("input", applyFilters);
}

function applyFilters() {
    const subject = document.getElementById("filter-subject").value;
    const coverage = document.getElementById("filter-coverage").value;
    const search = document.getElementById("search-input").value.toLowerCase().trim();

    allQuestionCards.forEach(({ element, data }) => {
        let visible = true;

        if (subject !== "all" && data.normalized_subject !== subject) visible = false;
        if (coverage !== "all" && element.dataset.coverage !== coverage) visible = false;
        if (search && !data.question_text.toLowerCase().includes(search) &&
            !data.nuanced_microthemes.some((mt) => mt.toLowerCase().includes(search))) {
            visible = false;
        }

        element.style.display = visible ? "" : "none";
    });
}

// ============================================
// Utilities
// ============================================
function escapeHtml(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// Initialize
// ============================================
document.addEventListener("DOMContentLoaded", loadData);
