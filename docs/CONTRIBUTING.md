# Contributing

## Running tests

### API (Python)

```bash
cd apps/api
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python -m pytest tests -v --tb=short
```

### Web (Jest)

From repo root with dependencies installed:

```bash
cd apps/web
npm install
npm test
```

If you use pnpm at root: `pnpm install` then `pnpm --filter web test`.

## Pushing to GitHub

After creating a new repository on GitHub (do not initialize with README):

```bash
git remote add origin https://github.com/YOUR_USERNAME/liveproof-ai.git
git branch -M main
git push -u origin main
```

Or with SSH:

```bash
git remote add origin git@github.com:YOUR_USERNAME/liveproof-ai.git
git branch -M main
git push -u origin main
```
