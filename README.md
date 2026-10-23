# Ignacio Santamaria: personal website

Static site built with Jekyll, which GitHub Pages runs automatically. There is no build step to run
and no external service (BibBase is gone): all content lives in plain files.

## Where things live

| To change...                  | Edit this file                                  |
|-------------------------------|-------------------------------------------------|
| About me, contact box, research lines | `index.html`                            |
| Email, Scholar/LinkedIn links | `_config.yml`                                   |
| Books                         | `_data/books.yml`                               |
| Journal articles              | `_data/journals.yml`                            |
| Conference papers             | `_data/conferences.yml`                         |
| Book chapters                 | `_data/chapters.yml`                            |
| Order of the publication sections | `_data/pubsections.yml`                     |
| Projects                      | `_data/projects.yml`                            |
| CV PDF                        | replace `assets/cv/CV_Santamaria_Oct26.pdf` (and update `cv_pdf` in `_config.yml` if the file name changes) |
| Colors, fonts, spacing        | `assets/css/main.css` (the tokens are at the top) |

## Adding a publication

Add the entry at the **top** of the right file (newest first). Numbers (J116, C212, ...) are computed
automatically, and the year headings follow the `year` field.

```yaml
- authors: A. Author, I. Santamaria and B. Author
  title: Title of the paper
  venue: IEEE Transactions on Signal Processing, vol. 75, pp. 1–15, 2027
  year: 2027
  # optional fields:
  doi: 10.1109/TSP.2027.1234567
  pdf: /assets/papers/my_preprint.pdf      # a file in assets/papers/, or a full https:// link (see below)
  award: Best Paper Award
```

Quote a value with `"..."` if it contains a colon followed by a space (`: `) or starts with a special
character. Your name is highlighted automatically when it appears as `I. Santamaria` or `I. Santamaría`.

## Links to PDFs

The `pdf` field accepts either a file stored in this repository (`/assets/papers/name.pdf`) or any full
link (`https://...`), for example a OneDrive or Dropbox "anyone with the link can view" share link.
Check that the sharing setting is public, otherwise visitors will be asked to sign in.

## DOIs

The DOIs in `journals.yml` and `conferences.yml` come from `CV_Santamaria_Oct26.tex`. To add one by hand,
put `doi: 10.xxxx/yyyy` in the entry (without the `https://doi.org/` prefix); the "DOI" link is built
automatically. `tools/add_dois.py` can look up the missing ones in Crossref (needs Python 3 and
`pip install pyyaml`):

```
python tools/add_dois.py --mailto your.email@unican.es --limit 10 --dry-run   # quick test, writes nothing
python tools/add_dois.py --mailto your.email@unican.es                        # full run
```

It only accepts a match when the title is almost identical and the first author appears in the Crossref
record. Entries it cannot match are listed in `doi_unmatched.txt`. Review the result with `git diff`.

## Preview locally (optional)

Requires Ruby (any recent version). From this folder:

```
bundle install
bundle exec jekyll serve
```

If you change the `Gemfile`, delete `Gemfile.lock` first.

Then open http://localhost:4000.

## Deploy

Commit and push. GitHub Pages rebuilds the site in a minute or two.
In the repository, Settings > Pages must point to the branch you push to (folder: `/ (root)`).
