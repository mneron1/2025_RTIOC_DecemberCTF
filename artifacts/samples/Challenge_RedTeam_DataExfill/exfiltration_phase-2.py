import requests
from bs4 import BeautifulSoup

BASE = "https://cybersecurity-space-fe-ores.chals.io"
COOKIES = {
    "session": "eYPQkUy9qtfl-b8Jw9-0Ekcub_oYGxbJmZqOIRGU_10.mOWPHnxcsZzfCPWT3GPiqi1Flq8"
}

def check_page(page: int):
    params = {
        "page": page,
        "date": "",
        "name": "",
        "department": "",
        "amount": "",
    }
    r = requests.get(f"{BASE}/finance", params=params, cookies=COOKIES)
    r.raise_for_status()

    if "flag{" in r.text:
        print(f"[!!!] Possible flag on page {page}")
        # Save raw HTML so you can inspect it
        with open(f"finance_page_{page}.html", "w", encoding="utf-8") as f:
            f.write(r.text)
        return True

    # Also stop if there’s no data table anymore
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", class_="table")
    if not table or not table.find("tbody"):
        return False

    rows = table.find("tbody").find_all("tr")
    # Only the filter row = no data
    real_rows = [tr for tr in rows if not tr.find("input")]
    if not real_rows:
        return False

    return True

def main():
    page = 1
    while True:
        print(f"[*] Checking page {page}")
        has_data = check_page(page)
        if not has_data:
            print(f"[!] No more data on page {page}, stopping.")
            break
        page += 1
        if page > 200:
            print("[!] Safety stop at page 200.")
            break

if __name__ == "__main__":
    main()
