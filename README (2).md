# HERMES Dashboard — Render Deployment

This is a modern, read-only, smooth dashboard for the HERMES trading bot.

## Features
- Interactive StarNetOS sprite world (HERMES walks when you click rooms)
- Clean modern UI with excellent spacing
- Equity as histogram (Chart.js)
- Market Strength as animated loading bars (orange = weak → blue = strong)
- Live metrics + GBrain + Signals
- Fully responsive (great on iPhone)

## How to Deploy on Render.com (Static Site)

1. Create a new GitHub repository (or use an existing one).
2. Upload the contents of this `render_dashboard` folder to the repo.
3. Go to https://dashboard.render.com
4. Click **New +** → **Static Site**
5. Connect your GitHub repo
6. Set these values:
   - **Name**: `hermes-dashboard`
   - **Build Command**: (leave empty)
   - **Publish directory**: `.` (or the folder if you put it in a subfolder)
7. Click **Create Static Site**

Render will give you a public URL (e.g. `https://hermes-dashboard.onrender.com`).

The dashboard is now live and smooth.

## Updating Data (Read-only)
Currently uses sample data. To show real data from your local bot:
- Export `latest_balance.json`, `learning_memory.json`, and recent trades
- Update the values in `index.html` (or load from a `data.json` file)
- Push the changes to GitHub — Render will auto-deploy

Future improvement: We can add a small local script that pushes updates to a public JSON.

## PWA (Install as App)
Open the site in Safari on iPhone → Share → "Add to Home Screen". It will feel like a native app.

## Local Testing
Just open `index.html` in any browser. No server needed.