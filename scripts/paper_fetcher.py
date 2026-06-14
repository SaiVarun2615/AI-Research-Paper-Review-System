## scripts/paper_fetcher.py

import json
import time
import os
from pathlib import Path

try:
    import requests
except ModuleNotFoundError:
    raise RuntimeError(
        "❌ 'requests' is not installed in the active Python environment.\n"
        "Run:\n"
        "  .\\.venv\\Scripts\\python.exe -m pip install requests"
    )

from dotenv import load_dotenv

# =========================
# PATH SETUP
# =========================
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent

QUERIES_FILE = ROOT_DIR / "queries.txt"
RESEARCH_DIR = ROOT_DIR / "research"
PDF_DIR = RESEARCH_DIR / "pdfs"
OUTPUT_FILE = RESEARCH_DIR / "papers.json"

RESEARCH_DIR.mkdir(exist_ok=True)
PDF_DIR.mkdir(exist_ok=True)

# =========================
# LOAD ENV + API KEY
# =========================
load_dotenv(ROOT_DIR / ".env")

API_KEY = os.getenv("S2_API_KEY")
if not API_KEY:
    raise RuntimeError("❌ S2_API_KEY not found in .env")

HEADERS = {"x-api-key": API_KEY}

# =========================
# API CONFIG
# =========================
BASE_URL = "https://api.semanticscholar.org/graph/v1"
SEARCH_ENDPOINT = f"{BASE_URL}/paper/search/bulk"

FIELDS = "paperId,title,url,year,openAccessPdf,authors"
PAPERS_PER_QUERY = 10
RATE_LIMIT_DELAY = 1.2

# =========================
# FETCH PAPERS
# =========================
def fetch_papers(query: str) -> list[dict]:
    results = []
    token = None

    params = {
        "query": query,
        "fields": FIELDS,
        "year": "2023-"
    }

    while True:
        if token:
            params["token"] = token

        response = requests.get(
            SEARCH_ENDPOINT,
            headers=HEADERS,
            params=params,
            timeout=60
        )

        if response.status_code == 429:
            time.sleep(2)
            continue

        response.raise_for_status()
        payload = response.json()

        results.extend(payload.get("data", []))

        if len(results) >= PAPERS_PER_QUERY:
            break

        token = payload.get("token")
        if not token:
            break

        time.sleep(RATE_LIMIT_DELAY)

    return results[:PAPERS_PER_QUERY]

# =========================
# DOWNLOAD PDF
# =========================
def download_pdf(url: str, save_path: Path) -> bool:
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        save_path.write_bytes(r.content)
        return True
    except Exception:
        return False

# =========================
# CORE PIPELINE FUNCTION
# =========================
def fetch_from_queries(queries_text: str = None) -> str:
    if queries_text:
        queries = [q.strip() for q in queries_text.splitlines() if q.strip()]
        QUERIES_FILE.write_text("\n".join(queries) + "\n", encoding="utf-8")
    else:
        if not QUERIES_FILE.exists():
            raise RuntimeError("queries.txt not found")
        queries = [q.strip() for q in QUERIES_FILE.read_text().splitlines() if q.strip()]

    if not queries:
        raise RuntimeError("No queries provided")

    all_data = {}

    for query in queries:
        print(f"🔍 Fetching papers for: {query}")
        papers = fetch_papers(query)

        query_folder = PDF_DIR / query.replace(" ", "_")
        query_folder.mkdir(parents=True, exist_ok=True)

        for idx, paper in enumerate(papers, start=1):
            pdf_info = paper.get("openAccessPdf")
            if not pdf_info or not pdf_info.get("url"):
                continue

            pdf_path = query_folder / f"paper_{idx}.pdf"
            if download_pdf(pdf_info["url"], pdf_path):
                paper["local_pdf_path"] = str(pdf_path)

        all_data[query] = papers
        print(f"✅ {len(papers)} papers processed\n")
        time.sleep(RATE_LIMIT_DELAY)

    OUTPUT_FILE.write_text(
        json.dumps(all_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return "Papers fetched and papers.json updated successfully"

# =========================
# CLI ENTRY POINT
# =========================
if __name__ == "__main__":
    msg = fetch_from_queries()
    print(f"\n🎉 {msg}")









# # scripts/list.py

# import json
# import time
# import os
# from pathlib import Path
# import requests

# # =========================
# # PATH CONFIGURATION
# # =========================
# SCRIPT_DIR = Path(__file__).resolve().parent
# ROOT_DIR = SCRIPT_DIR.parent

# QUERIES_FILE = ROOT_DIR / "queries.txt"
# OUTPUT_FILE = ROOT_DIR / "research" / "papers.json"

# # =========================
# # API CONFIGURATION
# # =========================
# BASE_URL = "https://api.semanticscholar.org/graph/v1"
# SEARCH_ENDPOINT = f"{BASE_URL}/paper/search/bulk"

# FIELDS = (
#     "paperId,title,url,year,publicationDate,"
#     "publicationTypes,openAccessPdf,authors"
# )

# PAPERS_PER_QUERY = 40
# RATE_LIMIT_DELAY = 1.1  # seconds

# # =========================
# # LOAD API KEY
# # =========================
# def load_api_key() -> str:
#     env_path = ROOT_DIR / ".env"

#     if env_path.exists():
#         for line in env_path.read_text(encoding="utf-8").splitlines():
#             if line.startswith("S2_API_KEY="):
#                 return line.split("=", 1)[1].strip()

#     key = os.getenv("S2_API_KEY")
#     if key:
#         return key

#     raise RuntimeError("S2_API_KEY not found")

# API_KEY = load_api_key()
# HEADERS = {"x-api-key": API_KEY}

# # =========================
# # LOAD SEARCH QUERIES
# # =========================
# def load_queries(path: Path) -> list[str]:
#     if not path.exists():
#         raise FileNotFoundError("queries.txt not found")

#     return [
#         line.strip()
#         for line in path.read_text(encoding="utf-8").splitlines()
#         if line.strip()
#     ]

# # =========================
# # FETCH PAPERS FROM API
# # =========================
# def fetch_papers(query: str, year_filter: str | None = "2023-") -> list[dict]:
#     results = []
#     token = None

#     params = {
#         "query": query,
#         "fields": FIELDS,
#     }

#     if year_filter:
#         params["year"] = year_filter

#     while True:
#         if token:
#             params["token"] = token

#         response = requests.get(
#             SEARCH_ENDPOINT,
#             headers=HEADERS,
#             params=params,
#             timeout=60
#         )

#         if response.status_code == 429:
#             time.sleep(1.5)
#             continue

#         response.raise_for_status()
#         payload = response.json()

#         results.extend(payload.get("data", []))

#         if len(results) >= PAPERS_PER_QUERY:
#             break

#         token = payload.get("token")
#         if not token:
#             break

#         time.sleep(RATE_LIMIT_DELAY)

#     return results[:PAPERS_PER_QUERY]

# # =========================
# # MAIN EXECUTION
# # =========================
# def main():
#     print("🚀 Research Paper Collection Started\n")

#     queries = load_queries(QUERIES_FILE)
#     OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

#     if OUTPUT_FILE.exists():
#         try:
#             all_papers = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
#         except json.JSONDecodeError:
#             all_papers = {}
#     else:
#         all_papers = {}

#     for query in queries:
#         print(f"🔍 Fetching papers for: {query}")

#         year_filter = None if any(y in query for y in ["2023-", "2024-", "2025-"]) else "2023-"
#         papers = fetch_papers(query, year_filter)

#         all_papers[query] = papers
#         print(f"✅ Collected {len(papers)} papers\n")

#         time.sleep(RATE_LIMIT_DELAY)

#     OUTPUT_FILE.write_text(
#         json.dumps(all_papers, indent=2, ensure_ascii=False),
#         encoding="utf-8"
#     )

#     print(f"📁 Data saved to: {OUTPUT_FILE}")
#     print("🎉 Process Completed")

# # =========================
# # ENTRY POINT
# # =========================
# if __name__ == "__main__":
#     main()






# # scripts/list.py
# import json
# import time
# import os
# from pathlib import Path
# import requests

# # --- paths (keep your structure) ---
# SCRIPT_DIR = Path(__file__).resolve().parent
# ROOT = SCRIPT_DIR.parent
# QUERIES_PATH = ROOT / "queries.txt"
# OUT_PATH = ROOT / "research" / "papers.json"

# # --- API setup ---
# BASE = "https://api.semanticscholar.org/graph/v1"
# ENDPOINT = f"{BASE}/paper/search/bulk"

# # Load API key from .env or environment
# def load_api_key() -> str:
#     # lightweight .env loader (no dependency required)
#     dotenv = ROOT / ".env"
#     if dotenv.exists():
#         for line in dotenv.read_text(encoding="utf-8").splitlines():
#             if line.strip().startswith("S2_API_KEY="):
#                 return line.split("=", 1)[1].strip()
#     # fallback to real env var
#     key = os.getenv("S2_API_KEY")
#     if key:
#         return key
#     raise RuntimeError("S2_API_KEY not found. Put it in Springboard/.env or set an env var.")

# API_KEY = load_api_key()
# HEADERS = {"x-api-key": API_KEY}

# # Only ask for fields you need (fewer fields = faster)
# FIELDS = "paperId,title,url,year,publicationDate,publicationTypes,openAccessPdf,authors"

# # how many papers to collect per query (approx; will stop when next token ends)
# TARGET_PER_QUERY = 40  # change to 100 if you want more

# def fetch_bulk(query: str, year_filter: str | None = "2023-") -> list[dict]:
#     """Fetch papers for one query using token pagination."""
#     params = {"query": query, "fields": FIELDS}
#     if year_filter:
#         params["year"] = year_filter  # e.g., "2023-"

#     results: list[dict] = []
#     token = None

#     while True:
#         p = params.copy()
#         if token:
#             p["token"] = token

#         r = requests.get(ENDPOINT, params=p, headers=HEADERS, timeout=60)
#         if r.status_code == 429:
#             # rate-limit backoff
#             time.sleep(1.3)
#             continue
#         r.raise_for_status()

#         payload = r.json()
#         data = payload.get("data", [])
#         results.extend(data)

#         # stop early if we already have enough
#         if TARGET_PER_QUERY and len(results) >= TARGET_PER_QUERY:
#             break

#         token = payload.get("token")
#         if not token:
#             break

#         # be nice to the 1 req/sec rule
#         time.sleep(1.1)

#     return results

# def load_queries(path: Path) -> list[str]:
#     return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

# def main():
#     queries = load_queries(QUERIES_PATH)
#     if not queries:
#         print("queries.txt is empty. Add one query per line.")
#         return

#     # load existing file so repeated runs append/merge
#     if OUT_PATH.exists():
#         try:
#             all_data = json.loads(OUT_PATH.read_text(encoding="utf-8"))
#         except Exception:
#             all_data = {}
#     else:
#         OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
#         all_data = {}

#     for q in queries:
#         print(f"\n[Fetching] {q}")
#         # if your query string already has a year like 2024-, we won't add our default filter
#         yr = None if any(s in q for s in ("2023-", "2024-", "2025-")) else "2023-"
#         papers = fetch_bulk(q, yr)
#         all_data[q] = papers
#         print(f"[OK] {len(papers)} papers")

#         # respect rate limit between queries too
#         time.sleep(1.1)

#     OUT_PATH.write_text(json.dumps(all_data, ensure_ascii=False, indent=2), encoding="utf-8")
#     print(f"\nSaved -> {OUT_PATH}")

# if __name__ == "__main__":
#     main()










































# import requests
# import json
# import argparse
# from pathlib import Path

# OPENALEX_URL = "https://api.openalex.org/works"

# def load_queries(path: Path):
#     return [line.strip() for line in path.read_text().splitlines() if line.strip()]

# def fetch_openalex(query: str, limit: int = 20):
#     params = {
#         "search": query,
#         "per-page": limit,
#         "mailto": "example@mail.com"  # required by OpenAlex politely
#     }

#     response = requests.get(OPENALEX_URL, params=params)
#     data = response.json()

#     papers = []
#     for item in data.get("results", []):
#         papers.append({
#             "title": item.get("title"),
#             "authors": [auth["author"]["display_name"] for auth in item.get("authorships", [])],
#             "year": item.get("publication_year"),
#             "venue": item.get("host_venue", {}).get("display_name"),
#             "url": item.get("primary_location", {}).get("landing_page_url"),
#             "doi": item.get("doi"),
#             "abstract": item.get("abstract_inverted_index"),
#             "cited_by_count": item.get("cited_by_count"),
#             "openalex_id": item.get("id"),
#             "query": query
#         })
#     return papers

# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--queries", default="research/queries.txt")
#     parser.add_argument("--out", default="research/papers.json")
#     parser.add_argument("--limit", type=int, default=20)
#     args = parser.parse_args()

#     query_file = Path(args.queries)
#     queries = load_queries(query_file)

#     all_papers = []
#     for q in queries:
#         print(f"Searching: {q}")
#         papers = fetch_openalex(q, args.limit)
#         print(f" → found {len(papers)} papers")
#         all_papers.extend(papers)

#     out_path = Path(args.out)
#     out_path.write_text(json.dumps(all_papers, indent=2))

#     print(f"\nSaved: {args.out} ({len(all_papers)} papers total)")

# if __name__ == "__main__":
#     main()
