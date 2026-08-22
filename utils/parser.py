import json
import re
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from utils.fetcher import Fetcher

BASE_URL = "https://www.examsnet.com"

class Parser:
    def __init__(self, fetcher: Optional[Fetcher] = None):
        self.fetcher = fetcher or Fetcher()

    def discover_capf_papers(self) -> List[Dict]:
        """
        Discovers all CAPF GAI papers from examsnet.
        Returns list of dicts: [{'year': '2023', 'paper': 'GAI', 'url': '...', 'title': '...'}]
        """
        index_url = f"{BASE_URL}/exams/upsc-capf-ac-previous-question-papers-online"
        html = self.fetcher.get(index_url)
        soup = BeautifulSoup(html, "html.parser")

        papers = []
        seen_urls = set()

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            text = a.get_text(separator=" ", strip=True)
            if "/test/" in href and "capf" in href.lower():
                # Avoid model papers unless real papers
                if "model" in href.lower() or "model" in text.lower():
                    continue

                full_url = f"{BASE_URL}{href}" if href.startswith("/") else href
                if full_url in seen_urls:
                    continue

                year_match = re.search(r"20\d{2}", href + " " + text)
                if year_match:
                    year = year_match.group(0)
                    papers.append({
                        "exam": "capf",
                        "year": year,
                        "paper": "GAI",
                        "attempt": None,
                        "url": full_url,
                        "title": text or f"UPSC CAPF {year} Paper"
                    })
                    seen_urls.add(full_url)

        # Sort chronologically
        papers.sort(key=lambda x: int(x["year"]))
        return papers

    def discover_cds_papers(self) -> List[Dict]:
        """
        Discovers all CDS General Knowledge (GK) papers from examsnet.
        Returns list of dicts: [{'year': '2023', 'paper': 'GK', 'attempt': 'I', 'url': '...', 'title': '...'}]
        """
        index_urls = [
            f"{BASE_URL}/exams/upsc-cds-previous-question-papers-online",
            f"{BASE_URL}/exams/upsc-cds-previous-year-solved-papers"
        ]

        papers = []
        seen_urls = set()

        for index_url in index_urls:
            html = self.fetcher.get(index_url)
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")

            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                text = a.get_text(separator=" ", strip=True)

                # Filter only GK / General Knowledge papers for CDS
                if "/test/" in href and "cds" in href.lower() and ("gk" in href.lower() or "gk" in text.lower() or "knowledge" in text.lower()):
                    full_url = f"{BASE_URL}{href}" if href.startswith("/") else href
                    if full_url in seen_urls:
                        continue

                    # Extract Year
                    year_match = re.search(r"20\d{2}", href + " " + text)
                    if not year_match:
                        continue
                    year = year_match.group(0)

                    # Extract Attempt (I or II)
                    attempt = self._extract_attempt(href, text)
                    if not attempt:
                        continue

                    papers.append({
                        "exam": "cds",
                        "year": year,
                        "paper": "GK",
                        "attempt": attempt,
                        "url": full_url,
                        "title": text or f"UPSC CDS {attempt} {year} GK Paper"
                    })
                    seen_urls.add(full_url)

        # Sort chronologically by year and attempt
        papers.sort(key=lambda x: (int(x["year"]), 1 if x["attempt"] == "I" else 2))
        return papers

    def _extract_attempt(self, href: str, text: str) -> Optional[str]:
        combined = (href + " " + text).lower()
        if re.search(r"cds[-_\s]*(?:ii|2|two)\b", combined) or re.search(r"\b(?:ii|2)\b[-_\s]*cds", combined) or "-cds-2-" in combined or "-cds-ii-" in combined or "cds 2" in combined or "cds ii" in combined:
            return "II"
        if re.search(r"cds[-_\s]*(?:i|1|one)\b", combined) or re.search(r"\b(?:i|1)\b[-_\s]*cds", combined) or "-cds-1-" in combined or "-cds-i-" in combined or "cds 1" in combined or "cds i" in combined:
            return "I"
        return None

    def get_total_questions(self, paper_url: str) -> int:
        """Determines total questions in paper by fetching question 1"""
        html = self.fetcher.get(f"{paper_url}/1" if not paper_url.endswith("/1") else paper_url)
        if not html:
            html = self.fetcher.get(paper_url)
        if not html:
            return 0

        # Pattern: Question : 1 of 120 or Question: 1 of 125
        match = re.search(r"Question\s*:\s*\d+\s+of\s+(\d+)", html, re.I)
        if match:
            return int(match.group(1))

        # Fallback: check schema.org
        return 120

    def parse_question_page(self, html: str, qnum: int, exam_info: Dict) -> Optional[Dict]:
        """
        Parses a single question HTML page into structured dictionary.
        """
        if not html or len(html) < 200:
            return None

        soup = BeautifulSoup(html, "html.parser")
        qdiv = soup.find(id="questiondiv")
        if not qdiv:
            return None

        # 1. Extract Question Text
        question_text = ""
        mquestion = qdiv.find(id="mquestion")
        if mquestion:
            # Remove watermark spans if present
            for w in mquestion.find_all(class_=re.compile(r"watermark", re.I)):
                w.decompose()
            question_text = mquestion.get_text(separator=" ", strip=True)
            # Remove leading question link artifacts
            question_text = re.sub(r"^©\s*examsnet\.com\s*", "", question_text)
            question_text = re.sub(r"\s+", " ", question_text).strip()

        # Fallback to Schema.org for Question Text
        schema_data = self._extract_schema_json(soup)
        if not question_text and schema_data:
            question_text = schema_data.get("question_text", "")

        if not question_text:
            return None

        # 2. Extract Options
        options = ["", "", "", ""]
        answers_ul = qdiv.find(id="answers")
        if answers_ul:
            items = answers_ul.find_all("li")
            for idx, li in enumerate(items[:4]):
                # Remove radio input text / values
                for inp in li.find_all("input"):
                    inp.decompose()
                opt_text = li.get_text(separator=" ", strip=True)
                opt_text = re.sub(r"\s+", " ", opt_text).strip()
                options[idx] = opt_text

        # Schema fallback for options
        if schema_data and schema_data.get("options") and (not options[0] or not options[1]):
            schema_opts = schema_data.get("options", [])
            for i in range(min(4, len(schema_opts))):
                if not options[i]:
                    options[i] = schema_opts[i]

        # 3. Extract Correct Answer
        correct_ans = ""
        # Pattern in script: var c = ["3"] or var c = ['0']
        c_match = re.search(r'var\s+c\s*=\s*\[\s*["\']?(\d+)["\']?\s*\]', html)
        if c_match:
            c_idx = int(c_match.group(1))
            if 0 <= c_idx <= 3:
                correct_ans = chr(ord("A") + c_idx)

        # Fallback from Schema.org acceptedAnswer
        if not correct_ans and schema_data and schema_data.get("accepted_answer"):
            accepted = schema_data.get("accepted_answer", "").strip()
            # Check if accepted matches option text
            for idx, opt in enumerate(options):
                if opt and (opt.lower() == accepted.lower() or opt.lower() in accepted.lower()):
                    correct_ans = chr(ord("A") + idx)
                    break

        if not correct_ans:
            correct_ans = "A" # Default fallback

        # 4. Extract Explanation
        explanation = ""
        ans_status = soup.find(id="answerstatus") or soup.find(class_=re.compile(r"explanation|solution", re.I))
        if ans_status:
            exp_text = ans_status.get_text(separator=" ", strip=True)
            if len(exp_text) > 15:
                explanation = exp_text

        # Generate ID format: CAPF-2023-GAI-001 or CDS-2023-I-GK-001
        exam = exam_info["exam"].upper()
        year = exam_info["year"]
        paper = exam_info["paper"].upper()
        attempt = f"-{exam_info['attempt']}" if exam_info.get("attempt") else ""
        qid = f"{exam}-{year}{attempt}-{paper}-{qnum:03d}"

        return {
            "Id": qid,
            "Year": year,
            "Paper": paper,
            "Subject": "",
            "Topics": "",
            "Tags": "",
            "Difficulty": "medium",
            "Question": question_text,
            "Option_A": options[0],
            "Option_B": options[1],
            "Option_C": options[2],
            "Option_D": options[3],
            "Correct_Answer": correct_ans,
            "Explanation": explanation,
        }

    def _extract_schema_json(self, soup: BeautifulSoup) -> Dict:
        result = {"question_text": "", "options": [], "accepted_answer": ""}
        for s in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(s.string or s.text or "{}")
                # Handle learning resource
                if data.get("@type") == "LearningResource" and "hasPart" in data:
                    part = data["hasPart"][0]
                    result["question_text"] = part.get("text") or part.get("name") or ""
                    if "suggestedAnswer" in part:
                        sorted_answers = sorted(part["suggestedAnswer"], key=lambda x: x.get("position", 0))
                        result["options"] = [a.get("text", "") for a in sorted_answers]
                # Handle QAPage
                elif data.get("@type") == "QAPage" and "mainEntity" in data:
                    entity = data["mainEntity"]
                    result["question_text"] = entity.get("text") or entity.get("name") or ""
                    if "acceptedAnswer" in entity:
                        ans_text = entity["acceptedAnswer"].get("text", "")
                        # e.g. "Correct Answer is : Sister"
                        ans_text = re.sub(r"^Correct\s+Answer\s+is\s*:\s*", "", ans_text, flags=re.I).strip()
                        result["accepted_answer"] = ans_text
            except Exception:
                continue
        return result
