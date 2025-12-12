# 🧩 **Blue Team | Challenge - Home Base**

> 🏷️ *Category:* **OSINT / Threat Intelligence**
> ⚙️ *Difficulty:* **Easy**
> 🕵️ *Author:* **cybersecurity.ctfd.io**
> 🧠 *Concepts:* Base64, XML parsing, 3-word geocode, OSINT pivoting, planetary nomenclature

---

## 📜 Challenge Description

> 💬
> The Threat Intel team found a darknet forum message about a meetup at the threat actor’s base of operations on Mars.
> We must use threat intelligence techniques to determine **where their home base is located**.
> The flag is the **dune field** most likely to be their base of operations.

---

## 📦 Provided Files / Data

| 📁 File / Variable | 🔍 Description                      | 💾 Value                     |
| ------------------ | ----------------------------------- | ---------------------------- |
| `forum_message`    | Suspicious encoded message          | Base64 string                |
| `decoded_message`  | Decoded payload                     | XML                          |
| `meetLoc/value`    | Location “reference” inside the XML | `ribald interject miniature` |
| `coords`           | Decoded coordinates from 3-word ref | `N72° 00.001' W070° 00.003'` |

---

## 🧠 Understanding the Problem

🕵️‍♂️ The message isn’t giving a city/country directly. Instead, it embeds a **location “Reference”** in the form of **three words**, which strongly suggests a **3-word geocode** (what3words-style).
Once we convert that reference into coordinates, we can pivot via OSINT to identify the **named dune field** at that location (on **Mars**, based on the message context).

---

## 🧩 Step-by-Step Solution

### 🔹 Step 1: Decode the message

🧩 *“What does this look like?”*

* The provided string is Base64.
* Decoding it reveals an XML structure (`<RedMsg>...</RedMsg>`).

Key fields found in the XML:

* `<mission>Perseverance</mission>`
* `<sol>1724</sol>`
* `<meetLoc> ... <value>ribald interject miniature</value> ... </meetLoc>`

---

### 🔹 Step 2: Recognize the “3 words” as a location reference

The value:

* `ribald interject miniature`

…matches the common pattern of **3-word geocodes** used to represent coordinates.

To proceed, we treated it as a 3-word locator (`ribald.interject.miniature`) and decoded it into latitude/longitude using a what3words-style / open equivalent decoder (CTF/OSINT pivot).

---

### 🔹 Step 3: Decode the 3-word reference into coordinates

Decoding produced coordinates:

* `N72° 00.001' W070° 00.003'`
  (effectively ~**72°N, 70°W**)

At first glance, if interpreted as **Earth GPS**, this lands in the ocean near Baffin Island — a strong hint that we must interpret the coordinates in the **context of the message**.

---

### 🔹 Step 4: Apply context pivot (Mars, not Earth)

The XML explicitly references:

* **Perseverance** (Mars rover mission)
* **Sol** (Martian day count)

Therefore, the coordinates should be interpreted as **planetary coordinates on Mars**, not Earth.

Next OSINT pivot:

* Search a **Mars nomenclature / gazetteer** for the named dune field located near **72°N, 70°W**.

This leads to the dune field:

✅ **Abalos Undae**

---

### 🔹 Step 5: Recover the Flag

<details>
<summary>🎯 <b>Click to Reveal the Flag</b></summary>

```
flag{AbalosUndae}
```

</details>

---

## 📘 Explanation — *Why It Works*

💡 **In short:**

* Threat actors (and CTFs) often avoid plain text locations and instead use **encoded “references”**.
* A **3-word phrase** is a known technique for hiding coordinates in an easily shareable format.
* The key intel pivot was **context**: `Perseverance` + `sol` indicates **Mars**, so Earth mapping is a false lead.
* Using OSINT (planetary nomenclature / gazetteer lookup), the coordinates map to the dune field **Abalos Undae**.

---

## 🧰 Tools & Techniques Used

| 🧩 Tool / Language                  | 💡 Purpose                                         |
| ----------------------------------- | -------------------------------------------------- |
| 🧮 Base64 decoder (e.g., CyberChef) | Decode the initial darknet message                 |
| 🔎 Manual XML review                | Identify mission, sol, and meet location reference |
| 🗺️ 3-word geocode decoding         | Convert `ribald interject miniature` → coordinates |
| 🪐 Mars gazetteer / map OSINT       | Convert coordinates → named dune field             |

---

## 📚 Key Learnings

| 🔑 Concept           | 🧠 Takeaway                                                                      |
| -------------------- | -------------------------------------------------------------------------------- |
| Context-driven OSINT | Always use message context (Mars mission + sol) to avoid false leads             |
| 3-word geocodes      | Three-word references can be a lightweight coordinate encoding                   |
| Pivoting methodology | Decode → extract fields → convert reference → validate with authoritative naming |

---

## 💬 Final Thoughts

> ✨ This challenge was a clean reminder that **OSINT is about pivots**: decode → identify the indicator → interpret using context → confirm with authoritative references.
> Once the “Mars, not Earth” pivot clicked, the dune field lookup was straightforward. 🏴‍☠️

---
⭐ **Author:** Mathieu Neron  
🕒 **Date:** December 2025  
🏆 **CTF Event:** RTIOC – December CTF  
📍 **Category:** OSINT / Threat Intelligence
---