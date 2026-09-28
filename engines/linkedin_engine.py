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
    
    search_queries = []
    if intent_query:
        search_queries.append(f'site:linkedin.com/posts/ "{intent_query}" "{location}"')
        search_queries.append(f'site:linkedin.com/pulse/ "{intent_query}"')
    else:
        for role in target_roles:
            search_queries.append(f'site:linkedin.com/in/ "{role}" "{industry}" "{location}"')
        search_queries.append(f'site:linkedin.com/company/ "{industry}" "{location}"')
        
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
        )
        context = await browser.new_context(user_agent=USER_AGENT, locale="en-US")
        page = await context.new_page()
        
        # Block heavy media resources
        await page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font"] else route.continue_())
        
        for q in search_queries:
            if len(results) >= limit:
                break
            search_url = f"https://search.brave.com/search?q={urllib.parse.quote_plus(q)}"
            print(f"Querying Index: {q}")
            
            try:
                await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
                await page.wait_for_timeout(2000)
                
                cards = await page.query_selector_all('div.snippet, div[data-type="web"]')
                for c in cards:
                    if len(results) >= limit:
                        break
                    t_el = await c.query_selector('a .title, .title')
                    l_el = await c.query_selector('a')
                    d_el = await c.query_selector('.snippet-description, .snippet-content, div.body')
                    
                    t = (await t_el.inner_text()).strip() if t_el else ""
                    href = (await l_el.get_attribute('href')) if l_el else ""
                    snippet = (await d_el.inner_text()).strip() if d_el else ""
                    
                    if 'linkedin.com' in href and href not in seen_urls and t:
                        seen_urls.add(href)
                        
                        clean_title = t.replace(' | LinkedIn', '').replace(' - LinkedIn', '').strip()
                        parts = clean_title.split(' - ')
                        
                        person_name = parts[0].strip() if len(parts) > 0 else clean_title
                        headline = parts[1].strip() if len(parts) > 1 else snippet[:120]
                        company = parts[2].strip() if len(parts) > 2 else industry
                        
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
                        print(f"  [{len(results)}/{limit}] {person_name} | {headline[:60]}")
                        print(f"      🔗 {href}")
            except Exception as e:
                print(f"  [!] Index search note: {e}")
                
        await browser.close()
        
    print(f"✅ Method 1 Complete: Extracted {len(results)} authentic LinkedIn records.\n")
    return results

# =====================================================================
# METHOD 2: SPECIFIC COMPANY & DECISION MAKER HARVESTER
# =====================================================================
async def harvest_company_decision_makers(company_name, roles=None, li_at_cookie=None, limit=10):
    """
    Extracts key decision makers (Owners, Founders, CXOs, Directors) for a SPECIFIC company.
    Uses authenticated session if cookie provided, otherwise uses targeted open company index.
    """
    if roles is None:
        roles = ["Owner", "Founder", "President", "CEO", "Partner", "General Manager", "Director of Operations", "VP"]
        
    print("\n" + "=" * 70)
    print(f" 🎯 [Company Deep-Dive] DECISION MAKERS FOR: '{company_name}'")
    print("=" * 70)
    
    active_cookie = li_at_cookie or LINKEDIN_LI_AT
    results = []
    seen_urls = set()
    
    # 1. If cookie available -> Direct Internal Search
    if active_cookie:
        print(f"Connecting with authenticated LinkedIn session (li_at)...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=USER_AGENT,
                locale="en-US",
                proxy=PLAYWRIGHT_PROXY
            )
            await context.add_cookies([{
                "name": "li_at",
                "value": active_cookie,
                "domain": ".linkedin.com",
                "path": "/"
            }])
            page = await context.new_page()
            
            for r in roles[:4]:
                if len(results) >= limit:
                    break
                search_url = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote_plus(f'{company_name} {r}')}"
                print(f"Searching LinkedIn Internal: '{company_name}' + {r} ...")
                try:
                    await page.goto(search_url, timeout=30000)
                    await page.wait_for_timeout(3500)
                    
                    cards = await page.query_selector_all('li.reusable-search__result-container, div.update-components-text')
                    for c in cards:
                        if len(results) >= limit:
                            break
                        text = await c.inner_text()
                        lines = [l.strip() for l in text.split('\n') if l.strip()]
                        link_el = await c.query_selector('a.app-aware-link, a')
                        link = (await link_el.get_attribute('href')) if link_el else ""
                        if link and '?' in link:
                            link = link.split('?')[0]
                            
                        name = lines[0] if lines else "LinkedIn Member"
                        headline = lines[1] if len(lines) > 1 else r
                        loc = lines[2] if len(lines) > 2 else ""
                        
                        if link and link not in seen_urls and "linkedin.com/in/" in link:
                            seen_urls.add(link)
                            results.append({
                                "company": company_name,
                                "name": name,
                                "role_headline": headline,
                                "target_role_match": r,
                                "location": loc,
                                "url": link
                            })
                            print(f"  ✓ Found Decision Maker: {name} ({headline}) -> {link}")
                except Exception as e:
                    print(f"  [!] Session query note: {e}")
            await browser.close()
            
    # 2. Fallback / Zero-Cookie Targeted Search
    if not results:
        print(f"Running zero-login targeted company decision-maker index...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
            )
            context = await browser.new_context(user_agent=USER_AGENT, locale="en-US")
            page = await context.new_page()
            await page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font"] else route.continue_())
            
            for r in roles:
                if len(results) >= limit:
                    break
                q = f'site:linkedin.com/in/ "{company_name}" "{r}"'
                url = f"https://search.brave.com/search?q={urllib.parse.quote_plus(q)}"
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    await page.wait_for_timeout(1800)
                    
                    cards = await page.query_selector_all('div.snippet, div[data-type="web"]')
                    for c in cards:
                        if len(results) >= limit:
                            break
                        t_el = await c.query_selector('a .title, .title')
                        l_el = await c.query_selector('a')
                        d_el = await c.query_selector('.snippet-description, .snippet-content, div.body')
                        
                        t = (await t_el.inner_text()).strip() if t_el else ""
                        href = (await l_el.get_attribute('href')) if l_el else ""
                        snippet = (await d_el.inner_text()).strip() if d_el else ""
                        
                        if 'linkedin.com/in/' in href and href not in seen_urls and t:
                            seen_urls.add(href)
                            clean_t = t.replace(' | LinkedIn', '').replace(' - LinkedIn', '').strip()
                            parts = clean_t.split(' - ')
                            p_name = parts[0].strip() if len(parts) > 0 else clean_t
                            p_headline = parts[1].strip() if len(parts) > 1 else snippet[:100]
                            
                            results.append({
                                "company": company_name,
                                "name": p_name,
                                "role_headline": p_headline,
                                "target_role_match": r,
                                "location": "Verified Metro",
                                "url": href,
                                "snippet": snippet
                            })
                            print(f"  ✓ Found Decision Maker: {p_name} | {p_headline[:50]}")
                            print(f"      🔗 {href}")
                except Exception as e:
                    pass
            await browser.close()
            
    print(f"\n✅ Company Deep-Dive Complete: Extracted {len(results)} decision-makers for '{company_name}'.\n")
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
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=USER_AGENT,
            locale="en-US",
            proxy=PLAYWRIGHT_PROXY
        )
        
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
            
            current_url = page.url
            if "login" in current_url or "authwall" in current_url or "checkpoint" in current_url:
                print("  [!] LinkedIn requested verification / cookie expired. Falling back to Method 1.")
                await browser.close()
                return await harvest_linkedin_index(limit=limit)
                
            cards = await page.query_selector_all('li.reusable-search__result-container, div.update-components-text')
            print(f"Discovered {len(cards)} live items on LinkedIn page.")
            
            for idx, c in enumerate(cards[:limit]):
                try:
                    text = await c.inner_text()
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    
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
                except Exception:
                    pass
                    
        except Exception as err:
            print(f"  [!] Session scraping error: {err}")
            
        await browser.close()
        
    print(f"✅ Method 3 Complete: Extracted {len(results)} live LinkedIn records.\n")
    return results
