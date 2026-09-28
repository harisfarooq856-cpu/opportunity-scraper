# 🎯 Opportunity Scraper & Multi-Source Intelligence Engine

An autonomous, multi-platform intelligence harvester built to uncover local business opportunities, active contracts, decision-maker profiles, and customer sentiment across **Google Maps, LinkedIn, Upwork, Facebook, Reddit, and Quora**.

Directly bridges with **[Opportunity Hunter Web Engine](https://hunter.inceptial.team)** (`opportunity-hunter`).

---

## ⚡ Features & Data Engines

1. **Google Maps (GMB) Engine:**
   * Business names, domains, phone numbers, review counts, average star rating.
   * Scrapes 1-star / negative review clusters to identify recurring service friction (e.g. missed weekend emergency calls, slow callbacks).
2. **LinkedIn Decision-Maker Engine:**
   * **Company Targeting:** Extracts Owners, Founders, CEOs, General Managers, and VPs for any specific company.
   * **Method 1 (Zero-Login / Open Index):** Instant discovery of decision-makers across entire metro areas.
   * **Method 3 (Session Ingestion):** Deep buying-intent search using `li_at` session cookies.
3. **Upwork Contracts & Hiring Engine:**
   * Extracts live active contract postings, project budgets, hourly rates, scope descriptions, and direct application links with 0 login required.
4. **Facebook Meta Ad Intelligence Engine:**
   * Scrapes active business advertisers, Facebook Page URLs, ad creative copy, and website destinations directly via Meta Ad Library.
5. **Reddit Sentiment Engine:**
   * Scrapes city subreddits (e.g., `r/rva`, `r/HVAC`) for unfiltered homeowner recommendations and complaint threads with exact ISO timestamps.
6. **Quora Problem Engine:**
   * Extracts high-intent question topics and troubleshooting FAQs for personalized outreach copy.
7. **Excel Tracker Enrichment Engine:**
   * Automatically ingests member/prospect spreadsheets (e.g. `Master BCA Member Onboarding Tracker.xlsx`) and enriches missing Job Titles, LinkedIn URLs, Phone Numbers, and Locations.
8. **Direct Laravel API Bridge:**
   * Pipes harvested data directly into `https://hunter.inceptial.team/campaigns/ingest` for 1-click review and dispatch.

---

## 🚀 Quick Start

### 1. Installation
```bash
cd opportunity-scraper
pip install -r requirements.txt
playwright install chromium
```

### 2. Run Full Multi-Platform Harvest
```bash
python harvest.py --location "Richmond, VA" --industry "HVAC"
```

### 3. Run Upwork Jobs & Facebook Advertisers Only
```bash
python harvest.py --platform upwork --industry "HVAC" --upwork-limit 10
python harvest.py --platform facebook --location "Richmond, VA" --industry "HVAC" --facebook-limit 10
```

### 4. Find Decision-Makers for a Specific Company
```bash
python harvest.py --platform linkedin --company "Woodfin - Your Home Team" --linkedin-limit 10
```

### 5. Enrich Member Tracker Excel Spreadsheet
```bash
python enrich_tracker.py
```

### 6. Run & Sync Directly to Opportunity Hunter Web App
```bash
python harvest.py --platform gmb --location "Richmond, VA" --industry "Plumbing" --sync --api-url "https://hunter.inceptial.team"
```

---

## 📁 Output Artifacts
* **Structured JSON:** `output/harvested_opportunities.json`
* **Executive Markdown Briefing:** `output/HARVEST_REPORT.md`
* **Enriched Spreadsheet:** `C:\Users\seoin\Downloads\Master_BCA_Member_Onboarding_Tracker_ENRICHED.xlsx`
