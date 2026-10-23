#!/usr/bin/env python3
"""Fill in missing `doi` fields in the publication data files using the Crossref API.

Usage (from the site folder):
    pip install pyyaml
    python tools/add_dois.py --mailto your.email@unican.es

What it does
  * For every entry without a `doi`, it asks Crossref for the best match of title, first author and year.
  * It only accepts a match when the title is nearly identical AND the first author appears in the
    Crossref author list (arXiv and other preprint DOIs are ignored).
  * Entries that already have a DOI are never touched. Existing files are backed up as *.bak the first time.
  * Entries it could not match are listed in doi_unmatched.txt, so you can add those DOIs by hand if you wish.

Options:
    --files   data files to process (default: _data/journals.yml _data/conferences.yml)
    --dry-run show what would be added without writing anything
    --limit   stop after N lookups (useful for a first test, e.g. --limit 10)
"""
import argparse, difflib, json, os, re, shutil, sys, time, unicodedata
import urllib.error, urllib.parse, urllib.request

import yaml

API = "https://api.crossref.org/works"
PREPRINT_PREFIXES = ("10.48550/", "10.36227/", "10.31219/", "10.22541/")


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def first_surname(authors):
    first = re.split(r",| and ", authors)[0].strip()
    return norm(re.split(r"[ .]+", first.strip())[-1])


def fetch(title, surname, year, mailto):
    params = {
        "query.bibliographic": f"{title} {surname}",
        "rows": 5,
        "select": "DOI,title,issued,author,type",
        "filter": f"from-pub-date:{year - 2},until-pub-date:{year + 2}",
        "mailto": mailto,
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": f"personal-site-doi-tool (mailto:{mailto})"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)["message"]["items"]
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                time.sleep(5 * (attempt + 1)); continue
            if e.code == 404:
                return []
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(5 * (attempt + 1))
    return []


def best_match(entry, items):
    title, surname = norm(entry["title"]), first_surname(entry["authors"])
    best, best_ratio = None, 0.0
    for it in items:
        doi = it.get("DOI", "")
        if it.get("type") == "posted-content" or doi.lower().startswith(PREPRINT_PREFIXES):
            continue
        cand = norm((it.get("title") or [""])[0])
        ratio = difflib.SequenceMatcher(None, title, cand).ratio()
        authors = [norm(a.get("family", "")) for a in it.get("author", [])]
        if authors and not any(surname == a or surname in a.split() for a in authors):
            continue
        if not authors and ratio < 0.97:
            continue
        if ratio >= 0.92 and ratio > best_ratio:
            best, best_ratio = doi, ratio
    return best


def save(path, data, header):
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False, width=10000, default_flow_style=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mailto", required=True, help="your email (Crossref asks for it, it gives you a faster queue)")
    ap.add_argument("--files", nargs="+", default=["_data/journals.yml", "_data/conferences.yml"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--delay", type=float, default=0.6, help="seconds between requests")
    a = ap.parse_args()

    done, unmatched = 0, []
    for path in a.files:
        header = open(path, encoding="utf-8").readline().strip()
        header = header if header.startswith("#") else "# Publications. Newest first."
        data = yaml.safe_load(open(path, encoding="utf-8"))
        if not a.dry_run and not os.path.exists(path + ".bak"):
            shutil.copy(path, path + ".bak")
        added = 0
        for i, e in enumerate(data):
            if e.get("doi"):
                continue
            if a.limit and done >= a.limit:
                break
            done += 1
            doi = best_match(e, fetch(e["title"], first_surname(e["authors"]), int(e["year"]), a.mailto))
            if doi:
                added += 1
                print(f"[{os.path.basename(path)} {i + 1}] {doi}  <-  {e['title'][:60]}")
                if not a.dry_run:
                    e["doi"] = doi
            else:
                unmatched.append(f"{os.path.basename(path)} | {e['year']} | {e['title']}")
            if not a.dry_run and done % 20 == 0:
                save(path, data, header)  # keep progress if interrupted
            time.sleep(a.delay)
        if not a.dry_run:
            save(path, data, header)
        print(f"{path}: {added} DOIs added")
    if unmatched and not a.dry_run:
        open("doi_unmatched.txt", "w", encoding="utf-8").write("\n".join(unmatched) + "\n")
        print(f"{len(unmatched)} entries without a confident match are listed in doi_unmatched.txt")


if __name__ == "__main__":
    main()
