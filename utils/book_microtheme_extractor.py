"""
UPSC Prelims Microtheme Extractor
Extracts all 179 canonical microthemes, 1,760 categorized questions (2009-2025),
and historical frequency distributions from 'UPSC Prelims_Microthemes (2009-25).pdf'.
"""

import pymupdf
import re
import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

TOC_SECTIONS = [
    (6, 'Polity'),
    (24, 'Economics'),
    (42, 'Geography'),
    (57, 'Agriculture'),
    (64, 'Modern History'),
    (75, 'Environment'),
    (96, 'International Relations'),
    (106, 'Governance'),
    (116, 'Arts & Culture'),
    (129, 'Science & Technology'),
    (144, 'Misc'),
]

def get_subject_for_page(page_1_indexed: int) -> str:
    current = 'Polity'
    for p, subj in TOC_SECTIONS:
        if page_1_indexed >= p:
            current = subj
        else:
            break
    return current

def clean_theme_title(raw_title: str) -> str:
    cleaned = re.sub(r'^\s*#\d+\.?\s*', '', raw_title).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned

def extract_all_from_pdf(pdf_path: str) -> dict:
    print(f"[PDF Extractor] Opening {pdf_path}...")
    doc = pymupdf.open(pdf_path)
    
    records = []
    microtheme_catalog = defaultdict(lambda: {
        "subject": "",
        "theme_name": "",
        "question_count": 0,
        "years": defaultdict(int),
        "questions": []
    })
    
    current_microtheme = "General"
    current_theme_id = 1
    
    for page_idx in range(len(doc)):
        page_num = page_idx + 1
        page_subj = get_subject_for_page(page_num)
        text = doc[page_idx].get_text('text')
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for microtheme header
            if line == '[Microtheme]' and i + 1 < len(lines):
                i += 1
                raw_theme = lines[i].strip()
                current_microtheme = clean_theme_title(raw_theme)
            elif re.match(r'^#\d+\.?\s+[A-Za-z]', line):
                current_microtheme = clean_theme_title(line)
            
            # Check for question header like '[2024]' or '1. [2024]'
            q_match = re.search(r'\[(20\d\d)\]\s*(.*)', line)
            if q_match:
                year = q_match.group(1)
                q_start = q_match.group(2)
                q_lines = [q_start]
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    if (re.search(r'\[(20\d\d)\]', next_line) or 
                        next_line == '[Microtheme]' or 
                        re.match(r'^#\d+\.?', next_line) or 
                        re.match(r'^\([a-d]\)', next_line) or 
                        next_line.startswith('Ans:')):
                        break
                    q_lines.append(next_line)
                    j += 1
                
                full_q_text = ' '.join(q_lines).strip()
                if len(full_q_text) > 8:
                    rec = {
                        'page': page_num,
                        'subject': page_subj,
                        'microtheme': current_microtheme,
                        'year': year,
                        'question_text': full_q_text
                    }
                    records.append(rec)
                    
                    # Update catalog
                    cat_key = f"{page_subj} :: {current_microtheme}"
                    microtheme_catalog[cat_key]["subject"] = page_subj
                    microtheme_catalog[cat_key]["theme_name"] = current_microtheme
                    microtheme_catalog[cat_key]["question_count"] += 1
                    microtheme_catalog[cat_key]["years"][year] += 1
                    microtheme_catalog[cat_key]["questions"].append({
                        "year": year,
                        "text": full_q_text
                    })
            i += 1
            
    print(f"[PDF Extractor] Successfully parsed {len(records)} total questions across {len(microtheme_catalog)} microthemes.")
    return {
        "records": records,
        "catalog": dict(microtheme_catalog)
    }

if __name__ == "__main__":
    pdf_file = "books/UPSC Prelims_Microthemes (2009-25).pdf"
    data = extract_all_from_pdf(pdf_file)
    with open("dashboard/data/book_microthemes.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Saved to dashboard/data/book_microthemes.json")
