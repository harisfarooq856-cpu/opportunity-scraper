import urllib.request
import urllib.parse
import json
import ssl

def sync_to_opportunity_hunter(prospects, base_url="https://hunter.inceptial.team"):
    """
    Pipes harvested opportunities directly into the Laravel Opportunity Hunter queue.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    endpoint = f"{base_url.rstrip('/')}/campaigns/ingest"
    synced = 0

    print(f"\n📡 Syncing {len(prospects)} harvested prospects to {endpoint} ...")

    for p in prospects:
        try:
            payload = json.dumps(p).encode('utf-8')
            req = urllib.request.Request(endpoint, data=payload, headers={
                'Content-Type': 'application/json',
                'User-Agent': 'OpportunityScraper-Bridge/1.0',
                'Accept': 'application/json'
            })
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                if resp.getcode() in [200, 201, 302]:
                    synced += 1
                    print(f"  ✓ Synced: {p.get('company_name')} ({p.get('opportunity_score', 85)}% Match)")
        except Exception as e:
            print(f"  ⚠️ Sync note for {p.get('company_name', 'Unknown')}: {e}")

    print(f"✨ Successfully synced {synced}/{len(prospects)} targets to Opportunity Hunter queue.\n")
    return synced
