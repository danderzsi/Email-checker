import re, subprocess, os, csv

INPUT = "emails.csv"
OUTPUT = "infoemails.csv"
FIND_EMAILS = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

def has_mx(domain: str) -> bool:
    out = subprocess.run(["nslookup", "-type=mx", domain],
                         capture_output=True, text=True)
    return "mail exchanger" in out.stdout.lower()

def has_a(domain: str) -> bool:
    out = subprocess.run(["nslookup", "-type=a", domain],
                         capture_output=True, text=True)
    return "address" in out.stdout.lower()

if not os.path.exists(INPUT):
    raise SystemExit(f"Missing file: {INPUT}")

raw = open(INPUT, encoding="utf-8", errors="ignore").read()
emails = sorted(set(e.lower().rstrip(",") for e in FIND_EMAILS.findall(raw)))

rows = []
ok_mx = ok_a = bad = 0
for e in emails:
    dom = e.split("@", 1)[1]
    if has_mx(dom):
        res = "OK (MX)"; ok_mx += 1
    elif has_a(dom):
        res = "OK (A-only)"; ok_a += 1
    else:
        res = "BAD (no DNS)"; bad += 1
    rows.append((e, dom, res))

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["email","domain","result"]); w.writerows(rows)

print(f"Wrote {OUTPUT}")
print(f"OK (MX): {ok_mx} | OK (A-only): {ok_a} | BAD (no DNS): {bad}")
