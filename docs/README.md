# TSPNet project website

A GitHub Pages-ready research project page for **Object-Grounded Text Priors for Saliency Ranking Detection**, accepted at **WACV 2027**.

The layout follows the academic project-page style of [ZOO-Prune](https://aim-skku.github.io/ZOO-Prune/): a centered title and author area, rounded paper/code buttons, a wide teaser, abstract, introduction, method figure, quantitative results, qualitative comparisons, and citation. This is an original implementation with no third-party JavaScript, CSS framework, build tool, or external font dependency. There are no video or poster buttons or sections.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | All page sections, text, figures, and the static ASSR table |
| `styles.css` | Typography, layout, responsive styles, tables, and image viewer |
| `script.js` | Editable publication details, benchmark data, dataset switching, carousel, image enlargement, and citation copying |
| `assets/images/` | Four figures extracted from the supplied paper and supplement |
| `assets/papers/tspnet-paper.pdf` | The supplied main-paper PDF |
| `assets/papers/tspnet-supplement.pdf` | The supplied supplementary PDF |
| `assets/favicon.svg` | Small project favicon |
| `.nojekyll` | Disables Jekyll processing on GitHub Pages |
| `LICENSE` | MIT license for the original website code; papers and figures retain their own rights |

## 1. Preview locally

Unzip the project and open `index.html` in a browser. No installation is needed. Relative paths and a regular deferred script let the page work directly from local files as well as on GitHub Pages. Keep `styles.css`, `script.js`, and `assets/` alongside `index.html`.

## 2. Add authors and public links

Edit **`SITE_CONFIG` at the top of `script.js`**. The uploaded paper is anonymous, so the page deliberately omits author names and affiliations until you add the correct list. Example configuration, using placeholder names to illustrate the format:

```js
authors: [
  {
    name: "First Author",
    bibtexName: "Author, First",
    affiliations: [1],
    url: "https://example.com/first-author",
  },
  {
    name: "Second Author",
    bibtexName: "Author, Second",
    affiliations: [1, 2],
    url: "", // Empty means display the name without a hyperlink.
  },
],
affiliations: [
  { id: 1, name: "First Institution" },
  { id: 2, name: "Second Institution" },
],
authorNote: "", // Set only if applicable.
links: {
  paper: "./assets/papers/tspnet-paper.pdf",
  supplement: "./assets/papers/tspnet-supplement.pdf",
  code: "https://github.com/YOUR-USERNAME/YOUR-MODEL-REPOSITORY",
  arxiv: "", // Add the real arXiv URL when available.
},
```

Replace the example names, order, institutions, and URLs with the actual publication information. You can add `marker: "*"` or `marker: "†"` to an author and explain it in `authorNote` if appropriate.

- **Paper** and **Supplement** work immediately using the bundled PDFs.
- **Code** displays a non-clickable “coming soon” label until its URL is configured.
- **arXiv** is hidden until its URL is configured.
- **BibTeX** appears automatically once at least one author is configured. Author order is preserved. Fill `bibtexName` carefully for each author; if omitted, the displayed name is used.
- Do not add a DOI, page range, or proceedings URL until those details have been assigned. These optional citation fields start empty.
- For an author list visible without JavaScript, also add the final author markup directly inside `#authors` and `#affiliations` in `index.html`, remove their `hidden` attributes, and change `configureHeader()` to replace rather than append those contents.

The bundled PDFs are the **anonymous submission copies** you provided. To show the camera-ready version, replace those PDFs while keeping the filenames, or change the two URLs in `SITE_CONFIG`. The website describes the paper as accepted, based on your confirmation.

## 3. Publish on GitHub Pages

1. Create a repository, for example **`TSPNet`**, in your GitHub account. A public repository works with GitHub Free; availability for private repositories depends on your account plan.
2. Upload the **contents** of this folder to the repository's `main` branch. `index.html` must be at the repository root, not inside another `tspnet-website` subfolder. Include the full `assets/` directory. If the web uploader omits `.nojekyll`, create that empty file with GitHub's **Add file → Create new file** command.
3. Open the repository's **Settings → Pages**.
4. Under **Build and deployment**, select **Deploy from a branch**.
5. Select **main** and **/(root)**, then save.
6. Once deployment finishes, GitHub displays your URL, normally `https://YOUR-USERNAME.github.io/TSPNet/`. This is an example URL; no repository or site has been created for you.

All asset paths start with `./`, so the page also works under a repository subpath. No custom domain or GitHub Actions workflow is required for this setup.

Official instructions: [Create a GitHub Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site) and [Configure the publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

## 4. Edit the content or appearance

- Change the page title, abstract, descriptions, captions, footer, and search/social metadata in `index.html`.
- Change the blue accent, body font, or content width in the `:root` variables and `body` rule in `styles.css`.
- Replace images inside `assets/images/` to update figures. If the aspect ratio changes, update each image's `width` and `height` attributes in `index.html`.
- Edit `BENCHMARKS` in `script.js` to update results. Each dataset is stored as `[SA-SOR, SOR, MAE]`. The selected dataset table is generated from these values, with best values highlighted separately for CNN and Transformer families. Also update the static ASSR rows in `index.html` if numbers change, so visitors without JavaScript see matching results.
- Keep the main title and citation title consistent if the final paper title changes.
- The supplied figures are extracted image assets rather than screenshots of full PDF pages. Their original labels and scientific content are preserved.

## Interaction and accessibility

- Dataset tabs support clicks and Left/Right/Home/End keys. A backbone selector filters the results.
- The qualitative carousel has numbered buttons, previous/next controls, and arrow-key navigation while its controls are focused. It does not autoplay.
- Figure links open a modal image viewer in browsers with native `dialog` support; otherwise they open the full image. Escape, the close button, or clicking the backdrop closes the viewer. Native modal focus behavior is retained, and focus returns to the figure link.
- On narrow screens, tables and enlarged figures can be scrolled horizontally.
- Without JavaScript, the abstract, figures, ASSR results, both qualitative comparisons, and bundled paper links remain usable.
- Motion respects the operating system's reduced-motion setting. No analytics or trackers are included.

## Content provenance and verification

The abstract, benchmark values (Table 2), and matching-corruption values (Table 4) come from your supplied main paper. Figures come from the main paper and supplementary material. Results are displayed as reported, not independently reproduced.

JavaScript syntax, local asset references, image dimensions, and benchmark values were checked during preparation. The page was not tested in a browser in this environment; open `index.html` to review appearance before publishing. Check the final author order, resource links, and camera-ready PDFs before your release.
