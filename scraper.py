import os, json, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

SQUADS_FILE = "squads.json"
BASELINE_FILE = "baseline_points.json"
OUTPUT_JSON  = "docs/data.json"

# ---------- browser ----------
def make_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36")
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=opts)

# ---------- scrape ESPN MVP page ----------
def scrape_espn():
    url = "https://www.espncricinfo.com/series/ipl-2026-1510719/most-valuable-players"
    print(f"Loading {url}")
    driver = make_driver()
    driver.get(url)

    # wait for the table to appear (up to 30 s)
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
        )
    except Exception:
        print("Timed out waiting for table — trying anyway")

    time.sleep(3)   # extra buffer for lazy-loaded rows

    players = {}
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    print(f"Found {len(rows)} rows")

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) < 2:
            continue
        # col 0 = rank, col 1 = player name+team, col 2 = total impact
        name_raw = cols[1].text.strip().split("\n")[0]   # first line is name
        try:
            pts = float(cols[2].text.strip().replace(",", ""))
        except ValueError:
            continue
        if name_raw:
            players[name_raw] = pts

    driver.quit()
    print(f"Scraped {len(players)} players")
    return players

# ---------- name matcher (fuzzy) ----------
def normalise(s):
    import re
    return re.sub(r"[^a-z]", "", s.lower())

def best_match(query, lookup):
    q = normalise(query)
    # exact normalised match
    for name in lookup:
        if normalise(name) == q:
            return name
    # substring: query inside name OR name inside query
    for name in lookup:
        n = normalise(name)
        if q in n or n in q:
            return name
    return None

# ---------- main ----------
def main():
    # load squads
    with open(SQUADS_FILE) as f:
        squads_data = json.load(f)
    teams = squads_data["teams"]

    # scrape current points
    current = scrape_espn()

    # ---- baseline handling ----
    # baseline_points.json stores each player's points as of auction day.
    # On first run it is created from the current scrape.
    # After that it is never overwritten automatically.
    if not os.path.exists(BASELINE_FILE):
        print("First run — saving baseline points (today = auction day)")
        with open(BASELINE_FILE, "w") as f:
            json.dump(current, f, indent=2)
        baseline = current
    else:
        with open(BASELINE_FILE) as f:
            baseline = json.load(f)

    # ---- calculate net points per team ----
    team_scores = {}
    team_details = {}

    for team, roster in teams.items():
        total_net = 0.0
        details = []
        for player in roster:
            # find player in scraped data
            matched = best_match(player, current.keys())
            cur_pts  = current.get(matched, 0.0)  if matched else 0.0

            # baseline: find same player in baseline
            bmatched  = best_match(player, baseline.keys())
            base_pts = baseline.get(bmatched, 0.0) if bmatched else 0.0

            net = round(cur_pts - base_pts, 2)
            total_net += net
            details.append({
                "name": player,
                "espn_name": matched or "—",
                "current_pts": round(cur_pts, 2),
                "baseline_pts": round(base_pts, 2),
                "net_pts": net
            })

        details.sort(key=lambda x: x["net_pts"], reverse=True)
        team_scores[team] = round(total_net, 2)
        team_details[team] = details

    # rank teams
    ranked = sorted(team_scores.items(), key=lambda x: x[1], reverse=True)

    output = {
        "updated_at": datetime.utcnow().strftime("%d %b %Y %H:%M UTC"),
        "auction_date": squads_data["auction_date"],
        "leaderboard": [
            {"rank": i+1, "team": t, "total_net_pts": s}
            for i, (t, s) in enumerate(ranked)
        ],
        "teams": team_details
    }

    os.makedirs("docs", exist_ok=True)
    with open(OUTPUT_JSON, "w") as f:
        json.dump(output, f, indent=2)

    print("\n===== LEADERBOARD =====")
    for entry in output["leaderboard"]:
        print(f"  #{entry['rank']}  {entry['team']:6}  {entry['total_net_pts']:>8.2f} pts")
    print(f"\nSaved → {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
