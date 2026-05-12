import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def scrape_and_update():
    print("Starting Chrome...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)

    print("Loading ESPNcricinfo...")
    url = "https://www.espncricinfo.com/series/ipl-2026-1510719/most-valuable-players"
    driver.get(url)
    time.sleep(15)

    print("Extracting data...")
    extracted_data = [["Player Name", "Total Impact Points"]]

    rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
    print(f"Found {len(rows)} players!")

    for row in rows:
        columns = row.find_elements(By.TAG_NAME, "td")
        if len(columns) >= 2:
            player_name = columns[0].text          # e.g. "1\nBhuvneshwar Kumar"
            impact_points = columns[2].text        # e.g. "578.3"
            extracted_data.append([player_name, impact_points])

    driver.quit()

    print("Connecting to Google Sheets...")
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    google_creds_json = os.getenv('GOOGLE_CREDENTIALS')
    if google_creds_json:
        print("Using GitHub Secret...")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            json.loads(google_creds_json), scope)
    else:
        print("Using local credentials.json...")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            os.path.join(script_dir, "credentials.json"), scope)

    client = gspread.authorize(creds)
    sheet = client.open("ipl auction 2026").worksheet("Sheet1")

    print("Uploading...")
    sheet.clear()
    sheet.update('A1', extracted_data)
    print("Done! Google Sheet updated.")

if __name__ == "__main__":
    scrape_and_update()
