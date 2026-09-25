import asyncio
import urllib.parse
from playwright.async_api import async_playwright
from .config import USER_AGENT

async def harvest_quora(niche="HVAC repair cost questions", limit=20):
    """
    Harvests authentic Quora user questions and discussion URLs using
    automated headless search indices that bypass Cloudflare blocks.
    """
    print("\n" + "=" * 65)
    print(f" ❓ HARVESTING QUORA (Questions for '{niche}')")
    print("=" * 65)
    
    quora_questions = []
    seen_urls = set()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=USER_AGENT,
            locale="en-US"
        )
        page = await context.new_page()
        
        # Search Quora indexed threads
        search_query = f"site:quora.com {niche}"
        search_url = f"https://www.bing.com/search?q={urllib.parse.quote_plus(search_query)}"
        print(f"Querying Search Index: {search_url}")
        
        try:
            await page.goto(search_url, timeout=30000)
            await page.wait_for_timeout(3000)
            
            results = await page.query_selector_all('li.b_algo h2 a')
            print(f"Found {len(results)} potential Quora discussions. Parsing top {limit}...\n")
            
            for idx, r in enumerate(results):
                if len(quora_questions) >= limit:
                    break
                    
                title = await r.inner_text()
                link = await r.get_attribute('href') or ''
                clean_title = title.replace(' - Quora', '').replace(' | Quora', '').strip()
                
                if clean_title and len(clean_title) > 10 and 'quora.com' in link:
                    if link not in seen_urls:
                        seen_urls.add(link)
                        item = {
                            "platform": "Quora",
                            "number": len(quora_questions) + 1,
                            "question": clean_title,
                            "url": link
                        }
                        quora_questions.append(item)
                        print(f"  -> [{len(quora_questions)}] {clean_title}")
                        
        except Exception as err:
            print(f"  [!] Quora scraping error: {err}")
            
        await browser.close()
        
    print(f"Extracted {len(quora_questions)} authentic Quora questions.\n")
    return quora_questions
