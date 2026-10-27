// The van page: photos, the main facts, and Peter's history of the van (data/van-history.md).
import type { Site } from "./data";

const esc = (s: string) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!);

/** Bold and links inside a line of the history. */
function inline(s: string) {
  return esc(s)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\[([^\]]+)\]\((https:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
}

/** The small part of Markdown the history uses: headings, paragraphs, bullet lists and one table.
 *  The title and the date line at the top are left out (the page has its own). */
export function historyHtml(md: string) {
  const out: string[] = [];
  let list: string[] | null = null, table: string[][] | null = null;
  const flush = () => {
    if (list) { out.push(`<ul>${list.map((l) => `<li>${inline(l)}</li>`).join("")}</ul>`); list = null; }
    if (table) {
      const [head, , ...rows] = table;
      out.push(`<div class="table-wrap"><table><thead><tr>${head.map((h) => `<th>${inline(h)}</th>`).join("")}</tr></thead>
        <tbody>${rows.map((r) => `<tr>${r.map((c) => `<td>${inline(c)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`);
      table = null;
    }
  };
  for (const raw of md.split(/\r?\n/)) {
    const line = raw.trim();
    if (line.startsWith("|")) { (table ??= []).push(line.slice(1, -1).split("|").map((c) => c.trim())); continue; }
    if (line.startsWith("- ")) { if (table) flush(); (list ??= []).push(line.slice(2)); continue; }
    flush();
    if (!line || line.startsWith("# ") || /^[A-Z][a-z]{2} \d{1,2}, \d{4} ·/.test(line)) continue;
    if (line.startsWith("## ")) out.push(`<h2>${inline(line.slice(3))}</h2>`);
    else out.push(`<p>${inline(line)}</p>`);
  }
  flush();
  return out.join("\n");
}

export async function renderVan(el: HTMLElement, site: Site) {
  const page = site.van_page;
  const photos = page?.photos ?? [];
  el.innerHTML = `
  <section class="sect van-page">
    <p class="kicker">The van</p>
    <h1>VW LT31 Westfalia Florida</h1>
    <div class="van-top">
      ${photos[0] ? `<img class="van-hero" src="${photos[0].image}" alt="${esc(photos[0].alt)}">` : ""}
      <dl class="van-specs">${site.van.specs.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("")}</dl>
    </div>
    ${photos.length > 1 ? `<div class="van-grid">${photos.slice(1).map((p) => `<img src="${p.image}" alt="${esc(p.alt)}" loading="lazy">`).join("")}</div>` : ""}
    <div class="van-history" id="van-history"><p class="muted">Loading the history of the van…</p></div>
  </section>`;
  if (!page) return;
  const r = await fetch(page.history);
  document.getElementById("van-history")!.innerHTML = r.ok ? historyHtml(await r.text()) : `<p class="muted">The history could not be loaded.</p>`;
}
