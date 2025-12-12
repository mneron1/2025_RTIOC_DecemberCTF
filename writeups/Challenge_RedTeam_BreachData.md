# 🧩 **Red Team Path | Challenge - Breach Data**

> 🏷️ *Category:* **Web / OSINT / Password Cracking**
> ⚙️ *Difficulty:* **Medium**
> 🕵️ *Author:* **cybersecurity.ctfd.io**
> 🧠 *Concepts:* OSINT, MD5 hash cracking, credential stuffing, breached data

---

## 📜 Challenge Description

> 💬
> As a part of the information gathering phase, we've created a profile for the Space Fe-Ores company (`osint.txt`) and procured a copy of past breach information thanks to some friends at Titan Shadows.
>
> Use the information provided, as well as what is in our private breached credentials list (`BreachData.txt`), to try and find a valid username/password pair to login to the company website.
>
> **Flag format:** `flag{example_flag}`
>
> `https://cybersecurity-space-fe-ores.chals.io/`

---

## 📦 Provided Files / Data

| 📁 File / Variable     | 🔍 Description                                       | 💾 Value |
| ---------------------- | ---------------------------------------------------- | -------- |
| `osint.txt`            | OSINT profile of Space Fe-Ores                       | —        |
| `2023BreachData.txt`   | 2023 breach dump (partial plaintext + MD5 hashes)    | —        |
| `BreachData.txt`       | Large “Titan Shadows” breach list (email:MD5 pairs)  | —        |
| `ProjectCodenames.txt` | Internal project names (TITAN, AURORA, etc.)         | —        |
| `DroneTelemetry.log`   | Drone logs (red herring for this specific challenge) | —        |

---

## 🧠 Understanding the Problem

🕵️‍♂️ We’re given:

* An **OSINT profile** of the company.
* Two different **breach datasets** involving employee accounts.
* A **live company website** with a login portal.

The task is to:

> Use the OSINT + breach data to find **one valid username/password pair** that still works on the production website and log in to retrieve the flag.

So this is really about:

* Recognizing **corporate email patterns** (`@spacefeore.com`).
* Correlating **multiple breaches**.
* **Cracking MD5 hashes** to recover a working password.
* Using the recovered credentials in a typical **credential stuffing** style attack against the target login form.

---

## 🧩 Step-by-Step Solution

### 🔹 Step 1: Initial Observation

First, I read through `osint.txt`:

* It describes the Space Fe-Ores company, some leadership roles (including **CFO Sophia Bennett**) and general business context.
* It also mentions a **March 2023 breach** where ~25 employee accounts were compromised and passwords were rotated afterward.

Next, I inspected the breach-related files:

1. `2023BreachData.txt`

   * Contains about 25 `spacefeore.com` users.
   * Some entries are **plaintext passwords**, others are **MD5 hashes**.
   * This confirms that passwords in these breaches are stored in **unsalted MD5**.

2. `BreachData.txt`

   * A large generic breach list (lots of different domains).
   * Importantly, it also contains some `@spacefeore.com` addresses mixed in with everyone else.
   * One of them is:

     ```text
     sophia.bennett@spacefeore.com:64a3599377c379028f94f2b1d481ed2b
     ```



Given the challenge description, the most promising path is to:

> Filter out **Space Fe-Ores employees** in `BreachData.txt`, crack their MD5 hashes, and test those credentials on the live login.

---

### 🔹 Step 2: Extract the Relevant Corporate Accounts

From `BreachData.txt`, I grepped for `@spacefeore.com`:

```bash
grep "spacefeore.com" BreachData.txt
```

Among the results, one particularly interesting line is:

```text
sophia.bennett@spacefeore.com:64a3599377c379028f94f2b1d481ed2b
```

Why Sophia?

* `osint.txt` mentions **Sophia Bennett** as the **CFO** (high-value account).
* The hash is **MD5**, consistent with the encoding in `2023BreachData.txt`.
* High-value users are often juicy targets and more likely to appear in curated “private” breach lists like Titan Shadows.

So we decide to target this hash:

```text
64a3599377c379028f94f2b1d481ed2b
```

---

### 🔹 Step 3: Crack the MD5 Hash

I then attempted to crack the MD5 hash using a standard wordlist / cracking workflow (e.g., `hashcat` or `john` with a common wordlist):

```bash
# hashcat example
echo "64a3599377c379028f94f2b1d481ed2b" > sophia_hash.txt
hashcat -m 0 -a 0 sophia_hash.txt /path/to/rockyou.txt
```

After running the attack, the hash resolved to:

```text
64a3599377c379028f94f2b1d481ed2b:ILoveSpace
```

So we now have:

* **Username:** `sophia.bennett@spacefeore.com`
* **Password:** `ILoveSpace`

This gives us a **likely valid login pair** for the Space Fe-Ores website.

---

### 🔹 Step 4: Log Into the Website

We head to the challenge URL:

```text
https://cybersecurity-space-fe-ores.chals.io/
```

Then:

1. Navigate to the **Login** page.
2. Enter the recovered credentials:

   * **Email / Username:** `sophia.bennett@spacefeore.com`
   * **Password:** `ILoveSpace`
3. Submit the form.

The login succeeds and we are redirected to the authenticated area (e.g., a dashboard or internal page) where the **flag is displayed**.

---

### 🔹 Step 5: Recover the Flag

On the logged-in page, the challenge flag is shown in the standard format:

<details>
<summary>🎯 <b>Click to Reveal the Flag</b></summary>

```text
flag{REPLACE_WITH_REAL_FLAG_FROM_DASHBOARD}
```

</details>

> 📝 **Note:** Replace the placeholder above with the actual flag string you saw on the site when you solved it.

---

## 📘 Explanation — *Why It Works*

💡 **In short:**

* The company experienced **multiple breaches**:

  * `2023BreachData.txt` showed that Space Fe-Ores credentials had leaked before.
  * `BreachData.txt` is a “private” breach corpus used by Titan Shadows that still contains valid hashes for corporate users.
* By focusing on **corporate domains** (`@spacefeore.com`), we filtered out the noise from thousands of unrelated accounts.
* We then **cracked a single MD5 hash** (`64a3599377c379028f94f2b1d481ed2b`) associated with **CFO Sophia Bennett**, recovering the plaintext password `ILoveSpace`.
* That password still worked on the production login portal, allowing us to **stuff** the recovered credentials into the web application and authenticate successfully.

This is a textbook demonstration of:

> How **password reuse** + **unsalted MD5** + **breach aggregation** can turn an old leak into an active compromise.

---

## 🧰 Tools & Techniques Used

| 🧩 Tool / Language        | 💡 Purpose                                    |
| ------------------------- | --------------------------------------------- |
| `grep` / text editor      | Filter `@spacefeore.com` emails from breaches |
| `hashcat` / `john`        | Crack the MD5 hash for Sophia’s account       |
| Wordlists (e.g., rockyou) | Common passwords & phrases for hash cracking  |
| Web browser               | Test the recovered credentials on the website |

---

## 📚 Key Learnings

| 🔑 Concept           | 🧠 Takeaway                                             |
| -------------------- | ------------------------------------------------------- |
| Breached credentials | Old leaks can still be weaponized if users reuse creds. |
| MD5 hashing          | Unsalted MD5 is trivial to brute-force today.           |
| OSINT + breaches     | OSINT helps prioritize *which* accounts to target.      |
| Credential stuffing  | Reusing passwords across services is extremely risky.   |

Some concrete lessons:

* **Never reuse passwords** between internal systems and external services.
* Use **salted, slow KDFs** (e.g., bcrypt/Argon2/scrypt) instead of MD5.
* Continuously monitor breach corpuses for your corporate domains and force **password resets** when new hits appear.
* Role-based accounts (CFO, CEO, etc.) are **high-value** and should be protected with strong, unique passphrases and **MFA**.

---

## 💬 Final Thoughts

> ✨ This challenge nicely ties together **OSINT**, **breach analysis**, and **practical password cracking**.
> With just a few clues and some targeted filtering, a single weak MD5-protected password was enough to compromise a high-value account.
> Another flag captured! 🏴‍☠️🚀

---
⭐ **Author:** Mathieu N.
🕒 **Date:** December 2025
🏆 **CTF Event:** RTIOC - December CTF  
📍 **Category:** Web / OSINT / Password Cracking
---
