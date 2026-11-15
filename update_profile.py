"""Rewrites the block between # stats:begin markers in README.md from the GitHub API."""
import json, os, re, urllib.request
from collections import Counter
from datetime import datetime, timezone

USER = "r0sc"

def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}")
    if t := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {t}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)

u = api(f"/users/{USER}")
repos = [r for r in api(f"/users/{USER}/repos?per_page=100&sort=pushed") if not r["fork"]]
langs = Counter(r["language"] for r in repos if r["language"])
stars = sum(r["stargazers_count"] for r in repos)
since = datetime.fromisoformat(u["created_at"].replace("Z", "+00:00"))
days = (datetime.now(timezone.utc) - since).days

lines = [
    f" repos     : {u['public_repos']}",
    f" stars     : {stars}",
    f" followers : {u['followers']}",
    f" following : {u['following']}",
    f" uptime    : {days // 365}y {days % 365 // 30}m",
    f" languages : {', '.join(f'{l} ({n})' for l, n in langs.most_common())}",
    "",
    "r0sc@github:~$ ls -t repos/",
]
for r in repos[:5]:
    desc = f"  # {r['description']}" if r["description"] else ""
    lines.append(f" {r['name']}/{desc}")
lines.append("")
lines.append(f"# updated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC")

block = "# stats:begin\n" + "\n".join(lines) + "\n# stats:end"
text = open("README.md", encoding="utf-8").read()
new = re.sub(r"# stats:begin.*?# stats:end", lambda _: block, text, flags=re.S)
assert new != text or block in text, "markers missing"
open("README.md", "w", encoding="utf-8").write(new)
