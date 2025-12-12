# 🧩 **Blue Team | Challenge - Anomaly**

> 🏷️ *Category:* **Blue Team / Log Analysis / Forensics**  
> ⚙️ *Difficulty:* **Easy–Medium**  
> 🕵️ *Author:* **cybersecurity.ctfd.io**  
> 🧠 *Concepts:* SIEM-style log analysis, CEF format, geoIP fields, anomaly detection, ISO country codes

---

## 📜 Challenge Description

> 💬  
> The network team at a joint venture has noticed some suspicious activity in their firewall logs.  
>  
> Can you analyze the logs and identify the country involved in the activity?  
>  
> Unfortunately, due to a configuration error, there are some additional services logging irrelevant data. Focus on the firewall logs to find the clue.  
>  
> **Flag format:** `flag{NameOfCountry}` **OR** `NameOfCountry`

---

## 📦 Provided Files / Data

| 📁 File / Variable      | 🔍 Description                                        | 💾 Value |
| ----------------------- | ----------------------------------------------------- | -------- |
| `logs.log`             | Raw mixed logs from multiple systems/services         | —        |

---

## 🧠 Understanding the Problem

🕵️‍♂️ We’re given a big, noisy log file from a fictional company using SecureSouls devices.  
Our job:

1. Ignore irrelevant logs (non-firewall).
2. Focus on **firewall** entries only.
3. Analyze those for **suspicious activity**.
4. Identify **which country** is the standout / culprit based on the logs.
5. Output the country name as the flag.

So this is a **log forensics / blue team** style challenge: pattern recognition and anomaly spotting in structured log fields.

---

## 🧩 Step-by-Step Solution

### 🔹 Step 1: Isolate the Firewall Logs

The first hint in the challenge text:

> *“Due to a configuration error, there are some additional services logging irrelevant data. Focus on the firewall logs…”*

Looking at `logs.log`, each line is a CEF-style entry:

```text
CEF:0|Vendor|Product|Version|SignatureID|Name|Severity| key=value ...
````

The firewall entries all have:

```text
SecureSouls|Firewall|
```

in the header. So, to filter on a real system, we could do something like:

**On Linux/macOS:**

```bash
grep 'SecureSouls|Firewall' logs.log > curated_logs.log
```

**On Windows (PowerShell):**

```powershell
Select-String -Path ".\logs.log" -Pattern "\|SecureSouls\|Firewall\|" |
    ForEach-Object { $_.Line } |
    Set-Content ".\curated_logs.log"
```

The resulting `curated_logs.log` (which you generated and provided) is the cleaned, **firewall-only** dataset we need to analyze.

---

### 🔹 Step 2: Identify Suspicious Activity Entries

In the curated log, most firewall events look like this:

```text
CEF:0|SecureSouls|Firewall|5.2.2|1001|Connection Allowed|Low|srcIP=... dstIP=... protocol=... srcGeo=US dstGeo=DE
```

Key traits:

* `SignatureID = 1001`
* `Name = Connection Allowed`
* `Severity = Low`
* Fields like `srcIP`, `dstIP`, `srcPort`, `dstPort`, `protocol`, `srcGeo`, `dstGeo`, etc.

The clearly **interesting** entries are those with:

```text
|2001|Suspicious Activity Detected|High|
```

and an `activityType` field:

```text
activityType=DDoS attempt
activityType=port scan
activityType=anomalous communication
```

So we focus on all lines with:

* `SecureSouls|Firewall`
* `Suspicious Activity Detected`
* `activityType=...`

These are the “alerts” that might point us to the culprit country.

---

### 🔹 Step 3: Look at Geo Information (srcGeo/dstGeo)

Most normal connection logs (and many suspicious ones) use typical country codes:

* `US` – United States
* `UK` – United Kingdom
* `DE` – Germany
* `FR` – France
* `AU` – Australia
* `IN` – India
* `CN` – China

For example:

```text
...|Connection Allowed|Low|... srcGeo=US dstGeo=DE
...|Connection Allowed|Low|... srcGeo=AU dstGeo=FR
...|Suspicious Activity Detected|High|... activityType=DDoS attempt ...
```

These all look like standard ISO country codes and appear multiple times.
Nothing in particular stands out at first glance — it’s just normal traffic and typical “big” countries involved in suspicious behavior (DDoS, port scans).

---

### 🔹 Step 4: Spot the Outlier – A Weird Destination Country

Among the suspicious activity entries, **one** stands out:

* It uses `activityType=anomalous communication`.
* Its destination geo field is **unusual** compared to the rest.

You find a line similar to:

```text
CEF:0|SecureSouls|Firewall|...|2001|Suspicious Activity Detected|High|srcIP=... dstIP=... activityType=anomalous communication severityScore=... dstGeo=KI
```

Here, the critical part is:

```text
dstGeo=KI
```

`KI` is **not** one of the common country codes we saw earlier (US, UK, DE, FR, AU, IN, CN).
Looking up ISO country code `KI`, we find:

> `KI` = **Kiribati**

This single **anomalous communication** going to `dstGeo=KI` is the clear, deliberate outlier planted by the challenge author.

Since the challenge question is:

> *“…identify the country involved in the activity.”*

and this entry is:

* Marked as **suspicious** (`Suspicious Activity Detected`, `High`),
* Marked as **anomalous communication** (not just DDoS or port scan),
* Targeting a rare / unexpected destination (`dstGeo=KI`),

we can confidently conclude that the intended “culprit country” is **Kiribati**.

---

### 🔹 Step 5: Recover the Flag

The challenge allows either the raw country name or the wrapped flag format:

> **Flag format:** `flag{NameOfCountry}` OR `NameOfCountry`

So we submit:

<details>
<summary>🎯 <b>Click to Reveal the Flag</b></summary>

```text
flag{Kiribati}
```

</details>

---

## 📘 Explanation — *Why It Works*

💡 **In short:**

* The log file is noisy and includes multiple products/services.
* We are explicitly told to **focus on firewall logs**, so we filter on `SecureSouls|Firewall`.
* Inside those firewall logs, the **suspicious activity** entries (`Suspicious Activity Detected`, `High`) contain an `activityType` field.
* Among those, most are DDoS / port scans involving common countries.
* A single outlier event is labeled `anomalous communication` with `dstGeo=KI`.
* `KI` is the ISO alpha-2 code for **Kiribati**, a small island nation — clearly chosen to stand out.

This is a classic blue-team-style CTF trick: use **log parsing and pattern recognition** to spot something that doesn’t fit.

---

## 🧰 Tools & Techniques Used

| 🧩 Tool / Technique       | 💡 Purpose                                      |
| ------------------------- | ----------------------------------------------- |
| `grep` / `Select-String`  | Filter on `SecureSouls\|Firewall\|` lines       |
| Manual log review         | Identify `Suspicious Activity Detected` entries |
| ISO country codes         | Interpret `srcGeo` / `dstGeo` fields            |
| Anomaly detection mindset | Look for outliers in otherwise normal patterns  |

---

## 📚 Key Learnings

| 🔑 Concept            | 🧠 Takeaway                                                  |
| --------------------- | ------------------------------------------------------------ |
| Log filtering         | Always narrow scope to relevant sources (here: firewall).    |
| CEF log structure     | Vendor/Product/Version + key-value pairs are very parseable. |
| GeoIP / country codes | `srcGeo` / `dstGeo` can be critical investigation clues.     |
| Outlier detection     | The weird thing (here: `dstGeo=KI`) is often the flag.       |

---

## 💬 Final Thoughts

> ✨ This challenge is a solid reminder that **blue team work is often about pattern recognition and careful filtering**.
> The data might be noisy and full of distractions, but once you isolate the relevant log source and look for anomalies, the answer tends to pop out — in this case, a single odd `dstGeo=KI` pointing all the way to **Kiribati**.
>
> Another flag captured! 🏴‍☠️📊

---
⭐ **Author:** Mathieu N.
🕒 **Date:** December 2025
🏆 **CTF Event:** RTIOC - December CTF 
📍 **Category:** Blue Team / Log Analysis
---