"""
Unified Multi-Platform Opportunity & Content Harvester
A production-grade scraping engine for GMB, LinkedIn, Upwork, Facebook, Reddit, and Quora.
Bypasses anti-bot defenses using residential proxies, headless browser automation, and open index harvesting.
"""

from .reddit_engine import harvest_reddit
from .gmb_engine import harvest_gmb
from .quora_engine import harvest_quora
from .linkedin_engine import harvest_linkedin_index, harvest_linkedin_session, harvest_company_decision_makers
from .upwork_engine import harvest_upwork
from .facebook_engine import harvest_facebook
from .report_generator import generate_markdown_report, save_json_output

__version__ = "1.2.0"
__all__ = [
    "harvest_reddit",
    "harvest_gmb",
    "harvest_quora",
    "harvest_linkedin_index",
    "harvest_linkedin_session",
    "harvest_company_decision_makers",
    "harvest_upwork",
    "harvest_facebook",
    "generate_markdown_report",
    "save_json_output"
]
