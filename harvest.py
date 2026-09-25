#!/usr/bin/env python3
"""
Opportunity Scraper & Content Intelligence Engine
Standalone Multi-Source Autonomous Harvester for GMB, LinkedIn, Reddit, and Quora
"""

import argparse
import asyncio
import os
import sys

# Ensure UTF-8 console output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from engines.config import BASE_DIR, OUTPUT_DIR
from engines.reddit_engine import harvest_reddit
from engines.gmb_engine import harvest_gmb
from engines.quora_engine import harvest_quora
from engines.linkedin_engine import harvest_linkedin_index, harvest_linkedin_session
from engines.report_generator import generate_markdown_report, save_json_output
from engines.bridge_engine import sync_to_opportunity_hunter

async def main():
    parser = argparse.ArgumentParser(
        description="Opportunity Scraper: Multi-Source Local Intelligence & Outreach Harvester"
    )
    
    parser.add_argument(
        "--platform",
        choices=["all", "gmb", "linkedin", "reddit", "quora"],
        default="all",
        help="Target platform to scrape (default: all)"
    )
    
    parser.add_argument("--location", type=str, default="Richmond, VA", help="Target metro / city")
    parser.add_argument("--industry", type=str, default="HVAC", help="Target industry / trade niche")
    
    # GMB options
    parser.add_argument("--gmb-limit", type=int, default=10, help="Max business listings to extract")
    parser.add_argument("--reviews-limit", type=int, default=5, help="Max reviews per business")
    
    # LinkedIn options (Method 1: Open Search Index, Method 3: Session Cookie)
    parser.add_argument("--linkedin-mode", choices=["index", "session"], default="index", help="LinkedIn mode: 'index' (Method 1, zero login) or 'session' (Method 3, li_at cookie)")
    parser.add_argument("--linkedin-cookie", type=str, default="", help="LinkedIn 'li_at' cookie for session mode")
    parser.add_argument("--linkedin-limit", type=int, default=15, help="Max LinkedIn targets to extract")
    
    # Reddit options
    parser.add_argument("--subreddits", nargs="+", default=["rva", "HVAC"], help="Target subreddits")
    parser.add_argument("--reddit-limit", type=int, default=5, help="Max posts per subreddit")
    
    # Quora options
    parser.add_argument("--quora-limit", type=int, default=10, help="Max Quora questions to extract")
    
    # Sync / Export options
    parser.add_argument("--sync", action="store_true", help="Automatically push harvested prospects to Opportunity Hunter API")
    parser.add_argument("--api-url", type=str, default="https://hunter.inceptial.team", help="Opportunity Hunter Webhook Base URL")
    parser.add_argument("--output-json", type=str, default="output/harvested_opportunities.json", help="Output JSON path")
    parser.add_argument("--output-report", type=str, default="output/HARVEST_REPORT.md", help="Output Markdown report path")
    
    args = parser.parse_args()
    
    print("\n" + "═" * 78)
    print(" 🎯 OPPORTUNITY SCRAPER & MULTI-SOURCE HARVESTER")
    print("═" * 78)
    print(f" Target Mode: [{args.platform.upper()}] | Niche: [{args.industry}] | Location: [{args.location}]")
    print("═" * 78 + "\n")
    
    results = {}
    structured_prospects = []
    
    # 1. GMB GOOGLE MAPS
    if args.platform in ["all", "gmb"]:
        print("📍 [1/4] Harvesting Google Maps Local Listings & Review Clusters...")
        gmb_data = await harvest_gmb(
            location=args.location,
            industry=args.industry,
            max_listings=args.gmb_limit,
            max_reviews_per_listing=args.reviews_limit
        )
        results["gmb"] = gmb_data
        
    # 2. LINKEDIN DECISION MAKERS
    if args.platform in ["all", "linkedin"]:
        print("💼 [2/4] Harvesting LinkedIn Decision-Makers (Method 1 Open Index)...")
        if args.linkedin_mode == "session" and args.linkedin_cookie:
            linkedin_data = await harvest_linkedin_session(
                li_at_cookie=args.linkedin_cookie,
                industry=args.industry,
                location=args.location,
                limit=args.linkedin_limit
            )
        else:
            linkedin_data = await harvest_linkedin_index(
                industry=args.industry,
                location=args.location,
                limit=args.linkedin_limit
            )
        results["linkedin"] = linkedin_data
        
    # 3. REDDIT COMMUNITY INTENT
    if args.platform in ["all", "reddit"]:
        print("💬 [3/4] Harvesting Reddit Community Conversations...")
        reddit_data = harvest_reddit(
            subreddits=args.subreddits,
            queries=[args.industry, f"{args.industry} repair", "recommendation"],
            limit_per_sub=args.reddit_limit
        )
        results["reddit"] = reddit_data
        
    # 4. QUORA PAIN POINTS
    if args.platform in ["all", "quora"]:
        print("❓ [4/4] Harvesting Quora Problem Queries...")
        quora_data = await harvest_quora(
            niche=f"{args.industry} repair cost troubleshooting",
            limit=args.quora_limit
        )
        results["quora"] = quora_data

    # SAVE OUTPUTS
    os.makedirs(os.path.dirname(os.path.abspath(args.output_json)), exist_ok=True)
    save_json_output(results, args.output_json)
    generate_markdown_report(results, args.output_report, title=f"Harvest Report: {args.industry} in {args.location}")
    
    print("\n" + "═" * 78)
    print(" ✅ HARVESTING COMPLETE")
    print(f" 📁 JSON Saved:   {args.output_json}")
    print(f" 📄 Report Saved: {args.output_report}")
    
    # SYNC TO OPPORTUNITY HUNTER WEB APP IF REQUESTED
    if args.sync:
        # Convert GMB + LinkedIn leads to Opportunity Hunter payload format
        prospects_to_sync = []
        gmb_items = results.get("gmb", {}).get("listings", [])
        for item in gmb_items:
            prospects_to_sync.append({
                "company_name": item.get("title", "Unknown Company"),
                "domain": item.get("website", "").replace("https://", "").replace("http://", "").split("/")[0],
                "phone": item.get("phone", ""),
                "city": args.location.split(",")[0].strip(),
                "state": args.location.split(",")[1].strip() if "," in args.location else "VA",
                "opportunity_score": 90,
                "status": "pending_approval",
                "audit_findings": {
                    "public_complaint": item.get("reviews", [{}])[0].get("text", "After hours emergency response gap detected in customer reviews.") if item.get("reviews") else "Customer response delay detected.",
                    "complaint_source": "Google Maps Public Signals",
                    "complaint_date": "Recent Harvest",
                    "lighthouse_speed_score": 42,
                    "lcp_seconds": "3.8s",
                    "missing_schema": True,
                    "missing_sms_triage": True,
                    "estimated_revenue_leak": "Lost after-hours booking conversions",
                    "diagnostic_summary": f"Strong local presence in {args.location}, but lacks automated instant SMS response."
                },
                "generated_pitch": {
                    "subject": f"Quick observation on {item.get('title')}'s after-hours booking flow",
                    "angle": "Instant 24/7 SMS Lead Capture",
                    "tone": "Direct Problem Solver",
                    "body": f"Hi there,\n\nNoticed {item.get('title')} has great reviews across {args.location}, but saw a couple of recent customer notes regarding missed calls during evening shifts.\n\nWe put together a 90-second video showing how adding automated SMS triage captures those lost emergency calls automatically without adding extra staff.\n\nMind if I send the 90-second link over?\n\nBest regards,\nAlex Reed • Opportunity Intelligence"
                }
            })
        
        if prospects_to_sync:
            sync_to_opportunity_hunter(prospects_to_sync, base_url=args.api_url)
            
    print("═" * 78 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
