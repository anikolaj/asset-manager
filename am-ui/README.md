# AM Dashboard

Frontend for [asset-manager](../README.md). It shows portfolio value, YTD, daily PnL, cash, allocation, and positions.

Stack: React, TypeScript, Vite, MUI, AG Grid, and Recharts.

## Prerequisites

- Node.js 18+
- The Flask API running locally (`am_api.py` in the repo root)

The dashboard loads `http://localhost:5000/portfolio?name=<portfolio>`. Without the API, the page still renders but stats, charts, and the positions table stay empty.

Start the API from the repo root:

```bash
python am_api.py
```

It listens on port 5000. The portfolio name is currently hardcoded as `test` in `src/App.tsx`. Change that constant to load a different portfolio.

## Setup

Install and run from this directory (`am-ui`), not the repo root:

```bash
npm install
npm run dev
```

Vite prints a local URL (usually `http://localhost:5173`).

## Scripts

| Command | Description |
| --- | --- |
| `npm run dev` | Start the Vite dev server |
| `npm run build` | Typecheck and produce a production build in `dist/` |
| `npm run preview` | Serve the production build locally |
| `npm run lint` | Run ESLint |

## Layout

```
am-ui/
├── index.html          # App shell
├── src/
│   ├── main.tsx        # React entry, MUI theme
│   ├── App.tsx         # Dashboard
│   └── App.css         # Grid and scrollbar styles
├── public/             # Static assets (favicon)
└── package.json
```

`App.tsx` fetches the portfolio, adds a cash row to the positions list, and drives the summary cards, pie chart, and table.
