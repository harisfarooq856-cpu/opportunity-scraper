# 🎯 Opportunity Scraper & Multi-Source Intelligence Engine

An autonomous, multi-platform intelligence harvester built to uncover local business opportunities, customer pain points, SEO/speed deficits, and decision-maker contact profiles across Google Maps, LinkedIn, Reddit, and Quora.

Directly bridges with **[Opportunity Hunter Web Engine](https://hunter.inceptial.team)** (`opportunity-hunter`).

---

## ⚡ Features & Data Engines

1. **Google Maps (GMB) Engine:**
   * Business names, domains, phone numbers, review counts, average star rating.
   * Scrapes 1-star / negative review clusters to identify recurring service friction (e.g. missed weekend emergency calls, slow callbacks).
2. **LinkedIn Decision-Maker Engine:**
   * **Method 1 (Zero-Login / Open Index):** Instant discovery of Owners, Presidents, Founders, and Operations Heads.
   * **Method 3 (Session Ingestion):** Deep buying-intent search using session cookies.
3. **Reddit Sentiment Engine:**
   * Scrapes city subreddits (e.g., `r/rva`, `r/HVAC`) for unfiltered homeowner recommendations and complaint threads.
4. **Quora Problem Engine:**
   * Extracts high-intent question topics and troubleshooting FAQs for content & pitch personalization.
5. **Direct Laravel API Bridge:**
   * Pipes harvested data directly into `https://hunter.inceptial.team/campaigns/ingest` for 1-click review and dispatch.

---

## 🚀 Quick Start

### 1. Installation
```bash
cd opportunity-scraper
pip install -r requirements.txt
```

### 2. Run Full Multi-Platform Harvest
```bash
python harvest.py --location "Richmond, VA" --industry "HVAC"
```

### 3. Run GMB + LinkedIn Only and Sync Directly to Web App
```bash
python harvest.py --platform gmb --location "Richmond, VA" --industry "Plumbing" --sync --api-url "https://hunter.inceptial.team"
```

### 4. Run LinkedIn Method 1 (Zero-Login Decision-Maker Discovery)
```bash
python harvest.py --platform linkedin --location "Richmond, VA" --industry "Roofing" --linkedin-limit 20
```

---

## 📁 Output Artifacts
* **Structured JSON:** `output/harvested_opportunities.json`
* **Executive Markdown Briefing:** `output/HARVEST_REPORT.md`
