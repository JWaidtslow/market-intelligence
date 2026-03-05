# GitHub Actions opsætning

## Én gang: opret repo og aktiver GitHub Pages

### 1. Opret et privat GitHub repo
Gå til https://github.com/new og opret et **privat** repo, f.eks. `market-intelligence`.

### 2. Push koden op
Åbn Terminal i din `Intelligence`-mappe og kør:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/JWaidtslow/market-intelligence.git
git push -u origin main
```

### 3. Aktiver GitHub Pages
- Gå til repo → **Settings → Pages**
- Under *Source*: vælg **Deploy from a branch**
- Branch: `main` / folder: `/docs`
- Klik **Save**

Dit dashboard vil herefter være tilgængeligt på:
`https://DITBRUGERNAVN.github.io/market-intelligence/`

### 4. Giv Actions skriveadgang
- Gå til repo → **Settings → Actions → General**
- Under *Workflow permissions*: vælg **Read and write permissions**
- Klik **Save**

---

## Køre manuelt (test)
Gå til repo → **Actions → Ugentlig konkurrentovervågning → Run workflow**

## Automatisk kørsel
Sker automatisk hver **onsdag kl. 08:00** dansk tid.
Resultatet committes tilbage til repoet og GitHub Pages opdateres automatisk.

---

## Opdatere koden
Du kan fortsat redigere koden via Claude/Cowork-sessionen.
Push ændringer til GitHub med:
```bash
git pull
git add .
git commit -m "Opdatering"
git push
```
git remote set-url origin https://github.com/JWaidtslow/market-intelligence.git
git push -u origin main