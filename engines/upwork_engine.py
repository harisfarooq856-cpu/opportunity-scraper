import asyncio
import urllib.parse
import re
import sys
from playwright.async_api import async_playwright
from .config import USER_AGENT

async def harvest_upwork(industry="HVAC", limit=10):
    """
    Harvests authentic, live Upwork job opportunities and client contracts.
    Extracts job titles, estimated budgets/rates, client requirements, and direct application links.
    Zero login required, ban-proof open search index harvesting.
    """
    print("\n" + "=" * 70)
    print(f" 💼 [Upwork Engine] HARVESTING JOBS & CONTRACTS ({industry})")
    print("=" * 70)
    
    results = []
    seen_urls = set()
    
    search_queries = [
        f'site:upwork.com/freelance-jobs "{industry}" apply',
        f'site:upwork.com/freelance-jobs "{industry}"',
        f'site:upwork.com/jobs "{industry}"'
    ]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
        )
        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1280, "height": 800},
            locale="en-US"
        )
        page = await context.new_page()
        
        # Block heavy media resources
        await page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font"] else route.continue_())
        
        for q in search_queries:
            if len(results) >= limit:
                break
                
            search_url = f"https://search.brave.com/search?q={urllib.parse.quote_plus(q)}"
            print(f"Querying Index: {q}")
            
            try:
                await page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(2500)
                
                # Check for bot challenge
                title = await page.title()
                if "Verifying" in title or "CAPTCHA" in title:
                    print("  [!] Bot check detected on primary index, switching to secondary index...")
                    bing_url = f"https://www.bing.com/search?q={urllib.parse.quote_plus(q)}&setlang=en-us"
                    await page.goto(bing_url, wait_until="domcontentloaded", timeout=20000)
                    await page.wait_for_timeout(2500)
                    
                    cards = await page.query_selector_all('li.b_algo')
                    for c in cards:
                        if len(results) >= limit:
                            break
                        h2 = await c.query_selector('h2 a')
                        p_el = await c.query_selector('.b_caption p, p')
                        t = (await h2.inner_text()).strip() if h2 else ""
                        u = (await h2.get_attribute('href')) if h2 else ""
                        d = (await p_el.inner_text()).strip() if p_el else ""
                        
                        if t and u and u not in seen_urls and "upwork.com" in u:
                            seen_urls.add(u)
                            clean_t = t.replace(" - Upwork", "").replace(" | Upwork", "").strip()
                            budget_m = re.search(r'(\$\d+[\d,]*(?:\s*-\s*\$\d+[\d,]*)?(?:\/(?:hr|hour|hr\b))?)', f"{clean_t} {d}")
                            budget = budget_m.group(1) if budget_m else "Custom Contract / Fixed"
                            
                            results.append({
                                "platform": "Upwork",
                                "id": len(results) + 1,
                                "job_title": clean_t,
                                "budget_or_rate": budget,
                                "url": u,
                                "snippet": d
                            })
                            print(f"  [{len(results)}/{limit}] {clean_t} | {budget}")
                    continue
                
                # Parse search snippets
                cards = await page.query_selector_all('div.snippet, div[data-type="web"]')
                for c in cards:
                    if len(results) >= limit:
                        break
                    t_el = await c.query_selector('a .title, .title')
                    l_el = await c.query_selector('a')
                    d_el = await c.query_selector('.snippet-description, .snippet-content, div.body')
                    
                    t = (await t_el.inner_text()).strip() if t_el else ""
                    u = (await l_el.get_attribute('href')) if l_el else ""
                    d = (await d_el.inner_text()).strip() if d_el else ""
                    
                    if t and u and u not in seen_urls and "upwork.com" in u:
                        # Skip generic navigation links
                        if "/hire/" in u and "/freelance-jobs/apply/" not in u and not any(k in t.lower() for k in ["job", "needed", "specialist", "coordinator", "developer", "technician", "engineer"]):
                            continue
                            
                        seen_urls.add(u)
                        clean_t = t.replace(" - Upwork", "").replace(" | Upwork", "").strip()
                        budget_m = re.search(r'(\$\d+[\d,]*(?:\s*-\s*\$\d+[\d,]*)?(?:\/(?:hr|hour|hr\b))?)', f"{clean_t} {d}")
                        budget = budget_m.group(1) if budget_m else "Custom Contract / Fixed"
                        
                        results.append({
                            "platform": "Upwork",
                            "id": len(results) + 1,
                            "job_title": clean_t,
                            "budget_or_rate": budget,
                            "url": u,
                            "snippet": d
                        })
                        print(f"  [{len(results)}/{limit}] {clean_t} | {budget}")
                        print(f"      🔗 {u}")
                        
            except Exception as e:
                print(f"  [!] Query error: {e}")
                
        await browser.close()
        
    print(f"\n✅ Upwork Harvest Complete: Extracted {len(results)} authentic job opportunities.\n")
    return results
