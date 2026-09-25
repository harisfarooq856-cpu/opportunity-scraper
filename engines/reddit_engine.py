import re
import urllib.parse
import xml.etree.ElementTree as ET
import requests
from .config import REQUESTS_PROXIES, USER_AGENT

def harvest_reddit(subreddits=None, queries=None, limit_per_sub=10, use_proxy=True):
    """
    Harvests authentic Reddit posts and threads via open Atom RSS feeds.
    Extracts verbatim text, exact ISO timestamps, author usernames, and live URLs.
    """
    if subreddits is None:
        subreddits = ["rva", "HVAC"]
    if queries is None:
        queries = ["HVAC repair", "AC replacement", "furnace install"]
        
    print("\n" + "=" * 65)
    print(" 🤖 HARVESTING REDDIT (Authentic Threads & Timestamps)")
    print("=" * 65)
    
    results = []
    seen_urls = set()
    proxies = REQUESTS_PROXIES if use_proxy else None
    
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/atom+xml,application/xml,text/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    for sub in subreddits:
        for q in queries:
            rss_url = f"https://www.reddit.com/r/{sub}/search.rss?q={urllib.parse.quote_plus(q)}&restrict_sr=1&sort=new"
            print(f"Fetching: r/{sub} | Query: '{q}' ...")
            
            try:
                res = requests.get(rss_url, headers=headers, proxies=proxies, timeout=15)
                
                # Fallback to direct if proxy fails or returns unexpected code
                if res.status_code != 200 and use_proxy:
                    print(f"  [!] HTTP {res.status_code} via proxy, attempting direct connection...")
                    res = requests.get(rss_url, headers=headers, timeout=15)
                    
                if res.status_code != 200:
                    print(f"  [!] Failed to fetch r/{sub} (HTTP {res.status_code})")
                    continue
                    
                root = ET.fromstring(res.text)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                entries = root.findall('atom:entry', ns)
                
                added_count = 0
                for entry in entries:
                    if added_count >= limit_per_sub:
                        break
                        
                    title_el = entry.find('atom:title', ns)
                    link_el = entry.find('atom:link', ns)
                    updated_el = entry.find('atom:updated', ns)
                    author_el = entry.find('atom:author/atom:name', ns)
                    content_el = entry.find('atom:content', ns)
                    
                    title = title_el.text.strip() if title_el is not None and title_el.text else ""
                    link = link_el.get('href') if link_el is not None else ""
                    date_iso = updated_el.text.strip() if updated_el is not None and updated_el.text else ""
                    author = author_el.text.replace('/u/', '').strip() if author_el is not None and author_el.text else "anonymous"
                    
                    raw_html = content_el.text if content_el is not None and content_el.text else ""
                    clean_text = re.sub('<[^<]+?>', ' ', raw_html)
                    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                    clean_text = clean_text.replace('&amp;', '&').replace('&quot;', '"').replace('&#39;', "'")
                    
                    if link and link not in seen_urls:
                        seen_urls.add(link)
                        item = {
                            "platform": "Reddit",
                            "subreddit": f"r/{sub}",
                            "title": title,
                            "author": f"u/{author}",
                            "exact_timestamp": date_iso,
                            "url": link,
                            "verbatim_text": clean_text
                        }
                        results.append(item)
                        added_count += 1
                        print(f"  -> [{date_iso[:10]}] u/{author}: {title[:65]}...")
                        
            except Exception as e:
                print(f"  [!] Error parsing r/{sub} ('{q}'): {e}")
                
    print(f"Extracted {len(results)} authentic Reddit posts.\n")
    return results
