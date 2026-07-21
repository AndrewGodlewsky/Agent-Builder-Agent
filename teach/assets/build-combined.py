import re
from pathlib import Path

root = Path(r"C:\Users\godle\OneDrive\Desktop\Claude\Agent-Builder-Agent\teach")
lessons_dir = root / "lessons"
css = (root / "assets" / "course.css").read_text(encoding="utf-8")
js = (root / "assets" / "quiz.js").read_text(encoding="utf-8")

lesson_files = sorted(lessons_dir.glob("0*.html"))
assert len(lesson_files) == 11, [p.name for p in lesson_files]

slug_to_anchor = {p.name: f"#lesson-{p.name[2:4]}" for p in lesson_files}

sections = []
toc = []
for p in lesson_files:
    html = p.read_text(encoding="utf-8")
    nn = p.name[2:4]

    m = re.search(r"<body>(.*)<script>", html, re.S)
    assert m, f"no body/script split in {p.name}"
    content = m.group(1).strip()

    # lesson-to-lesson links become in-page anchors
    for slug, anchor in slug_to_anchor.items():
        content = content.replace(f'href="{slug}"', f'href="{anchor}"')
    # reference links: combined file lives in teach/, one level up from lessons/
    content = content.replace('href="../reference/', 'href="reference/')

    title_m = re.search(r"<h1>(.*?)</h1>", content, re.S)
    title = re.sub(r"\s+", " ", title_m.group(1)).strip() if title_m else p.name
    series_m = re.search(r'titleblock-series">(.*?)</div>', content, re.S)
    series = re.sub(r"\s+", " ", series_m.group(1)).strip() if series_m else ""
    course = series.split("·")[-1].strip() if "·" in series else series

    toc.append((nn, title, course))
    sections.append(f'<section class="lesson" id="lesson-{nn}">\n{content}\n</section>')

# table of contents grouped by course
toc_rows = "\n".join(
    f'    <li><a href="#lesson-{nn}"><span class="toc-no">{nn}</span> {title}</a>'
    f'<span class="toc-course">{course}</span></li>'
    for nn, title, course in toc
)

extra_css = """
/* ---- combined-edition additions ---- */
.lesson { margin-top: 4.5rem; border-top: 4px double var(--ink); padding-top: 3rem; }
.lesson:first-of-type { margin-top: 3rem; }
.toc { background: var(--panel); border: 2px solid var(--ink); padding: 1.5rem; }
.toc h2 { margin-bottom: 1rem; }
.toc ol { list-style: none; margin: 0; }
.toc li { display: flex; align-items: baseline; gap: 0.6rem; padding: 0.35rem 0; border-bottom: 1px solid var(--hairline); margin: 0; }
.toc li:last-child { border-bottom: none; }
.toc a { text-decoration: none; font-family: var(--display); font-weight: 700; }
.toc a:hover { text-decoration: underline; }
.toc-no { color: var(--draft); font-family: var(--data); font-weight: 400; }
.toc-course { margin-left: auto; font-family: var(--data); font-size: 0.7rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); }
.backtotop { display: block; text-align: right; font-family: var(--data); font-size: 0.8rem; margin-top: 1.5rem; }
html { scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
@media print { .toc a { color: var(--ink); } .backtotop { display: none; } .lesson { break-before: page; } }
"""

back_to_top = '<a class="backtotop" href="#top">Contents ↑</a>'
body_sections = f"\n{back_to_top}\n".join(sections)

out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Copilot Studio Field Manual — Complete Edition</title>
<style>
{css}
{extra_css}
</style>
</head>
<body id="top">

<header class="titleblock">
  <div class="titleblock-top">
    <div class="titleblock-no">∑</div>
    <div class="titleblock-main">
      <div class="titleblock-series">Copilot Studio Field Manual · Complete Edition</div>
      <h1>All eleven lessons, one document</h1>
    </div>
  </div>
  <div class="titleblock-meta">
    <div><span class="k">Contents</span>Courses A–C · 11 lessons · field checks included</div>
    <div><span class="k">Reference</span><a href="reference/glossary.html">Glossary</a> · <a href="reference/limits-cheatsheet.html">Limits</a> · <a href="reference/decision-flowcharts.html">Flowcharts</a></div>
    <div><span class="k">Source</span>research/ · built 2026-07-21</div>
  </div>
</header>

<nav class="toc">
  <h2>Contents</h2>
  <ol>
{toc_rows}
  </ol>
</nav>

{body_sections}
{back_to_top}

<script>
{js}
</script>
</body>
</html>
"""

dest = root / "field-manual-complete.html"
dest.write_text(out, encoding="utf-8")
print("wrote", dest, len(out), "chars")
print("quizzes:", out.count('class="quiz"'), "| sections:", out.count('<section'), "| toc entries:", len(toc))
for nn, title, course in toc:
    print(nn, "-", title, "|", course)
