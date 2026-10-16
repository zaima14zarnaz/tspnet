"use strict";

/* ======================== EDIT YOUR DETAILS HERE ========================
   The supplied PDF is anonymous. Add the actual authors in publication order.
   Empty public links are hidden (arXiv) or labeled coming soon (Code).
   All paths are relative so this works at username.github.io/TSPNet/.
*/
const SITE_CONFIG = {
  authors: [
    // { name: "Full Name", bibtexName: "Surname, Given Names", affiliations: [1], url: "https://example.com" },
  ],
  affiliations: [
    // { id: 1, name: "Florida International University" },
  ],
  authorNote: "", // Example: "* Equal contribution. † Corresponding author."
  links: {
    paper: "./assets/papers/tspnet-paper.pdf",
    supplement: "./assets/papers/tspnet-supplement.pdf",
    code: "https://github.com/zaima14zarnaz/tspnet",
    arxiv: "", // Add the actual arXiv URL when available.
  },
  citation: {
    key: "tspnet2027",
    title: "Object-Grounded Text Priors for Saliency Ranking Detection",
    booktitle: "Proceedings of the IEEE/CVF Winter Conference on Applications of Computer Vision (WACV)",
    year: "2027",
    doi: "", // Optional. Leave empty until assigned.
    pages: "", // Optional. Leave empty until assigned.
    url: "", // Optional. Your permanent paper or project URL.
  },
};
/* ======================== END OF CONFIGURATION ======================== */

// Table 2 of the supplied paper. Arrays are [SA-SOR, SOR, MAE].
const BENCHMARKS = [
  { method: "RSDNet", backbone: "ResNet-101", family: "CNN", ASSR: [0.6313,0.7758,0.1236], IRSR: [0.4232,0.7096,0.1175], SIFR: [0.4791,0.7239,0.0772] },
  { method: "ASSR", backbone: "ResNet-101", family: "CNN", ASSR: [0.5400,0.7920,0.1010], IRSR: [0.3207,0.6521,0.1098], SIFR: [0.3281,0.5843,0.0624] },
  { method: "IRSR-U", backbone: "ResNet-50", family: "CNN", ASSR: [0.7051,0.8314,0.0923], IRSR: [0.5647,0.8143,0.0953], SIFR: [0.5585,0.7487,0.0465] },
  { method: "IRSR-L", backbone: "ResNet-50", family: "CNN", ASSR: [0.7090,0.8283,0.0914], IRSR: [0.5648,0.8141,0.0953], SIFR: [0.5585,0.7487,0.0465] },
  { method: "SOR", backbone: "VoVNet-39", family: "CNN", ASSR: [0.6371,0.8330,0.0799], IRSR: [0.5171,0.7909,0.0988], SIFR: [0.3820,0.7554,0.0580] },
  { method: "QAGNet", backbone: "ResNet-50", family: "CNN", ASSR: [0.7545,0.8514,0.0619], IRSR: [0.6110,0.8108,0.0845], SIFR: [0.6119,0.7899,0.0437] },
  { method: "LG-SOR", backbone: "ResNet-50", family: "CNN", ASSR: [0.7360,0.8875,0.0650], IRSR: [0.5690,0.8150,0.0620], SIFR: [0.5840,0.7900,0.0380] },
  { method: "TSPNet", backbone: "ResNet-50", family: "CNN", ours: true, ASSR: [0.7975,0.9002,0.0913], IRSR: [0.7009,0.8521,0.0521], SIFR: [0.6151,0.8059,0.0470] },
  { method: "TSPNet", backbone: "ResNet-101", family: "CNN", ours: true, ASSR: [0.8117,0.9071,0.0621], IRSR: [0.7144,0.8613,0.0490], SIFR: [0.6208,0.8143,0.0304] },
  { method: "OCOR", backbone: "Swin-L", family: "Transformer", ASSR: [0.6413,0.8843,0.0786], IRSR: [0.5183,0.8149,0.1003], SIFR: [0.4392,0.7436,0.0488] },
  { method: "QAGNet", backbone: "Swin-B", family: "Transformer", ASSR: [0.7741,0.8583,0.0538], IRSR: [0.6252,0.8152,0.0792], SIFR: [0.6167,0.7933,0.0409] },
  { method: "QAGNet", backbone: "Swin-L", family: "Transformer", ASSR: [0.7793,0.8591,0.0492], IRSR: [0.6466,0.8241,0.0768], SIFR: [0.6206,0.7982,0.0416] },
  { method: "LG-SOR", backbone: "Swin-L", family: "Transformer", ASSR: [0.7810,0.8920,0.0490], IRSR: [0.6390,0.8410,0.0480], SIFR: [0.6130,0.8040,0.0370] },
  { method: "TSPNet", backbone: "Swin-B", family: "Transformer", ours: true, ASSR: [0.8146,0.9057,0.0480], IRSR: [0.7066,0.8551,0.0406], SIFR: [0.6177,0.8125,0.0279] },
  { method: "TSPNet", backbone: "Swin-L", family: "Transformer", ours: true, ASSR: [0.8142,0.9104,0.0459], IRSR: [0.7214,0.8615,0.0355], SIFR: [0.6240,0.8140,0.0277] },
];

function safeHref(value) {
  if (typeof value !== "string" || !value.trim()) return null;
  const trimmed = value.trim();
  // Allow website URLs and local document paths; reject executable schemes.
  if (/^https?:\/\//i.test(trimmed)) return trimmed;
  if (/^(?:\.\/)?assets\/[a-z0-9_./-]+$/i.test(trimmed)) return trimmed;
  return null;
}

function makeElement(tag, text, className) {
  const element = document.createElement(tag);
  if (text !== undefined) element.textContent = text;
  if (className) element.className = className;
  return element;
}

function configureHeader() {
  const authorContainer = document.getElementById("authors");
  SITE_CONFIG.authors.forEach((author) => {
    const span = makeElement("span", undefined, "author");
    const url = safeHref(author.url);
    const name = makeElement(url ? "a" : "span", author.name);
    if (url) { name.href = url; name.target = "_blank"; name.rel = "noopener"; }
    span.append(name);
    if (author.affiliations?.length) span.append(makeElement("sup", author.affiliations.join(",")));
    if (author.marker) span.append(makeElement("sup", author.marker));
    authorContainer.append(span);
    const metadata = document.createElement("meta");
    metadata.name = "citation_author";
    metadata.content = author.name;
    document.head.append(metadata);
  });
  authorContainer.hidden = SITE_CONFIG.authors.length === 0;
  const affiliations = document.getElementById("affiliations");
  SITE_CONFIG.affiliations.forEach((item) => {
    const span = makeElement("span", undefined, "affiliation");
    span.append(makeElement("sup", item.id), document.createTextNode(` ${item.name}`));
    affiliations.append(span);
  });
  affiliations.hidden = SITE_CONFIG.affiliations.length === 0;
  const note = document.getElementById("author-note");
  note.textContent = SITE_CONFIG.authorNote;
  note.hidden = !SITE_CONFIG.authorNote;

  for (const name of ["paper", "supplement", "code", "arxiv"]) {
    const link = document.getElementById(`${name}-link`);
    const url = safeHref(SITE_CONFIG.links[name]);
    if (url) {
      link.href = url;
      link.target = "_blank";
      link.rel = "noopener";
      link.hidden = false;
      link.classList.remove("unavailable");
      link.removeAttribute("aria-disabled");
      link.removeAttribute("tabindex");
      if (name === "code") document.getElementById("code-label").textContent = "Code";
    } else if (name === "code") {
      link.removeAttribute("href");
      link.setAttribute("aria-disabled", "true");
      link.setAttribute("tabindex", "-1");
      link.classList.add("unavailable");
    } else {
      link.hidden = true;
    }
  }
}

function configureResults() {
  let dataset = "ASSR";
  const tabs = [...document.querySelectorAll("[data-dataset]")];
  const filter = document.getElementById("backbone-filter");
  const body = document.getElementById("results-body");
  const panel = document.getElementById("results-panel");
  const caption = document.getElementById("results-caption");
  const takeaway = document.getElementById("results-takeaway");
  const messages = {
    ASSR: "On ASSR, TSPNet achieves SA-SOR of 0.8146 with Swin-B and SOR of 0.9104 with Swin-L.",
    IRSR: "On IRSR, TSPNet with Swin-L achieves SA-SOR of 0.7214, SOR of 0.8615, and MAE of 0.0355.",
    SIFR: "On SIFR, TSPNet with Swin-L achieves SA-SOR of 0.6240 and MAE of 0.0277; ResNet-101 gives its highest SOR of 0.8143.",
  };
  function render() {
    const fragment = document.createDocumentFragment();
    for (const family of ["CNN", "Transformer"]) {
      if (filter.value !== "all" && filter.value !== family) continue;
      const rows = BENCHMARKS.filter((row) => row.family === family);
      const best = [0, 1, 2].map((i) => (i === 2 ? Math.min : Math.max)(...rows.map((row) => row[dataset][i])));
      const group = makeElement("tr", undefined, "group-row");
      const groupHeading = makeElement("th", `${family}-based`);
      groupHeading.colSpan = 5;
      group.append(groupHeading);
      fragment.append(group);
      for (const row of rows) {
        const tr = makeElement("tr", undefined, row.ours ? "ours" : "");
        const method = makeElement("th", row.method);
        method.scope = "row";
        tr.append(method, makeElement("td", row.backbone));
        row[dataset].forEach((value, i) => {
          const cell = makeElement("td");
          cell.append(makeElement(value === best[i] ? "strong" : "span", value.toFixed(4)));
          tr.append(cell);
        });
        fragment.append(tr);
      }
    }
    body.replaceChildren(fragment);
    caption.textContent = `${dataset} benchmark. Higher is better for SA-SOR and SOR; lower is better for MAE.`;
    takeaway.textContent = messages[dataset];
    panel.setAttribute("aria-labelledby", `tab-${dataset.toLowerCase()}`);
  }
  function activate(tab) {
    dataset = tab.dataset.dataset;
    tabs.forEach((item) => {
      const selected = item === tab;
      item.classList.toggle("is-active", selected);
      item.setAttribute("aria-selected", String(selected));
      item.tabIndex = selected ? 0 : -1;
    });
    render();
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => activate(tab));
    tab.addEventListener("keydown", (event) => {
      let next;
      if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
      if (event.key === "ArrowLeft") next = (index - 1 + tabs.length) % tabs.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = tabs.length - 1;
      if (next === undefined) return;
      event.preventDefault();
      tabs[next].focus();
      activate(tabs[next]);
    });
  });
  filter.addEventListener("change", render);
  panel.setAttribute("role", "tabpanel");
  document.getElementById("results-controls").hidden = false;
  render();
}

function configureCarousel() {
  const carousel = document.querySelector(".carousel");
  const slides = [...carousel.querySelectorAll(".carousel-slide")];
  const buttons = [...carousel.querySelectorAll("[data-slide]")];
  const status = document.getElementById("carousel-status");
  let current = 0;
  function show(index, announce = true) {
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, i) => { slide.hidden = i !== current; });
    buttons.forEach((button, i) => {
      button.classList.toggle("is-active", i === current);
      button.setAttribute("aria-pressed", String(i === current));
    });
    if (announce) status.textContent = `Comparison ${current + 1} of ${slides.length}`;
  }
  buttons.forEach((button) => button.addEventListener("click", () => show(Number(button.dataset.slide))));
  carousel.querySelector(".previous").addEventListener("click", () => show(current - 1));
  carousel.querySelector(".next").addEventListener("click", () => show(current + 1));
  carousel.querySelector(".carousel-controls").addEventListener("keydown", (event) => {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    event.preventDefault();
    show(current + (event.key === "ArrowLeft" ? -1 : 1));
    buttons[current].focus();
  });
  carousel.classList.add("is-enhanced");
  carousel.querySelector(".carousel-controls").hidden = false;
  show(0, false);
}

function configureImageViewer() {
  const dialog = document.getElementById("image-dialog");
  if (typeof dialog.showModal !== "function") return; // Links open the full image as a fallback.
  const image = document.getElementById("dialog-image");
  let opener;
  document.querySelectorAll("[data-zoom]").forEach((link) => {
    link.addEventListener("click", (event) => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0) return;
      event.preventDefault();
      opener = link;
      image.src = link.href;
      image.alt = link.querySelector("img").alt;
      document.getElementById("dialog-caption").textContent = link.dataset.caption;
      dialog.showModal();
      document.body.style.overflow = "hidden";
    });
  });
  dialog.querySelector(".dialog-close").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    const rect = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) dialog.close();
  });
  dialog.addEventListener("close", () => {
    document.body.style.overflow = "";
    image.removeAttribute("src");
    opener?.focus();
  });
}

function bibtexEscape(value) {
  return String(value).replace(/[&%_#{}]/g, (character) => `\\${character}`);
}

function configureCitation() {
  if (!SITE_CONFIG.authors.length) return; // Never publish a fabricated author list.
  const citation = SITE_CONFIG.citation;
  const fields = {
    author: SITE_CONFIG.authors.map((author) => bibtexEscape(author.bibtexName || author.name)).join(" and "),
    title: bibtexEscape(citation.title),
    booktitle: bibtexEscape(citation.booktitle),
    year: citation.year,
  };
  for (const field of ["pages", "doi", "url"]) if (citation[field]) fields[field] = bibtexEscape(citation[field]);
  const key = String(citation.key).replace(/[^a-z0-9_:-]/gi, "");
  const text = `@inproceedings{${key},\n${Object.entries(fields).map(([key, value]) => `  ${key.padEnd(9)} = {${value}}`).join(",\n")}\n}`;
  document.getElementById("bibtex").textContent = text;
  document.getElementById("citation-section").hidden = false;
  const button = document.getElementById("copy-citation");
  const status = document.getElementById("copy-status");
  let resetTimer;
  button.addEventListener("click", async () => {
    let copied = false;
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        copied = true;
      }
    } catch (_) { /* Use the local-file clipboard fallback below. */ }
    if (!copied) {
      const area = makeElement("textarea");
      area.value = text;
      area.style.cssText = "position:fixed;left:-9999px;top:0";
      document.body.append(area);
      area.select();
      try { copied = document.execCommand("copy"); } catch (_) { copied = false; }
      area.remove();
      button.focus();
    }
    button.querySelector("span").textContent = copied ? "Copied!" : "Select text";
    status.textContent = copied ? "Citation copied to clipboard." : "Automatic copy is unavailable. The citation text is selected; copy it manually.";
    if (!copied) {
      const range = document.createRange();
      range.selectNodeContents(document.getElementById("bibtex"));
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
    }
    clearTimeout(resetTimer);
    resetTimer = setTimeout(() => { button.querySelector("span").textContent = "Copy"; }, 2500);
  });
}

configureHeader();
configureResults();
configureCarousel();
configureImageViewer();
configureCitation();
