"""
Portal Data Compiler
Builds a complete, indexed JSON & JavaScript database for the Microtheme Study Portal.
Maps all 183 canonical microthemes from the book with all matching questions from CSE (2009-2026),
CAPF (2013-2024), and CDS (2013-2025) with full options, answers, explanations, and frequency stats.
"""

import json
import re
import pandas as pd
from pathlib import Path
from collections import defaultdict

SUBJECT_ORDER = [
    "Polity",
    "Economics",
    "Geography",
    "Environment",
    "Science & Technology",
    "Modern History",
    "Arts & Culture",
    "International Relations",
    "Governance",
    "Agriculture",
    "Misc"
]

SUBJECT_ICONS = {
    "Polity": "🏛️",
    "Economics": "📈",
    "Geography": "🌍",
    "Environment": "🌿",
    "Science & Technology": "🔬",
    "Modern History": "📜",
    "Arts & Culture": "🎭",
    "International Relations": "🌐",
    "Governance": "⚖️",
    "Agriculture": "🌾",
    "Misc": "🧩"
}

SUBJECT_COLORS = {
    "Polity": "#34d399",
    "Economics": "#fbbf24",
    "Geography": "#22d3ee",
    "Environment": "#4ade80",
    "Science & Technology": "#f472b6",
    "Modern History": "#fb923c",
    "Arts & Culture": "#a78bfa",
    "International Relations": "#60a5fa",
    "Governance": "#818cf8",
    "Agriculture": "#a3e635",
    "Misc": "#94a3b8"
}

def clean_theme_title(raw_title: str) -> str:
    cleaned = re.sub(r'^\s*#\d+\.?\s*', '', raw_title).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned

def extract_keywords(text: str) -> set:
    if not text or pd.isna(text):
        return set()
    cleaned = re.sub(r'[^a-zA-Z\s]', ' ', str(text).lower())
    words = set(w for w in cleaned.split() if len(w) >= 4)
    stop = {'which', 'following', 'statement', 'statements', 'correct', 'incorrect', 'consider', 'respect', 'regard', 'given', 'below', 'india', 'state', 'among', 'answer', 'select', 'using', 'code'}
    return words - stop

def build_portal_data():
    print("[Portal Builder] Loading book microthemes and master CSV...")
    with open('dashboard/data/book_microthemes.json', 'r', encoding='utf-8') as f:
        book_data = json.load(f)
    
    df_all = pd.read_csv('output/all_exams_prelims.csv', dtype=str)
    
    # 1. Structure all microthemes by Subject
    subjects_dict = defaultdict(lambda: {
        "subject_name": "",
        "icon": "",
        "color": "",
        "total_questions": 0,
        "microthemes": []
    })
    
    # Pre-index CSV questions by keyword & text snippet for fast matching
    csv_records = []
    for idx, row in df_all.iterrows():
        q_text = str(row.get('Question', ''))
        csv_records.append({
            "id": str(row.get('Id', '')),
            "year": str(row.get('Year', '')),
            "paper": str(row.get('Paper', '')),
            "subject": str(row.get('Subject', '')),
            "topics": str(row.get('Topics', '')) if pd.notna(row.get('Topics')) else '',
            "tags": str(row.get('Tags', '')) if pd.notna(row.get('Tags')) else '',
            "question": q_text,
            "option_a": str(row.get('Option_A', '')) if pd.notna(row.get('Option_A')) else '',
            "option_b": str(row.get('Option_B', '')) if pd.notna(row.get('Option_B')) else '',
            "option_c": str(row.get('Option_C', '')) if pd.notna(row.get('Option_C')) else '',
            "option_d": str(row.get('Option_D', '')) if pd.notna(row.get('Option_D')) else '',
            "correct_answer": str(row.get('Correct_Answer', '')) if pd.notna(row.get('Correct_Answer')) else '',
            "explanation": str(row.get('Explanation', '')) if pd.notna(row.get('Explanation')) else '',
            "keywords": extract_keywords(q_text) | extract_keywords(row.get('Tags', '')) | extract_keywords(row.get('Topics', ''))
        })
    
    cse_csv_records = [r for r in csv_records if r['paper'] == 'GS']
    other_csv_records = [r for r in csv_records if r['paper'] in ['GK', 'GAI']]
    
    # Build Microthemes catalog
    theme_id_counter = 1
    all_microthemes_flat = []
    
    for cat_key, cat_val in book_data['catalog'].items():
        subj = cat_val['subject']
        theme_name = clean_theme_title(cat_val['theme_name'])
        
        if not theme_name or theme_name == "General":
            continue
            
        theme_kws = extract_keywords(theme_name)
        
        # 1. Gather all Book CSE questions for this theme
        theme_questions = []
        matched_csv_ids = set()
        
        for bq in cat_val.get('questions', []):
            b_year = str(bq.get('year', ''))
            b_text = str(bq.get('text', ''))
            b_kws = extract_keywords(b_text)
            
            # Find best match in CSV
            best_r = None
            best_overlap = 0
            for r in cse_csv_records:
                if r['year'] == b_year:
                    overlap = len(b_kws & r['keywords'])
                    if overlap > best_overlap:
                        best_overlap = overlap
                        best_r = r
            
            if best_r and best_overlap >= 2:
                matched_csv_ids.add(best_r['id'])
                theme_questions.append({
                    "id": best_r['id'],
                    "year": best_r['year'],
                    "exam": "UPSC CSE GS",
                    "paper": "GS",
                    "question": best_r['question'],
                    "option_a": best_r['option_a'],
                    "option_b": best_r['option_b'],
                    "option_c": best_r['option_c'],
                    "option_d": best_r['option_d'],
                    "correct_answer": best_r['correct_answer'],
                    "explanation": best_r['explanation'],
                    "tags": best_r['tags'],
                    "source": "book_direct"
                })
            else:
                # Fallback to book text
                theme_questions.append({
                    "id": f"book-{b_year}-{len(theme_questions)+1}",
                    "year": b_year,
                    "exam": "UPSC CSE GS",
                    "paper": "GS",
                    "question": b_text,
                    "option_a": "",
                    "option_b": "",
                    "option_c": "",
                    "option_d": "",
                    "correct_answer": "",
                    "explanation": "",
                    "tags": theme_name,
                    "source": "book_text"
                })
        
        # 2. Match related CDS & CAPF questions testing this microtheme
        cross_exam_questions = []
        if len(theme_kws) >= 1:
            for r in other_csv_records:
                overlap = len(theme_kws & r['keywords'])
                if overlap >= 2:
                    exam_label = "UPSC CDS GK" if r['paper'] == 'GK' else "UPSC CAPF GAI"
                    cross_exam_questions.append({
                        "id": r['id'],
                        "year": r['year'],
                        "exam": exam_label,
                        "paper": r['paper'],
                        "question": r['question'],
                        "option_a": r['option_a'],
                        "option_b": r['option_b'],
                        "option_c": r['option_c'],
                        "option_d": r['option_d'],
                        "correct_answer": r['correct_answer'],
                        "explanation": r['explanation'],
                        "tags": r['tags'],
                        "source": "cross_exam_match"
                    })
        
        # Sort questions by year descending
        theme_questions.sort(key=lambda x: int(x['year']) if x['year'].isdigit() else 0, reverse=True)
        cross_exam_questions.sort(key=lambda x: int(x['year']) if x['year'].isdigit() else 0, reverse=True)
        
        # Calculate frequency statistics
        years_list = [q['year'] for q in theme_questions if q['year'].isdigit()]
        year_counts = defaultdict(int)
        for y in years_list:
            year_counts[y] += 1
            
        recent_count = sum(c for y, c in year_counts.items() if int(y) >= 2018)
        total_cse_count = len(theme_questions)
        total_all_count = total_cse_count + len(cross_exam_questions)
        
        # Determine Yield Status
        if total_cse_count >= 10 or recent_count >= 4:
            yield_badge = "🔥 High Yield (Core Repeat)"
            yield_class = "yield-high"
        elif total_cse_count >= 5 or recent_count >= 2:
            yield_badge = "⭐ Medium Yield (Regular)"
            yield_class = "yield-medium"
        else:
            yield_badge = "📌 Standard Microtheme"
            yield_class = "yield-standard"
            
        theme_obj = {
            "id": f"mt-{theme_id_counter:03d}",
            "subject": subj,
            "theme_name": theme_name,
            "total_cse_questions": total_cse_count,
            "total_cross_exam_questions": len(cross_exam_questions),
            "total_all_questions": total_all_count,
            "recent_count_last_7_yrs": recent_count,
            "yield_badge": yield_badge,
            "yield_class": yield_class,
            "years_appeared": sorted(list(set(years_list)), reverse=True),
            "year_distribution": dict(year_counts),
            "cse_questions": theme_questions,
            "cross_exam_questions": cross_exam_questions[:15],  # top 15 cross exam
        }
        
        theme_id_counter += 1
        all_microthemes_flat.append(theme_obj)
        subjects_dict[subj]["microthemes"].append(theme_obj)
        subjects_dict[subj]["total_questions"] += total_cse_count
        subjects_dict[subj]["subject_name"] = subj
        subjects_dict[subj]["icon"] = SUBJECT_ICONS.get(subj, "📚")
        subjects_dict[subj]["color"] = SUBJECT_COLORS.get(subj, "#6366f1")

    # Order subjects
    ordered_subjects = []
    for sname in SUBJECT_ORDER:
        if sname in subjects_dict:
            s_data = subjects_dict[sname]
            # Sort microthemes by total questions descending
            s_data["microthemes"].sort(key=lambda x: x['total_cse_questions'], reverse=True)
            ordered_subjects.append(s_data)
            
    # Also add any remaining subjects
    for sname, s_data in subjects_dict.items():
        if sname not in SUBJECT_ORDER:
            s_data["microthemes"].sort(key=lambda x: x['total_cse_questions'], reverse=True)
            ordered_subjects.append(s_data)
            
    # Sort all microthemes flat by frequency
    all_microthemes_flat.sort(key=lambda x: x['total_cse_questions'], reverse=True)
    
    # Read Political Theory Master Guide text for the built-in concept reader
    theory_guide_content = ""
    guide_path = Path("books/POLITICAL_THEORY_MASTER_GUIDE.md")
    if guide_path.exists():
        theory_guide_content = guide_path.read_text(encoding="utf-8")
        
    portal_database = {
        "metadata": {
            "title": "UPSC Prelims Microtheme Master Study Portal",
            "version": "2.0",
            "total_microthemes": len(all_microthemes_flat),
            "total_subjects": len(ordered_subjects),
            "total_cse_questions_cataloged": sum(m['total_cse_questions'] for m in all_microthemes_flat),
            "total_cross_exam_questions": sum(m['total_cross_exam_questions'] for m in all_microthemes_flat),
            "exam_years_covered": "2009–2026 (CSE) & 2013–2025 (CDS/CAPF)",
            "sources": "UPSC CSE Prelims, UPSC CDS GK, UPSC CAPF AC Paper-I"
        },
        "subjects": ordered_subjects,
        "microthemes": all_microthemes_flat,
        "theory_guides": {
            "political_theory": theory_guide_content
        }
    }
    
    # Save to portal/ and docs/
    for dest_dir in ["portal", "docs"]:
        p = Path(dest_dir) / "data"
        p.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        json_file = p / "portal_data.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(portal_database, f, indent=2, ensure_ascii=False)
            
        # Save inline JS
        js_file = Path(dest_dir) / "portal_data.js"
        with open(js_file, "w", encoding="utf-8") as f:
            f.write(f"const PORTAL_DATA = {json.dumps(portal_database, ensure_ascii=False)};")
            
        print(f"[Portal Builder] Saved portal data to {json_file} and {js_file}")
        
    print(f"[Portal Builder] Done! Compiled {len(all_microthemes_flat)} canonical microthemes across {len(ordered_subjects)} subjects.")

if __name__ == "__main__":
    build_portal_data()
