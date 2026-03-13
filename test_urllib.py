import urllib.request
import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
urls = [
    "https://hoininsight-commits.github.io/hoininsight/data/ops/investment_os_brief.md",
    "https://hoininsight-commits.github.io/hoininsight/data/decision/manifest.json"
]
for u in urls:
    print(f"Fetching {u}...")
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            print(resp.getcode())
    except Exception as e:
        print(f"Exception: {e}")
