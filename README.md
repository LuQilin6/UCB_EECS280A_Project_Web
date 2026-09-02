# UCB_EECS280A_Project_Web

A cyber-themed project console for UC Berkeley EECS 280A coursework, built with plain HTML/CSS/JS and hosted on GitHub Pages.

**Live site:** https://LuQilin6.github.io/UCB_EECS280A_Project_Web/

## Structure

- `index.html`, `assets/home/` — the landing page (terminal-styled header, animated background, project selector grid). Styling/scripts here are scoped to the home page only.
- `projects/project0` … `projects/project4/` — one folder per project, each with its own `index.html`, `style.css`, and `script.js`. Every project page is fully self-contained, so any page can be redesigned or rebuilt without touching the home page or any other project page.

## Editing a project page

Open the relevant `projects/projectN/index.html`, `style.css`, and `script.js` and replace the placeholder content. Nothing outside that folder needs to change.

## Local preview

Just open `index.html` in a browser, or serve the repo root with any static file server (e.g. `npx serve .`).

## Deployment

GitHub Pages is configured to deploy from the `main` branch, root folder (Settings → Pages). Any push to `main` updates the live site.
