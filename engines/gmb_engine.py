import asyncio
import re
from playwright.async_api import async_playwright
from .config import USER_AGENT

async def harvest_gmb(location="Richmond, VA", industry="HVAC", max_listings=5, max_reviews_per_listing=5):
    """
    Harvests authentic Google Business Profiles (GMB) and verified customer reviews
    via Playwright headless Chromium.
    """
    print("\n" + "=" * 65)
    print(f" 📍 HARVESTING GOOGLE MAPS ({industry} in {location})")
    print("=" * 65)
    
    gmb_results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=USER_AGENT,
            locale="en-US"
        )
        page = await context.new_page()
        
        search_query = f"{industry} in {location}".replace(' ', '+')
        url = f"https://www.google.com/maps/search/{search_query}?hl=en"
        print(f"Loading Google Maps: {url}")
        
        try:
            await page.goto(url, timeout=35000)
            await page.wait_for_timeout(4000)
            
            cards = await page.query_selector_all('div.Nv2PK')
            print(f"Discovered {len(cards)} listings in viewport. Processing top {max_listings}...\n")
            
            for idx in range(min(len(cards), max_listings)):
                try:
                    cards_now = await page.query_selector_all('div.Nv2PK')
                    if idx >= len(cards_now):
                        break
                    c = cards_now[idx]
                    
                    text = await c.inner_text()
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    b_name = lines[0] if lines else f"Listing #{idx+1}"
                    
                    rating = "N/A"
                    review_count = "N/A"
                    for l in lines:
                        m = re.search(r'([0-5]\.[0-9])\s*\(([\d,]+)\)', l)
                        if m:
                            rating = m.group(1)
                            review_count = m.group(2)
                            break
                            
                    print(f"[{idx+1}/{max_listings}] Inspecting: {b_name} (⭐ {rating} | {review_count} reviews)")
                    
                    # Click listing card
                    link = await c.query_selector('a.hfpxzc')
                    if link:
                        await link.click()
                    else:
                        await c.click()
                    await page.wait_for_timeout(3500)
                    
                    # Extract Address & Phone from main panel if present
                    phone = "N/A"
                    address = "N/A"
                    info_buttons = await page.query_selector_all('button[data-item-id*="phone:"], button[data-item-id*="address"]')
                    for ib in info_buttons:
                        aria = await ib.get_attribute('aria-label') or ''
                        if "Phone:" in aria:
                            phone = aria.replace("Phone:", "").strip()
                        elif "Address:" in aria:
                            address = aria.replace("Address:", "").strip()
                    
                    # Switch to Reviews Tab
                    rev_tab = await page.query_selector('button[role="tab"][aria-label*="Reviews"], button[aria-label*="Reviews for"]')
                    if rev_tab:
                        await rev_tab.click()
                        await page.wait_for_timeout(3000)
                    
                    # Extract verified reviews
                    extracted_reviews = []
                    
                    # Review author headers
                    action_btns = await page.query_selector_all('button[aria-label*="Actions for"]')
                    for ab in action_btns[:max_reviews_per_listing]:
                        aria = await ab.get_attribute('aria-label') or ''
                        author_name = aria.replace("Actions for", "").replace("'s review", "").replace(".", "").strip()
                        if author_name:
                            extracted_reviews.append({
                                "reviewer_name": author_name,
                                "review_source": "Google Maps Verified Review",
                                "business": b_name
                            })
                            
                    # Review text blocks
                    review_cards = await page.query_selector_all('div.jftiEf, div.MyEned, span.wiI7pd, div.G54Mfd')
                    for r_i, rc in enumerate(review_cards[:max_reviews_per_listing]):
                        r_text = await rc.inner_text()
                        cleaned_r = re.sub(r'\s+', ' ', r_text).strip()
                        if cleaned_r and len(cleaned_r) > 20:
                            if r_i < len(extracted_reviews):
                                extracted_reviews[r_i]["text"] = cleaned_r
                            else:
                                extracted_reviews.append({
                                    "reviewer_name": f"Verified Customer #{r_i+1}",
                                    "review_source": "Google Maps Verified Review",
                                    "business": b_name,
                                    "text": cleaned_r
                                })
                                
                    gmb_results.append({
                        "platform": "Google Business Profile",
                        "business_name": b_name,
                        "rating": rating,
                        "total_reviews": review_count,
                        "address": address,
                        "phone": phone,
                        "reviews": extracted_reviews
                    })
                    
                except Exception as e:
                    print(f"  [!] Error processing listing #{idx+1}: {e}")
                    
        except Exception as err:
            print(f"  [!] Global GMB scraping error: {err}")
            
        await browser.close()
        
    print(f"Extracted {len(gmb_results)} Google Business Profiles with verified customer reviews.\n")
    return gmb_results
