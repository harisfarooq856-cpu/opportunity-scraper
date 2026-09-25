"""
Unified Content & Sentiment Harvester
A production-grade scraping engine for Reddit, Google Business Profiles (GMB), Quora, and LinkedIn.
Bypasses anti-bot defenses using residential proxies and headless browser automation.
"""

from .reddit_engine import harvest_reddit
from .gmb_engine import harvest_gmb
from .quora_engine import harvest_quora
from .linkedin_engine import harvest_linkedin_index, harvest_linkedin_session
from .report_generator import generate_markdown_report, save_json_output

__version__ = "1.1.0"
__all__ = [
    "harvest_reddit",
    "harvest_gmb",
    "harvest_quora",
    "harvest_linkedin_index",
    "harvest_linkedin_session",
    "generate_markdown_report",
    "save_json_output"
]
