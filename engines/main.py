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

from .config import BASE_DIR, OUTPUT_DIR
from .reddit_engine import harvest_reddit
from .gmb_engine import harvest_gmb
from .quora_engine import harvest_quora
from .linkedin_engine import harvest_linkedin_index, harvest_linkedin_session
from .report_generator import generate_markdown_report, save_json_output

async def run_cli():
    parser = argparse.ArgumentParser(
        description="Unified Content & Opportunity Harvester: Reddit, GMB, Quora & LinkedIn Engine"
    )
    
    parser.add_argument(
        "--platform",
        choices=["all", "reddit", "gmb", "quora", "linkedin"],
        default="all",
        help="Target platform to scrape (default: all)"
    )
    
    # Common filters
    parser.add_argument("--location", type=str, default="Richmond, VA", help="Target city / region")
    parser.add_argument("--industry", type=str, default="HVAC", help="Target niche / industry")
    
    # Reddit options
    parser.add_argument("--subreddits", nargs="+", default=["rva", "HVAC"], help="List of subreddits to search")
    parser.add_argument("--reddit-queries", nargs="+", default=["HVAC", "AC repair", "heat pump"], help="Reddit search queries")
    parser.add_argument("--reddit-limit", type=int, default=5, help="Max posts per subreddit")
    parser.add_argument("--no-proxy", action="store_true", help="Disable residential proxy for Reddit")
    
    # GMB options
    parser.add_argument("--gmb-limit", type=int, default=5, help="Max business listings to inspect")
    parser.add_argument("--reviews-limit", type=int, default=5, help="Max reviews per business")
    
    # Quora options
    parser.add_argument("--quora-query", type=str, default="HVAC repair cost replacement questions", help="Quora search query")
    parser.add_argument("--quora-limit", type=int, default=15, help="Max Quora questions to extract")
    
    # LinkedIn options (Method 1 & Method 3)
    parser.add_argument("--linkedin-mode", choices=["index", "session"], default="index", help="LinkedIn extraction mode: 'index' (Method 1, zero login) or 'session' (Method 3, li_at cookie)")
    parser.add_argument("--linkedin-cookie", type=str, default="", help="LinkedIn 'li_at' cookie for Method 3")
    parser.add_argument("--linkedin-limit", type=int, default=15, help="Max LinkedIn profiles/posts to extract")
    parser.add_argument("--linkedin-intent", type=str, default="", help="Search query for buying intent posts (optional)")
    
    # Output options
    parser.add_argument("--output-json", type=str, default="harvest_authentic_data.json", help="Output JSON filename")
    parser.add_argument("--output-report", type=str, default="HARVEST_AUTHENTIC_DATA_REPORT.md", help="Output Markdown report filename")
    parser.add_argument("--report-title", type=str, default="Content Intelligence & Sentiment Harvest Report", help="Report Title")
    
    args = parser.parse_args()
    
    data = {}
    
    print("\n" + "═" * 75)
    print(" 🚀 UNIFIED OPPORTUNITY & CONTENT HARVESTER — PRODUCTION ENGINE")
    print("═" * 75)
    print(f" Target Mode: [{args.platform.upper()}] | Niche: [{args.industry}] | Loc: [{args.location}]")
    
    # 1. Reddit
    if args.platform in ["all", "reddit"]:
        reddit_data = harvest_reddit(
            subreddits=args.subreddits,
            queries=args.reddit_queries,
            limit_per_sub=args.reddit_limit,
            use_proxy=not args.no_proxy
        )
        data["reddit"] = reddit_data
        
    # 2. GMB Google Maps
    if args.platform in ["all", "gmb"]:
        gmb_data = await harvest_gmb(
            location=args.location,
            industry=args.industry,
            max_listings=args.gmb_limit,
            max_reviews_per_listing=args.reviews_limit
        )
        data["gmb"] = gmb_data
        
    # 3. Quora
    if args.platform in ["all", "quora"]:
        quora_data = await harvest_quora(
            niche=args.quora_query,
            limit=args.quora_limit
        )
        data["quora"] = quora_data
        
    # 4. LinkedIn (Method 1 & Method 3)
    if args.platform in ["all", "linkedin"]:
        if args.linkedin_mode == "session" and args.linkedin_cookie:
            linkedin_data = await harvest_linkedin_session(
                li_at_cookie=args.linkedin_cookie,
                limit=args.linkedin_limit
            )
        else:
            linkedin_data = await harvest_linkedin_index(
                industry=args.industry,
                location=args.location,
                intent_query=args.linkedin_intent if args.linkedin_intent else None,
                limit=args.linkedin_limit
            )
        data["linkedin"] = linkedin_data
        
    # Save Outputs
    json_full_path = os.path.join(OUTPUT_DIR, args.output_json)
    report_full_path = os.path.join(OUTPUT_DIR, args.output_report)
    
    print("\n" + "═" * 75)
    print(" 📊 GENERATING HARVEST REPORTS & EXPORTS")
    print("═" * 75)
    save_json_output(data, json_full_path)
    generate_markdown_report(data, report_full_path, title=args.report_title)
    
    print("\n" + "═" * 75)
    print(" ✅ HARVEST COMPLETE & VERIFIED!")
    print(f" • JSON Data:   {json_full_path}")
    print(f" • MD Report:   {report_full_path}")
    print("═" * 75 + "\n")

def main():
    asyncio.run(run_cli())

if __name__ == "__main__":
    main()
