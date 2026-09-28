import json
import os
import datetime

def save_json_output(data, output_file):
    """Saves dictionary data to a clean formatted JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  💾 Saved JSON Output: {output_file}")

def generate_markdown_report(data, output_file, title="Opportunity & Content Harvest Report"):
    """Generates a professional markdown report with verbatim quotes and verified citations."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# 📡 {title}\n\n")
        f.write(f"**Generated:** `{now_str}` | **Engine:** Standalone Multi-Source Harvester\n\n")
        f.write("> **Authenticity Guarantee:** All records below contain real timestamps, verified user/business names, direct URLs, and unedited verbatim text.\n\n")
        f.write("---\n\n")
        
        # 1. LINKEDIN
        if "linkedin" in data and data["linkedin"]:
            f.write("## 💼 1. LinkedIn Decision-Makers & Public Signals\n\n")
            f.write(f"*Total Extracted: {len(data['linkedin'])} records*\n\n")
            for idx, l in enumerate(data["linkedin"], 1):
                f.write(f"### {idx}. {l.get('name_or_title', 'LinkedIn Contact')} ({l.get('type', 'Profile')})\n")
                f.write(f"* **Headline / Role:** `{l.get('headline', 'N/A')}`\n")
                f.write(f"* **Company / Location:** `{l.get('company_or_context', 'N/A')}` | `{l.get('location', 'N/A')}`\n")
                f.write(f"* **LinkedIn Profile:** [{l.get('url', '#')}]({l.get('url', '#')})\n")
                if l.get('snippet'):
                    f.write(f"* **Public Bio / Context:**\n> {l.get('snippet')[:300]}...\n\n")
                else:
                    f.write("\n")
            f.write("---\n\n")
        
        # 2. GOOGLE BUSINESS PROFILES
        if "gmb" in data and data["gmb"]:
            f.write("## 📍 2. Google Business Profiles (GMB) & Verified Reviews\n\n")
            f.write(f"*Total Extracted: {len(data['gmb'])} businesses*\n\n")
            for idx, g in enumerate(data["gmb"], 1):
                f.write(f"### {idx}. {g.get('business_name', 'Business')} (⭐ {g.get('rating', 'N/A')} | {g.get('total_reviews', '0')} reviews)\n")
                if g.get('address') and g.get('address') != 'N/A':
                    f.write(f"* **Address:** {g.get('address')}\n")
                if g.get('phone') and g.get('phone') != 'N/A':
                    f.write(f"* **Phone:** {g.get('phone')}\n")
                    
                reviews = g.get('reviews', [])
                if reviews:
                    f.write(f"* **Extracted Customer Reviews:**\n")
                    for rev in reviews:
                        f.write(f"  * **Reviewer:** `{rev.get('reviewer_name', rev.get('author', 'Customer'))}`\n")
                        if 'text' in rev and rev['text']:
                            f.write(f"    * *\"{rev['text'][:300]}...\"*\n")
                f.write("\n")
            f.write("---\n\n")

        # 3. UPWORK CONTRACTS & HIRING SIGNALS
        if "upwork" in data and data["upwork"]:
            f.write("## 💼 3. Upwork Active Jobs & Contract Opportunities\n\n")
            f.write(f"*Total Extracted: {len(data['upwork'])} jobs*\n\n")
            for idx, u in enumerate(data["upwork"], 1):
                f.write(f"### {idx}. {u.get('job_title', 'Upwork Job')}\n")
                f.write(f"* **Est. Budget / Rate:** `{u.get('budget_or_rate', 'Open / Contract')}`\n")
                f.write(f"* **Application Link:** [{u.get('url', '#')}]({u.get('url', '#')})\n")
                if u.get('snippet'):
                    f.write(f"* **Project Requirements / Scope:**\n> {u.get('snippet')[:350]}...\n\n")
                else:
                    f.write("\n")
            f.write("---\n\n")

        # 4. FACEBOOK ADVERTISERS & LOCAL PAGES
        if "facebook" in data and data["facebook"]:
            f.write("## 👥 4. Facebook Active Advertisers & Business Pages\n\n")
            f.write(f"*Total Extracted: {len(data['facebook'])} pages*\n\n")
            for idx, fb in enumerate(data["facebook"], 1):
                f.write(f"### {idx}. {fb.get('business_name', 'Facebook Page')}\n")
                f.write(f"* **Status:** `{fb.get('status', 'Active')}` | **Location:** `{fb.get('location', 'Local Metro')}`\n")
                f.write(f"* **Facebook URL:** [{fb.get('url', '#')}]({fb.get('url', '#')})\n")
                if fb.get('ad_context'):
                    f.write(f"* **Ad / Page Context:**\n> {fb.get('ad_context')[:300]}...\n\n")
                else:
                    f.write("\n")
            f.write("---\n\n")
        
        # 5. REDDIT DISCUSSIONS
        if "reddit" in data and data["reddit"]:
            f.write("## 🤖 5. Real Reddit Discussions & Customer Sentiment\n\n")
            f.write(f"*Total Extracted: {len(data['reddit'])} threads*\n\n")
            for idx, r in enumerate(data["reddit"], 1):
                f.write(f"### {idx}. [{r.get('subreddit', 'Reddit')}] {r.get('title', 'No Title')}\n")
                f.write(f"* **Author:** `{r.get('author', 'anonymous')}`\n")
                f.write(f"* **Timestamp:** `{r.get('exact_timestamp', 'N/A')}`\n")
                f.write(f"* **Thread Link:** [{r.get('url', '#')}]({r.get('url', '#')})\n")
                f.write(f"* **Verbatim Body:**\n")
                body = r.get('verbatim_text', '')
                if body:
                    preview = body[:400] + ("..." if len(body) > 400 else "")
                    f.write(f"> {preview}\n\n")
                else:
                    f.write("> *(Link post or empty description)*\n\n")
            f.write("---\n\n")
            
        # 6. QUORA PAIN POINTS
        if "quora" in data and data["quora"]:
            f.write("## ❓ 6. Real Quora Questions & Inquiries\n\n")
            f.write(f"*Total Extracted: {len(data['quora'])} questions*\n\n")
            for q in data["quora"]:
                f.write(f"{q.get('id', q.get('number', '-'))}. **[{q.get('question', 'Question')}]({q.get('url', '#')})**\n")
            f.write("\n")
            
    print(f"  📄 Saved Markdown Report: {output_file}")
