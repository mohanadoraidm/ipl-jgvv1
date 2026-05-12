import os, json, time, re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime

SQUADS_FILE  = "squads.json"
OUTPUT_JSON  = "docs/data.json"

# ─────────────────────────────────────────────
#  BASELINE: impact points as of 8 May 2026
#  (scraped from your PDF — do NOT edit)
# ─────────────────────────────────────────────
BASELINE = {
    # RR squad
    "Shardul Thakur": 129.5,
    "David Miller": 111.1,
    "Yashasvi Jaiswal": 284.5,
    "Arshdeep Singh": 328.9,
    "Priyansh Arya": 376.8,
    "Vaibhav Suryavanshi": 499.9,
    "Kagiso Rabada": 492.3,
    "Abhishek Sharma": 494.7,
    "Sunil Narine": 332.6,
    "Suyash Sharma": 182.6,
    "Jamie Overton": 405.1,
    "Mohammed Siraj": 375.4,
    "Donovan Ferreira": 228.2,
    "Riyan Parag": 191.0,
    "Vijaykumar Vyshak": 173.1,
    "Mayank Yadav": -30.5,
    "Nitish Kumar Reddy": 399.1,
    "Rasikh Salam": 125.3,
    "Nehal Wadhera": 1.5,
    "Shashank Singh": 158.3,
    "Xavier Bartlett": 140.8,
    "Tristan Stubbs": 212.0,
    "Shubham Dubey": 64.1,
    "Ashutosh Sharma": 82.8,
    "Ashok Sharma": 102.8,
    # CSK squad
    "MS Dhoni": 0.0,
    "Rashid Khan": 300.9,
    "Noor Ahmad": 281.7,
    "Kartik Tyagi": 270.6,
    "Aiden Markram": 150.3,
    "Sanju Samson": 483.2,
    "KL Rahul": 393.6,
    "Anshul Kamboj": 371.9,
    "Urvil Patel": 56.3,
    "Travis Head": 317.1,
    "Sarfaraz Khan": 208.3,
    "Heinrich Klaasen": 373.4,
    "Eshan Malinga": 397.7,
    "Deepak Chahar": 36.7,
    "Mohsin Khan": 317.8,
    "Bhuvneshwar Kumar": 433.9,
    "Lungi Ngidi": 272.8,
    "Avesh Khan": 97.9,
    "Naman Dhir": 212.2,
    "Nitish Rana": 161.3,
    "Aniket Verma": 54.1,
    "Rovman Powell": 98.2,
    "Rahul Tewatia": 43.3,
    "Vaibhav Arora": 235.5,
    "Sandeep Sharma": 82.3,
    # MI squad
    "Nicholas Pooran": 114.8,
    "Suryakumar Yadav": 172.8,
    "Shubman Gill": 337.1,
    "Sai Sudharsan": 330.9,
    "Rajat Patidar": 375.8,
    "Shivam Dube": 133.7,
    "Mitchell Starc": 107.4,
    "Angkrish Raghuvanshi": 180.4,
    "Dewald Brevis": 38.1,
    "Axar Patel": 327.1,
    "Yuzvendra Chahal": 242.4,
    "Jos Buttler": 299.5,
    "Tim David": 220.0,
    "Hardik Pandya": 159.1,
    "Marco Jansen": 264.0,
    "Corbin Bosch": 86.7,
    "Jason Holder": 199.0,
    "Ravindra Jadeja": 322.4,
    "Marcus Stoinis": 146.7,
    "Jacob Bethell": 24.7,
    "Rishabh Pant": 213.9,
    "Salil Arora": 52.7,
    "Brijesh Sharma": 163.7,
    "Suryansh Shedge": 70.9,
    "Gurjapneet Singh": 71.0,
    # RCB squad
    "Virat Kohli": 296.5,
    "Shreyas Iyer": 226.3,
    "Tilak Varma": 211.7,
    "Devdutt Padikkal": 290.5,
    "Rinku Singh": 220.4,
    "Ajinkya Rahane": 135.8,
    "Prabhsimran Singh": 331.9,
    "Phil Salt": 165.3,
    "Cameron Green": 278.5,
    "Cooper Connolly": 252.4,
    "Harpreet Brar": 19.6,
    "Ravi Bishnoi": 225.7,
    "Varun Chakravarthy": 283.4,
    "Allah Ghazanfar": 317.7,
    "Harsh Dubey": 185.7,
    "Prashant Veer": 8.9,
    "Jofra Archer": 443.8,
    "Josh Hazlewood": 234.7,
    "Trent Boult": 83.1,
    "Prasidh Krishna": 243.9,
    "T Natarajan": 134.0,
    "Mukesh Kumar": 175.0,
    "Mukul Choudhary": 159.5,
    "Finn Allen": 110.4,
    "Romario Shepherd": 87.8,
    # SRH squad
    "Shimron Hetmyer": 29.6,
    "Kuldeep Yadav": 197.3,
    "Akeal Hosein": 175.8,
    "Will Jacks": 50.2,
    "Krunal Pandya": 312.2,
    "Jitesh Sharma": -7.2,
    "Ryan Rickelton": 361.8,
    "Kartik Sharma": 123.6,
    "Ruturaj Gaikwad": 157.6,
    "Pat Cummins": 165.4,
    "Pathum Nissanka": 211.9,
    "Sameer Rizvi": 250.8,
    "Mukesh Choudhary": 119.1,
    "Mohammed Shami": 411.0,
    "Praful Hinge": 159.2,
    "Sakib Hussain": 196.5,
    "Mitchell Santner": 128.9,
    "Washington Sundar": 184.9,
    "Dhruv Jurel": 193.8,
    "Rohit Sharma": 213.3,
    "Jasprit Bumrah": 269.1,
    "Prince Yadav": 468.5,
    "Ishan Kishan": 446.6,
    "Shivang Kumar": 189.5,
    "Nandre Burger": 257.6,
}

# ─────────────────────────────────────────────
#  BROWSER SETUP
# ─────────────────────────────────────────────
def make_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    # Selenium 4.10+ auto-detects ChromeDriver — no Service() needed
    return webdriver.Chrome(options=opts)

# ─────────────────────────────────────────────
#  SCRAPE ESPN MVP PAGE
# ─────────────────────────────────────────────
def scrape_espn():
    url = "https://www.espncricinfo.com/series/ipl-2026-1510719/most-valuable-players"
    print("Loading ESPN MVP page...")
    driver = make_driver()
    driver.get(url)

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
        )
    except Exception:
        print("Table wait timed out — proceeding anyway")

    time.sleep(5)

    players = {}
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    print(f"Found {len(rows)} rows")

    # Debug: print first 3 rows to confirm column structure
    for i, row in enumerate(rows[:3]):
        cols = row.find_elements(By.TAG_NAME, "td")
        print(f"Row {i} ({len(cols)} cols): " +
              " | ".join(f"[{j}]='{c.text.strip()[:30]}'" for j, c in enumerate(cols)))

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) < 4:
            continue

        # col[1] contains player name (may include team on second line — take first line only)
        name_raw = cols[1].text.strip().split("\n")[0].strip()

        # col[3] = Total Impact points
        try:
            pts = float(cols[3].text.strip().replace(",", "").split("\n")[0])
        except ValueError:
            continue

        if name_raw and not name_raw.isdigit():
            players[name_raw] = pts

    driver.quit()
    print(f"Scraped {len(players)} players")
    # Print first 5 to verify
    for name, pts in list(players.items())[:5]:
        print(f"  {name}: {pts}")
    return players





# ─────────────────────────────────────────────
#  FUZZY NAME MATCHER
# ─────────────────────────────────────────────
def normalise(s):
    return re.sub(r"[^a-z]", "", s.lower())

def best_match(query, lookup_keys):
    q = normalise(query)
    # 1. exact normalised
    for k in lookup_keys:
        if normalise(k) == q:
            return k
    # 2. one is substring of other
    for k in lookup_keys:
        n = normalise(k)
        if q in n or n in q:
            return k
    # 3. last-name match
    q_last = q[-6:] if len(q) > 6 else q
    for k in lookup_keys:
        if q_last in normalise(k):
            return k
    return None

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    with open(SQUADS_FILE) as f:
        squads_data = json.load(f)
    teams = squads_data["teams"]

    # 1. Get live points from ESPN
    current = scrape_espn()

    # 2. Calculate net points per team (current - baseline)
    team_scores = {}
    team_details = {}

    for team, roster in teams.items():
        total_net = 0.0
        details   = []

        for player in roster:
            # Match player name in live scraped data
            matched_live = best_match(player, current.keys())
            cur_pts = current.get(matched_live, 0.0) if matched_live else 0.0

            # Match player name in our hardcoded baseline
            matched_base = best_match(player, BASELINE.keys())
            base_pts = BASELINE.get(matched_base, 0.0) if matched_base else 0.0

            net = round(cur_pts - base_pts, 2)
            total_net += net

            details.append({
                "name":         player,
                "espn_name":    matched_live or "Not on ESPN yet",
                "current_pts":  round(cur_pts, 2),
                "baseline_pts": round(base_pts, 2),
                "net_pts":      net
            })

        details.sort(key=lambda x: x["net_pts"], reverse=True)
        team_scores[team] = round(total_net, 2)
        team_details[team] = details

    ranked = sorted(team_scores.items(), key=lambda x: x[1], reverse=True)

    output = {
        "updated_at":   datetime.utcnow().strftime("%d %b %Y %H:%M UTC"),
        "auction_date": squads_data["auction_date"],
        "leaderboard":  [
            {"rank": i+1, "team": t, "total_net_pts": s}
            for i, (t, s) in enumerate(ranked)
        ],
        "teams": team_details
    }

    os.makedirs("docs", exist_ok=True)
    with open(OUTPUT_JSON, "w") as f:
        json.dump(output, f, indent=2)

    print("\n===== LEADERBOARD =====")
    for e in output["leaderboard"]:
        sign = "+" if e["total_net_pts"] >= 0 else ""
        print(f"  #{e['rank']}  {e['team']:5}  {sign}{e['total_net_pts']:.1f} pts")
    print(f"\nSaved → {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
