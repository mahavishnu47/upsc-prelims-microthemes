import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict

from utils.fetcher import Fetcher
from utils.parser import Parser
from utils.enricher import Enricher
from utils.exporter import Exporter

def scrape_single_paper(paper_info: Dict, fetcher: Fetcher, parser: Parser, enricher: Enricher, exporter: Exporter, concurrency: int = 8) -> int:
    exam = paper_info["exam"]
    year = paper_info["year"]
    attempt = paper_info.get("attempt")
    paper_type = paper_info["paper"]
    paper_url = paper_info["url"]
    label = f"{exam.upper()} {year}" + (f" ({attempt})" if attempt else "")

    print(f"\n==========================================")
    print(f"[*] Processing: {label} [{paper_type}]")
    print(f"[*] URL: {paper_url}")

    # Determine total question count
    total_q = parser.get_total_questions(paper_url)
    if total_q == 0:
        total_q = 125 if exam == "capf" else 120
    print(f"[*] Total Questions: {total_q}")

    questions = [None] * total_q

    def fetch_and_parse(qnum: int):
        q_url = f"{paper_url}/{qnum}"
        html = fetcher.get(q_url)
        q_dict = parser.parse_question_page(html, qnum, paper_info)
        if q_dict:
            q_dict = enricher.enrich_question(q_dict)
            return qnum, q_dict
        return qnum, None

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {executor.submit(fetch_and_parse, i): i for i in range(1, total_q + 1)}
        for future in as_completed(futures):
            qnum, q_dict = future.result()
            if q_dict:
                questions[qnum - 1] = q_dict

    valid_questions = [q for q in questions if q is not None]

    if not valid_questions:
        print(f"[!] Warning: No questions parsed for {label}")
        return 0

    # Save to disk
    exporter.save_year_csv(valid_questions, exam=exam, year=year, attempt=attempt)
    return len(valid_questions)

def main():
    parser_cli = argparse.ArgumentParser(description="Examsnet UPSC CAPF & CDS Prelims Scraper")
    parser_cli.add_argument("--structure", default="folder_per_year", choices=["folder_per_year"], help="Folder structure")
    parser_cli.add_argument("--schema", default="superkalam", choices=["superkalam"], help="Output CSV schema")
    parser_cli.add_argument("--exam", default="all", choices=["all", "capf", "cds"], help="Filter by exam")
    parser_cli.add_argument("--year", default=None, help="Filter by specific year (e.g. 2023)")
    parser_cli.add_argument("--concurrency", type=int, default=8, help="Concurrent workers for question fetching")
    parser_cli.add_argument("--delay", type=float, default=0.05, help="Request delay in seconds")

    args = parser_cli.parse_args()

    print(f"==================================================")
    print(f"  Examsnet UPSC Prelims Scraper")
    print(f"  Structure: {args.structure} | Schema: {args.schema}")
    print(f"  Target Exams: {args.exam.upper()} | Filter Year: {args.year or 'ALL'}")
    print(f"==================================================")

    fetcher = Fetcher(use_cache=True, delay=args.delay)
    parser = Parser(fetcher)
    enricher = Enricher()
    exporter = Exporter()

    papers_to_scrape = []

    if args.exam in ["all", "capf"]:
        print("[*] Discovering CAPF (GAI) Papers...")
        capf_papers = parser.discover_capf_papers()
        print(f"    Found {len(capf_papers)} CAPF papers ({', '.join(p['year'] for p in capf_papers)})")
        papers_to_scrape.extend(capf_papers)

    if args.exam in ["all", "cds"]:
        print("[*] Discovering CDS (GK) Papers...")
        cds_papers = parser.discover_cds_papers()
        print(f"    Found {len(cds_papers)} CDS GK papers")
        papers_to_scrape.extend(cds_papers)

    if args.year:
        papers_to_scrape = [p for p in papers_to_scrape if p["year"] == str(args.year)]

    total_scraped = 0
    for paper in papers_to_scrape:
        count = scrape_single_paper(paper, fetcher, parser, enricher, exporter, concurrency=args.concurrency)
        total_scraped += count

    print(f"\n==================================================")
    print(f"[*] Generating merged CSVs and folder tree...")
    exporter.generate_merged_files()
    print(f"[*] Finished scraping! Total questions processed: {total_scraped}")
    print(f"==================================================")

if __name__ == "__main__":
    main()
