import os, json, time, re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

# ── SQUADS ──────────────────────────────────────────────
SQUADS = {
  "RR":  ["Shardul Thakur","David Miller","Yashasvi Jaiswal","Arshdeep Singh",
          "Priyansh Arya","Vaibhav Sooryavanshi","Kagiso Rabada","Abhishek Sharma",
          "Sunil Narine","Suyash Sharma","Jamie Overton","Mohammed Siraj",
          "Donovan Ferreira","Riyan Parag","Vijaykumar Vyshak","Mayank Yadav",
          "Nitish Kumar Reddy","Rasikh Salam","Nehal Wadhera","Shashank Singh",
          "Xavier Bartlett","Tristan Stubbs","Shubham Dubey","Ashutosh Sharma","Ashok Sharma"],
  "CSK": ["MS Dhoni","Rashid Khan","Noor Ahmad","Kartik Tyagi","Aiden Markram",
          "Sanju Samson","KL Rahul","Anshul Kamboj","Urvil Patel","Travis Head",
          "Sarfaraz Khan","Heinrich Klaasen","Eshan Malinga","Deepak Chahar",
          "Mohsin Khan","Bhuvneshwar Kumar","Lungi Ngidi","Avesh Khan",
          "Naman Dhir","Nitish Rana","Aniket Verma","Rovman Powell",
          "Rahul Tewatia","Vaibhav Arora","Sandeep Sharma"],
  "MI":  ["Nicholas Pooran","Suryakumar Yadav","Shubman Gill","Sai Sudharsan",
          "Rajat Patidar","Shivam Dube","Mitchell Starc","Angkrish Raghuvanshi",
          "Dewald Brevis","Axar Patel","Yuzvendra Chahal","Jos Buttler",
          "Tim David","Hardik Pandya","Marco Jansen","Corbin Bosch",
          "Jason Holder","Ravindra Jadeja","Marcus Stoinis","Jacob Bethell",
          "Rishabh Pant","Salil Arora","Brijesh Sharma","Suryansh Shedge","Gurjapneet Singh"],
  "RCB": ["Virat Kohli","Shreyas Iyer","Tilak Varma","Devdutt Padikkal",
          "Rinku Singh","Ajinkya Rahane","Prabhsimran Singh","Phil Salt",
          "Cameron Green","Cooper Connolly","Harpreet Brar","Ravi Bishnoi",
          "Varun Chakravarthy","AM Ghazanfar","Harsh Dubey","Prashant Veer",
          "Jofra Archer","Josh Hazlewood","Trent Boult","Prasidh Krishna",
          "T Natarajan","Mukesh Kumar","Mukul Choudhary","Finn Allen","Romario Shepherd"],
  "SRH": ["Shimron Hetmyer","Kuldeep Yadav","Akeal Hosein","Will Jacks",
          "Krunal Pandya","Jitesh Sharma","Ryan Rickelton","Kartik Sharma",
          "Ruturaj Gaikwad","Pat Cummins","Pathum Nissanka","Sameer Rizvi",
          "Mukesh Choudhary","Mohammed Shami","Praful Hinge","Sakib Hussain",
          "Mitchell Santner","Washington Sundar","Dhruv Jurel","Rohit Sharma",
          "Jasprit Bumrah","Prince Yadav","Ishan Kishan","Shivang Kumar","Nandre Burger"]
}

# ── BASELINE (points as of 8 May 2026 from PDF) ─────────
BASELINE = {
  "Shardul Thakur":129.5,"David Miller":111.1,"Yashasvi Jaiswal":284.5,
  "Arshdeep Singh":328.9,"Priyansh Arya":376.8,"Vaibhav Sooryavanshi":499.9,
  "Kagiso Rabada":492.3,"Abhishek Sharma":494.7,"Sunil Narine":332.6,
  "Suyash Sharma":182.6,"Jamie Overton":405.1,"Mohammed Siraj":375.4,
  "Donovan Ferreira":228.2,"Riyan Parag":191.0,"Vijaykumar Vyshak":173.1,
  "Mayank Yadav":-30.5,"Nitish Kumar Reddy":399.1,"Rasikh Salam":125.3,
  "Nehal Wadhera":1.5,"Shashank Singh":158.3,"Xavier Bartlett":140.8,
  "Tristan Stubbs":212.0,"Shubham Dubey":64.1,"Ashutosh Sharma":82.8,"Ashok Sharma":102.8,
  "MS Dhoni":0.0,"Rashid Khan":300.9,"Noor Ahmad":281.7,"Kartik Tyagi":270.6,
  "Aiden Markram":150.3,"Sanju Samson":483.2,"KL Rahul":393.6,"Anshul Kamboj":371.9,
  "Urvil Patel":56.3,"Travis Head":317.1,"Sarfaraz Khan":208.3,"Heinrich Klaasen":373.4,
  "Eshan Malinga":397.7,"Deepak Chahar":36.7,"Mohsin Khan":317.8,
  "Bhuvneshwar Kumar":433.9,"Lungi Ngidi":272.8,"Avesh Khan":97.9,
  "Naman Dhir":212.2,"Nitish Rana":161.3,"Aniket Verma":54.1,
  "Rovman Powell":98.2,"Rahul Tewatia":43.3,"Vaibhav Arora":235.5,"Sandeep Sharma":82.3,
  "Nicholas Pooran":114.8,"Suryakumar Yadav":172.8,"Shubman Gill":337.1,
  "Sai Sudharsan":330.9,"Rajat Patidar":375.8,"Shivam Dube":133.7,
  "Mitchell Starc":107.4,"Angkrish Raghuvanshi":180.4,"Dewald Brevis":38.1,
  "Axar Patel":327.1,"Yuzvendra Chahal":242.4,"Jos Buttler":299.5,
  "Tim David":220.0,"Hardik Pandya":159.1,"Marco Jansen":264.0,
  "Corbin Bosch":86.7,"Jason Holder":199.0,"Ravindra Jadeja":322.4,
  "Marcus Stoinis":146.7,"Jacob Bethell":24.7,"Rishabh Pant":213.9,
  "Salil Arora":52.7,"Brijesh Sharma":163.7,"Suryansh Shedge":70.9,"Gurjapneet Singh":71.0,
  "Virat Kohli":296.5,"Shreyas Iyer":226.3,"Tilak Varma":211.7,
  "Devdutt Padikkal":290.5,"Rinku Singh":220.4,"Ajinkya Rahane":135.8,
  "Prabhsimran Singh":331.9,"Phil Salt":165.3,"Cameron Green":278.5,
  "Cooper Connolly":252.4,"Harpreet Brar":19.6,"Ravi Bishnoi":225.7,
  "Varun Chakravarthy":283.4,"AM Ghazanfar":317.7,"Harsh Dubey":185.7,
  "Prashant Veer":8.9,"Jofra Archer":443.8,"Josh Hazlewood":234.7,
  "Trent Boult":83.1,"Prasidh Krishna":243.9,"T Natarajan":134.0,
  "Mukesh Kumar":175.0,"Mukul Choudhary":159.5,"Finn Allen":110.4,"Romario Shepherd":87.8,
  "Shimron Hetmyer":29.6,"Kuldeep Yadav":197.3,"Akeal Hosein":175.8,
  "Will Jacks":50.2,"Krunal Pandya":312.2,"Jitesh Sharma":-7.2,
  "Ryan Rickelton":361.8,"Kartik Sharma":123.6,"Ruturaj Gaikwad":157.6,
  "Pat Cummins":165.4,"Pathum Nissanka":211.9,"Sameer Rizvi":250.8,
  "Mukesh Choudhary":119.1,"Mohammed Shami":411.0,"Praful Hinge":159.2,
  "Sakib Hussain":196.5,"Mitchell Santner":128.9,"Washington Sundar":184.9,
  "Dhruv Jurel":193.8,"Rohit Sharma":213.3,"Jasprit Bumrah":269.1,
  "Prince Yadav":468.5,"Ishan Kishan":446.6,"Shivang Kumar":189.5,"Nandre Burger":257.6
}

# ── NAME MATCHER ─────────────────────────────────────────
def norm(s):
    return re.sub(r"[^a-z]", "", s.lower())

def match(query, keys):
    q = norm(query)
    for k in keys:
        if norm(k) == q: return k
    for k in keys:
        n = norm(k)
        if q in n or n in q: return k
    return None

# ── SCRAPE ESPN ──────────────────────────────────────────
def scrape():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=opts)

    print("Loading ESPN page...")
    driver.get("https://www.espncricinfo.com/series/ipl-2026-1510719/most-valuable-players")

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
        )
    except:
        print("Timeout waiting for table")

    time.sleep(8)

    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    print(f"Found {len(rows)} rows")

    # Print first 2 rows for debugging
    for i, row in enumerate(rows[:2]):
        cols = row.find_elements(By.TAG_NAME, "td")
        print(f"Row {i}: " + " | ".join(f"[{j}]='{c.text[:20]}'" for j,c in enumerate(cols)))

    live = {}
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) < 3: continue
        # col[0] contains "rank\nPlayer Name" — split on newline
        raw = cols[0].text.strip()
        lines = [l.strip() for l in raw.split("\n") if l.strip()]
        # Find the name line (not a pure number)
        name = next((l for l in lines if not l.isdigit()), None)
        # col[2] = Total Impact
        try:
            pts = float(cols[2].text.strip().split("\n")[0].replace(",",""))
        except:
            continue
        if name:
            live[name] = pts

    driver.quit()
    print(f"Scraped {len(live)} players")
    for n,p in list(live.items())[:5]:
        print(f"  {n}: {p}")
    return live

# ── MAIN ─────────────────────────────────────────────────
def main():
    live = scrape()
    live_keys = list(live.keys())

    results = []
    for team, roster in SQUADS.items():
        total = 0
        players = []
        for player in roster:
            lm = match(player, live_keys)
            cur = live[lm] if lm else 0.0
            bm = match(player, list(BASELINE.keys()))
            base = BASELINE[bm] if bm else 0.0
            net = round(cur - base, 1)
            total += net
            players.append({"name":player,"current":cur,"baseline":base,"net":net})

        players.sort(key=lambda x: x["net"], reverse=True)
        results.append({"team":team,"total":round(total,1),"players":players})

    results.sort(key=lambda x: x["total"], reverse=True)
    for i,r in enumerate(results): r["rank"] = i+1

    out = {
        "updated_at": datetime.now().strftime("%d %b %Y %H:%M IST"),
        "leaderboard": results
    }

    os.makedirs("docs", exist_ok=True)
    with open("docs/data.json","w") as f:
        json.dump(out, f, indent=2)

    print("\n=== LEADERBOARD ===")
    for r in results:
        print(f"  #{r['rank']} {r['team']:5} {r['total']:+.1f}")

if __name__ == "__main__":
    main()
