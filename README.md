# ⚡ UPSC Prelims Canonical Microtheme Master Hub (2009–2026)

> **A one-stop, data-driven platform for UPSC Civil Services Prelims preparation powered by 17 years of canonical microtheme analysis across UPSC CSE, CAPF (AC), and CDS examinations.**

[![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-Live_Portal-success?style=for-the-badge&logo=github)](https://mahavishnu47.github.io/upsc-prelims-microthemes/)
[![Questions Cataloged](https://img.shields.io/badge/Questions_Cataloged-6%2C215-blue?style=for-the-badge)](output/all_exams_prelims.csv)
[![Canonical Microthemes](https://img.shields.io/badge/Canonical_Microthemes-183-orange?style=for-the-badge)](dashboard/data/book_microthemes.json)
[![Coverage Rate](https://img.shields.io/badge/CSE_2024_PYQ_Overlap-100%25-brightgreen?style=for-the-badge)](dashboard/index.html)

---

## 📌 Executive Summary

UPSC Civil Services Prelims questions are not random—they consistently revolve around specific, high-frequency **canonical microthemes**. By analyzing **6,215 questions** across 17+ years of UPSC examinations:
- **100% (100/100)** of UPSC CSE 2024 General Studies questions map directly to recurring microthemes.
- **93% (93/100)** have **strong direct overlap** (tested 3+ times in prior CSE exams or high-similarity multi-exam matches in CDS/CAPF).
- This repository provides the complete dataset, analysis engines, study guides, and an **interactive Web Portal** for microtheme-based preparation.

---

## 🌐 Interactive Web Portals

### 1. 🌟 Microtheme Master Study Portal (`/docs` & `portal/`)
The primary destination for students:
- **183 Canonical Microthemes** organized across all 11 standard UPSC subjects.
- **Instant Drill-Down**: Click any microtheme to view all historical questions with frequency trends (e.g. *"Asked 14 times between 2009–2025"*).
- **Interactive Options & Explanations**: Options A, B, C, D with emerald green highlights for the correct answer.
- **Study Mode vs Practice Mode**: Test yourself by clicking options with instant feedback or study with full concept explanations.
- **Cross-Exam Integration**: Easily switch between *UPSC CSE Prelims*, *CDS & CAPF Practice*, and *All Questions*.
- **Integrated Theory Guides**: Built-in modal reader for master conceptual guides.

### 2. 📊 CSE 2024 Overlap Analyzer Dashboard (`dashboard/`)
- Visual dashboard showing the microtheme overlap of the 2024 paper against 6,115 prior PYQs.
- Subject-wise coverage charts, year-wise contribution heatmaps, and exam distribution doughnuts.

### 3. 📖 Master Theory Guides (`books/`)
- [`books/POLITICAL_THEORY_MASTER_GUIDE.md`](books/POLITICAL_THEORY_MASTER_GUIDE.md): Self-contained, high-yield guide covering *Constitutionalism, Liberty & Law, State vs Government, Rule of Law, Separation of Powers, Rights vs Duties, and Marx vs Gandhi* with solved PYQs from CSE, CAPF, and CDS.

---

## 📂 Repository Structure

```
├── docs/                             # 🚀 GitHub Pages Web Portal (Deploy root)
│   ├── index.html                    # Single Page Application
│   ├── style.css                     # Premium Dark-Mode Glassmorphism Design
│   ├── app.js                        # Client-Side Application Logic & Router
│   ├── portal_data.js                # Embedded Microtheme & Question Database
│   └── data/
│       └── portal_data.json          # Formatted JSON dataset
│
├── portal/                           # Source files for the Study Portal (mirror of docs)
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── portal_data.js
│
├── dashboard/                        # CSE 2024 Microtheme Overlap Analyzer
│   ├── index.html                    # Visual Dashboard with Chart.js
│   ├── style.css
│   ├── app.js
│   ├── data.js
│   └── data/
│       ├── analysis_results.json     # Microtheme overlap scores & matching pairs
│       └── book_microthemes.json     # 179 parsed canonical microthemes
│
├── books/                            # Conceptual Study Guides & Source References
│   ├── POLITICAL_THEORY_MASTER_GUIDE.md # Comprehensive Political Theory Notes
│   └── UPSC Prelims_Microthemes (2009-25).pdf # 17-Year Microtheme Reference
│
├── PRELIMS/                          # UPSC CSE Raw Question Bank
│   ├── gs/                           # UPSC CSE General Studies (2011–2026)
│   └── csat/                         # UPSC CSE CSAT Paper-II (2013–2026)
│
├── output/                           # Processed & Merged Multi-Exam Datasets
│   ├── all_exams_prelims.csv         # Master merged dataset (6,215 questions)
│   ├── capf/                         # UPSC CAPF AC Paper-I GAI (2013–2024)
│   └── cds/                          # UPSC CDS GK Papers (2013–2025)
│
├── utils/                            # Python Automation & Processing Tools
│   ├── microtheme_analyzer.py        # Microtheme Matching & Scoring Engine
│   ├── book_microtheme_extractor.py  # PDF Microtheme Extractor
│   ├── build_portal_data.py          # Portal Database Compiler
│   ├── fetcher.py                    # Scraper HTTP fetcher
│   ├── parser.py                     # HTML & Question parser
│   └── exporter.py                   # CSV merger & directory organizer
│
├── main.py                           # CLI Pipeline Runner
└── .gitignore                        # Git ignore definitions
```

---

## 📊 Dataset Overview & Statistics

The repository unifies **6,215 questions** adhering to the 14-column SuperKalam standard schema:

```csv
Id,Year,Paper,Subject,Topics,Tags,Difficulty,Question,Option_A,Option_B,Option_C,Option_D,Correct_Answer,Explanation
```

### Breakdown by Examination:
| Exam | Paper Code | Years Covered | Questions |
| :--- | :--- | :--- | :--- |
| **UPSC CDS (Attempts I & II)** | `GK` | 2013–2025 | **3,120** |
| **UPSC CSE General Studies** | `GS` | 2011–2026 | **1,600** |
| **UPSC CAPF AC** | `GAI` | 2013–2024 | **1,495** |
| **Total Master Dataset** | | | **6,215** |

### Canonical Subject Distribution:
1. **Environment & Ecology** (283 questions &bull; 28 microthemes)
2. **Economics** (235 questions &bull; 24 microthemes)
3. **Polity & Governance** (216 questions &bull; 23 microthemes)
4. **Geography** (196 questions &bull; 21 microthemes)
5. **Science & Technology** (190 questions &bull; 18 microthemes)
6. **Arts & Culture** (154 questions &bull; 16 microthemes)
7. **Modern History** (134 questions &bull; 14 microthemes)
8. **International Relations** (125 questions &bull; 12 microthemes)
9. **Governance & Schemes** (112 questions &bull; 11 microthemes)
10. **Agriculture** (77 questions &bull; 8 microthemes)
11. **Misc & Sports** (38 questions &bull; 4 microthemes)

---

## 💻 Running the Portals Locally

### 1. Launch the Microtheme Study Portal
```bash
# Serve the portal on port 8899
python3 -m http.server 8899 --directory docs

# Open in browser: http://localhost:8899
```

### 2. Launch the CSE 2024 Overlap Analyzer
```bash
# Serve the analyzer dashboard on port 8765
python3 -m http.server 8765 --directory dashboard

# Open in browser: http://localhost:8765
```

### 3. Rebuilding / Updating the Database
To re-extract microthemes or re-compile the portal database:
```bash
# Extract book microthemes
python3 utils/book_microtheme_extractor.py

# Re-run microtheme analysis
python3 utils/microtheme_analyzer.py

# Re-compile portal database
python3 utils/build_portal_data.py
```

---

## 🚀 Deploying to GitHub Pages (1-Click)

The repository is structured with the [`docs/`](docs/) directory containing the complete zero-dependency web app.

1. **Push this repository to GitHub** (see instructions below).
2. On GitHub, navigate to **Repository Settings** &rarr; **Pages** (in the left sidebar).
3. Under **Build and deployment**:
   - **Source**: `Deploy from a branch`
   - **Branch**: `main` (or your default branch) &rarr; Folder: `/docs` &rarr; Click **Save**.
4. Your portal will be live at `https://<your-username>.github.io/<repo-name>/` in ~60 seconds!

---

## 📜 License & Acknowledgments
- Prepared for UPSC Civil Services Examination aspirants.
- Question papers & solutions compiled from UPSC CSE, CDS, and CAPF previous year official keys.
