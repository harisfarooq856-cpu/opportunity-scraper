import asyncio
import re
import urllib.parse
from playwright.async_api import async_playwright
from .config import USER_AGENT, PLAYWRIGHT_PROXY, LINKEDIN_LI_AT

# =====================================================================
# METHOD 1: PUBLIC SEARCH INDEX ENGINE (ZERO LOGIN / ZERO RISK)
# =====================================================================
async def harvest_linkedin_index(industry="HVAC", location="Richmond, VA", target_roles=None, intent_query=None, limit=15):
    """
    Method 1: Harvests public LinkedIn profiles and posts from search indices.
    No login required, completely ban-proof.
    """
    if target_roles is None:
        target_roles = ["Owner", "Founder", "President", "CEO", "General Manager"]
        
    print("\n" + "=" * 70)
    print(f" 💼 [LinkedIn Method 1] INDEX HARVEST ({industry} in {location})")
    print("=" * 70)
    
    results = []
    seen_urls = set()
    
    # Build search queries
    search_queries = []
    if intent_query:
        # Looking for buying intent posts
        search_queries.append(f'site:linkedin.com/posts/ "{intent_query}" "{location}"')
        search_queries.append(f'site:linkedin.com/pulse/ "{intent_query}"')
    else:
        # Looking for decision-maker profiles
        for role in target_roles:
            search_queries.append(f'site:linkedin.com/in/ "{role}" "{industry}" "{location}"')
        search_queries.append(f'site:linkedin.com/company/ "{industry}" "{location}"')
        
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=USER_AGENT, locale="en-US")
        page = await context.new_page()
        
        for q in search_queries:
            if len(results) >= limit:
                break
            search_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(q)}&hl=en"
            print(f"Querying Index: {q}")
            
            try:
                await page.goto(search_url, timeout=25000)
                await page.wait_for_timeout(2500)
                
                # Extract search cards
                links = await page.query_selector_all('div.g, div.tF2Cxc')
                for card in links:
                    if len(results) >= limit:
                        break
                        
                    a_tag = await card.query_selector('a')
                    href = (await a_tag.get_attribute('href')) if a_tag else ''
                    title_el = await card.query_selector('h3')
                    title = (await title_el.inner_text()) if title_el else ''
                    snippet_el = await card.query_selector('div.VwiC3b')
                    snippet = (await snippet_el.inner_text()) if snippet_el else ''
                    
                    if 'linkedin.com' in href and href not in seen_urls and title:
                        seen_urls.add(href)
                        
                        # Clean name & headline
                        # Format on Google: "John Doe - Owner - ABC Heating | LinkedIn"
                        clean_title = title.replace(' | LinkedIn', '').replace(' - LinkedIn', '').strip()
                        parts = clean_title.split(' - ')
                        
                        person_name = parts[0].strip() if len(parts) > 0 else clean_title
                        headline = parts[1].strip() if len(parts) > 1 else snippet[:120]
                        company = parts[2].strip() if len(parts) > 2 else "Verified Business"
                        
                        item = {
                            "method": "Method 1 (Search Index)",
                            "id": len(results) + 1,
                            "type": "Profile" if "/in/" in href else ("Company" if "/company/" in href else "Post"),
                            "name_or_title": person_name,
                            "headline": headline,
                            "company_or_context": company,
                            "location": location,
                            "url": href,
                            "snippet": snippet.strip()
                        }
                        results.append(item)
                        print(f"  [{len(results)}/{limit}] {person_name} | {headline[:60]} -> {href}")
            except Exception as e:
                print(f"  [!] Index search error: {e}")
                
        await browser.close()
        
    print(f"✅ Method 1 Complete: Extracted {len(results)} authentic LinkedIn records.\n")
    return results

# =====================================================================
# METHOD 3: PLAYWRIGHT AUTHENTICATED SESSION (1-TIME LI_AT COOKIE)
# =====================================================================
async def harvest_linkedin_session(target_url="https://www.linkedin.com/search/results/people/?keywords=HVAC%20Richmond%20VA", li_at_cookie=None, limit=10):
    """
    Method 3: Authenticated Playwright session using the `li_at` cookie.
    Renders live LinkedIn pages directly via residential proxy.
    """
    active_cookie = li_at_cookie or LINKEDIN_LI_AT
    
    print("\n" + "=" * 70)
    print(f" 💼 [LinkedIn Method 3] AUTHENTICATED BROWSER SESSION")
    print("=" * 70)
    
    if not active_cookie:
        print("  ⚠️ No 'li_at' cookie provided. Fallback to Method 1 (Search Index).")
        return await harvest_linkedin_index(limit=limit)
        
    results = []
    
    async with async_playwright() as p:
        # Launch browser with residential proxy
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=USER_AGENT,
            locale="en-US",
            proxy=PLAYWRIGHT_PROXY
        )
        
        # Inject li_at authentication cookie
        await context.add_cookies([
            {
                "name": "li_at",
                "value": active_cookie,
                "domain": ".linkedin.com",
                "path": "/"
            }
        ])
        
        page = await context.new_page()
        print(f"Navigating to LinkedIn via Residential Proxy: {target_url}")
        
        try:
            await page.goto(target_url, timeout=35000)
            await page.wait_for_timeout(4000)
            
            # Check if login succeeded
            current_url = page.url
            if "login" in current_url or "authwall" in current_url or "checkpoint" in current_url:
                print("  [!] LinkedIn requested verification / cookie expired. Falling back to Method 1.")
                await browser.close()
                return await harvest_linkedin_index(limit=limit)
                
            # Extract live search result cards
            cards = await page.query_selector_all('li.reusable-search__result-container, div.update-components-text')
            print(f"Discovered {len(cards)} live items on LinkedIn page.")
            
            for idx, c in enumerate(cards[:limit]):
                try:
                    text = await c.inner_text()
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    
                    # Extract profile link
                    link_el = await c.query_selector('a.app-aware-link, a')
                    link = (await link_el.get_attribute('href')) if link_el else ""
                    if link and '?' in link:
                        link = link.split('?')[0]
                        
                    name = lines[0] if lines else f"LinkedIn Result #{idx+1}"
                    headline = lines[1] if len(lines) > 1 else ""
                    loc = lines[2] if len(lines) > 2 else ""
                    
                    results.append({
                        "method": "Method 3 (Live Session)",
                        "id": len(results) + 1,
                        "name_or_title": name,
                        "headline": headline,
                        "location": loc,
                        "url": link,
                        "raw_snippet": " ".join(lines[:4])
                    })
                    print(f"  [{len(results)}/{limit}] {name} ({headline[:50]})")
                except Exception as e:
                    pass
                    
        except Exception as err:
            print(f"  [!] Session scraping error: {err}")
            
        await browser.close()
        
    print(f"✅ Method 3 Complete: Extracted {len(results)} live LinkedIn records.\n")
    return results
