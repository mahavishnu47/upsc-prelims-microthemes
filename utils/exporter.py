import os
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional

COLUMNS = [
    "Id", "Year", "Paper", "Subject", "Topics", "Tags", "Difficulty",
    "Question", "Option_A", "Option_B", "Option_C", "Option_D",
    "Correct_Answer", "Explanation"
]

def sort_key_for_csv(path: Path):
    name = path.stem
    # If CDS attempt I / II
    if "_I_" in name or name.endswith("_I"):
        return 1
    if "_II_" in name or name.endswith("_II"):
        return 2
    return 0

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """Normalizes dataframe columns to match exact SuperKalam schema."""
    # Handle ID vs Id
    if "ID" in df.columns and "Id" not in df.columns:
        df["Id"] = df["ID"]

    # Ensure all required columns exist
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""

    return df[COLUMNS]

class Exporter:
    def __init__(self, base_path: Optional[Path] = None, prelims_path: Optional[Path] = None):
        self.base_path = base_path or (Path(__file__).resolve().parent.parent / "output")
        self.prelims_path = prelims_path or (Path(__file__).resolve().parent.parent / "PRELIMS")
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._try_setup_root_output()

    def _try_setup_root_output(self):
        """Attempts to symlink or create /output if root write permission exists"""
        try:
            root_output = Path("/output")
            if not root_output.exists():
                os.symlink(str(self.base_path), "/output")
        except Exception:
            pass

    def save_year_csv(self, questions: List[Dict], exam: str, year: str, attempt: Optional[str] = None) -> Path:
        """
        Saves a list of question dicts into the specific year folder:
        - CAPF: output/capf/capf {year}/capf_{year}_GAI.csv
        - CDS:  output/cds/cds {year}/cds_{year}_{attempt}_GK.csv
        """
        if exam.lower() == "capf":
            folder = self.base_path / "capf" / f"capf {year}"
            filename = f"capf_{year}_GAI.csv"
        else:
            folder = self.base_path / "cds" / f"cds {year}"
            att = attempt if attempt else "I"
            filename = f"cds_{year}_{att}_GK.csv"

        folder.mkdir(parents=True, exist_ok=True)
        target_file = folder / filename

        df = pd.DataFrame(questions)
        df = normalize_df(df)

        # Save UTF-8 CSV
        df.to_csv(target_file, index=False, encoding="utf-8")
        print(f"[Exporter] Saved {target_file.relative_to(self.base_path.parent)} -> {len(df)} questions")
        return target_file

    def generate_merged_files(self):
        """
        Generates and updates:
        - output/capf/capf_all_years_GAI.csv
        - output/cds/cds_all_years_GK.csv
        - output/all_exams_prelims.csv (Contains CAPF + CDS + UPSC CSE GS from PRELIMS/gs)
        - output/folder_tree.txt
        """
        capf_dfs = []
        cds_dfs = []
        upsc_cse_dfs = []

        # 1. Collect all CAPF CSVs
        capf_dir = self.base_path / "capf"
        if capf_dir.exists():
            for y_dir in sorted(capf_dir.glob("capf *")):
                for csv_file in sorted(y_dir.glob("capf_*_GAI.csv")):
                    try:
                        df = pd.read_csv(csv_file, dtype=str)
                        df = normalize_df(df)
                        capf_dfs.append(df)
                    except Exception as e:
                        print(f"Error reading {csv_file}: {e}")

        if capf_dfs:
            capf_merged = pd.concat(capf_dfs, ignore_index=True)
            capf_merged = capf_merged[COLUMNS]
            capf_merged_path = capf_dir / "capf_all_years_GAI.csv"
            capf_merged.to_csv(capf_merged_path, index=False, encoding="utf-8")
            print(f"[Exporter] Updated merged CAPF CSV: {capf_merged_path} ({len(capf_merged)} questions)")

        # 2. Collect all CDS CSVs
        cds_dir = self.base_path / "cds"
        if cds_dir.exists():
            for y_dir in sorted(cds_dir.glob("cds *")):
                csv_files = sorted(y_dir.glob("cds_*_GK.csv"), key=sort_key_for_csv)
                for csv_file in csv_files:
                    try:
                        df = pd.read_csv(csv_file, dtype=str)
                        df = normalize_df(df)
                        cds_dfs.append(df)
                    except Exception as e:
                        print(f"Error reading {csv_file}: {e}")

        if cds_dfs:
            cds_merged = pd.concat(cds_dfs, ignore_index=True)
            cds_merged = cds_merged[COLUMNS]
            cds_merged_path = cds_dir / "cds_all_years_GK.csv"
            cds_merged.to_csv(cds_merged_path, index=False, encoding="utf-8")
            print(f"[Exporter] Updated merged CDS CSV: {cds_merged_path} ({len(cds_merged)} questions)")

        # 3. Collect all UPSC CSE GS CSVs from PRELIMS/gs (and PRELIMS root)
        if self.prelims_path.exists():
            # Search both PRELIMS/gs/*.csv and PRELIMS/*GS*.csv
            gs_files = sorted(list(self.prelims_path.glob("gs/*.csv")) + list(self.prelims_path.glob("*GS*.csv")))
            # De-duplicate files
            seen_files = set()
            for f in gs_files:
                if f.resolve() in seen_files:
                    continue
                seen_files.add(f.resolve())
                try:
                    df = pd.read_csv(f, dtype=str)
                    df = normalize_df(df)
                    upsc_cse_dfs.append(df)
                except Exception as e:
                    print(f"Error reading {f}: {e}")

        if upsc_cse_dfs:
            print(f"[Exporter] Loaded {len(upsc_cse_dfs)} UPSC CSE GS files ({sum(len(d) for d in upsc_cse_dfs)} questions) from PRELIMS")

        # 4. Collect everything into all_exams_prelims.csv
        all_dfs = capf_dfs + cds_dfs + upsc_cse_dfs
        if all_dfs:
            all_merged = pd.concat(all_dfs, ignore_index=True)
            all_merged = all_merged[COLUMNS]
            all_merged_path = self.base_path / "all_exams_prelims.csv"
            all_merged.to_csv(all_merged_path, index=False, encoding="utf-8")
            print(f"[Exporter] Updated overall merged CSV: {all_merged_path} ({len(all_merged)} questions)")

        # 5. Generate folder_tree.txt
        self.generate_folder_tree(upsc_cse_count=sum(len(d) for d in upsc_cse_dfs))

    def generate_folder_tree(self, upsc_cse_count: int = 0):
        """Generates a clean text representation of the folder tree with question counts."""
        tree_lines = ["/output/"]
        
        # CAPF
        capf_dir = self.base_path / "capf"
        if capf_dir.exists():
            tree_lines.append("  /capf/")
            for y_dir in sorted(capf_dir.glob("capf *")):
                if y_dir.is_dir():
                    tree_lines.append(f"    /{y_dir.name}/")
                    for f in sorted(y_dir.glob("*.csv")):
                        try:
                            df = pd.read_csv(f, dtype=str)
                            tree_lines.append(f"      {f.name}  ({len(df)} rows)")
                        except Exception:
                            tree_lines.append(f"      {f.name}")
            # Merged CAPF
            merged_capf = capf_dir / "capf_all_years_GAI.csv"
            if merged_capf.exists():
                try:
                    df = pd.read_csv(merged_capf, dtype=str)
                    tree_lines.append(f"    capf_all_years_GAI.csv  ({len(df)} rows, merged)")
                except Exception:
                    tree_lines.append("    capf_all_years_GAI.csv  (merged)")

        # CDS
        cds_dir = self.base_path / "cds"
        if cds_dir.exists():
            tree_lines.append("  /cds/")
            for y_dir in sorted(cds_dir.glob("cds *")):
                if y_dir.is_dir():
                    tree_lines.append(f"    /{y_dir.name}/")
                    for f in sorted(y_dir.glob("*.csv"), key=sort_key_for_csv):
                        try:
                            df = pd.read_csv(f, dtype=str)
                            tree_lines.append(f"      {f.name}  ({len(df)} rows)")
                        except Exception:
                            tree_lines.append(f"      {f.name}")
            # Merged CDS
            merged_cds = cds_dir / "cds_all_years_GK.csv"
            if merged_cds.exists():
                try:
                    df = pd.read_csv(merged_cds, dtype=str)
                    tree_lines.append(f"    cds_all_years_GK.csv  ({len(df)} rows, merged)")
                except Exception:
                    tree_lines.append("    cds_all_years_GK.csv  (merged)")

        # Global merged
        all_merged = self.base_path / "all_exams_prelims.csv"
        if all_merged.exists():
            try:
                df = pd.read_csv(all_merged, dtype=str)
                extra_note = f" [Includes {upsc_cse_count} UPSC CSE GS rows from PRELIMS/gs]" if upsc_cse_count > 0 else ""
                tree_lines.append(f"  all_exams_prelims.csv  ({len(df)} rows, merged){extra_note}")
            except Exception:
                pass

        tree_content = "\n".join(tree_lines) + "\n"
        tree_file = self.base_path / "folder_tree.txt"
        tree_file.write_text(tree_content, encoding="utf-8")
        print(f"[Exporter] Generated folder tree at {tree_file}")
