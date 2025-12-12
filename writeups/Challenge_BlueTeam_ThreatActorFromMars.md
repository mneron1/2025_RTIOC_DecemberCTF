# 🧩 **Blue Team Path | Challenge - Threat Actor From Mars** 

> 🏷️ *Category:* **Threat Intel / Blue Team / MITRE ATT&CK**
> ⚙️ *Difficulty:* **Easy**
> 🕵️ *Author:* **RTIOC – December CTF**
> 🧠 *Concepts:* MITRE ATT&CK, Defense Evasion, Threat Profiling

---

## 📜 Challenge Description

> 💬
> Intel reports suggest a new threat actor group calling themselves "Red Dune Collective" has emerged from Mars.
>
> Analyze the attached threat actor profile and identify their defense evasion techniques.
>
> The flag is the concatenation of the two MITRE ATT&CK® sub-technique IDs they use for defense evasion.
>
> Flag format: `flag{T1000.000T2000.000}` OR `T1000.000T2000.000`

---

## 📦 Provided Files / Data

| 📁 File / Variable          | 🔍 Description                             | 💾 Value                  |
| --------------------------- | ------------------------------------------ | ------------------------- |
| `tap-RedDuneCollective.pdf` | Threat Action Profile: Red Dune Collective | PDF from challenge portal |

The threat profile contains a MITRE ATT&CK TTPs section describing how Red Dune Collective operates across the kill chain, including initial access, execution, persistence, privilege escalation, defense evasion, and more.

---

## 🧠 Understanding the Problem

🕵️‍♂️ At a high level, we need to:

1. Read the threat actor profile for **Red Dune Collective**.
2. Identify the parts that describe **defense evasion**, specifically.
3. Map those behaviors to **MITRE ATT&CK sub-techniques**.
4. Concatenate the two sub-technique IDs (defense evasion only) to form the flag.

We’re not asked to fully analyze every TTP – only to zero in on **defense evasion** and correctly translate the narrative description into **MITRE IDs**.

---

## 🧩 Step-by-Step Solution

### 🔹 Step 1: Initial Observation

🧩 *“What does this look like?”*

Opening `tap-RedDuneCollective.pdf`, we find a “MITRE ATT&CK TTPs” section describing behavior across the attack lifecycle.

In the middle of that section we see the relevant line for this challenge:

> “They evade detection with **embedded payloads** and **renaming legitimate utilities**.”

These two phrases are *very* characteristic of specific MITRE ATT&CK **defense evasion** sub-techniques:

* **Embedded payloads** → sounds like obfuscated/hidden content inside files or scripts.
* **Renaming legitimate utilities** → classic “masquerading” behavior.

So the challenge is clearly about **mapping these two behaviors** to their precise **ATT&CK sub-technique IDs**.

---

### 🔹 Step 2: Analyze and Map to MITRE ATT&CK

Now we turn those narrative descriptions into ATT&CK entries.

#### 2.1. “Embedded payloads”

The phrase *“embedded payloads”* in a defense evasion context matches the MITRE ATT&CK sub-technique under **Obfuscated/Encrypted Files and Information** where payloads are hidden inside other content.

* **Technique family:** Obfuscated Files or Information
* **Sub-technique:** **Embedded Payloads**
* **Sub-technique ID:** **T1027.009**

So the **first defense evasion sub-technique** is:

> **T1027.009 – Obfuscated Files or Information: Embedded Payloads**

---

#### 2.2. “Renaming legitimate utilities”

The second phrase is *“renaming legitimate utilities”*. This is a textbook example of **masquerading**:

* Adversaries rename legitimate utilities (or their own tools) so they **appear** to be system binaries or trusted applications, to avoid detection.

In ATT&CK, this is captured by the **Masquerading** family and specifically the sub-technique for renaming legitimate utilities:

* **Technique family:** Masquerading
* **Sub-technique:** **Rename Legitimate Utilities**
* **Sub-technique ID:** **T1036.003**

So the **second defense evasion sub-technique** is:

> **T1036.003 – Masquerading: Rename Legitimate Utilities**

---

### 🔹 Step 3: Build the Flag

The challenge instructions say:

> *“The flag is the concatenation of the two MITRE ATT&CK® sub-technique IDs they use for defense evasion.”*

We’ve identified:

1. **T1027.009** – Obfuscated Files or Information: Embedded Payloads
2. **T1036.003** – Masquerading: Rename Legitimate Utilities

Concatenating them in that order:

> **T1027.009T1036.003**

---

### 🔹 Step 4: Recover the Flag

<details>
<summary>🎯 <b>Click to Reveal the Flag</b></summary>

```text
flag{T1027.009T1036.003}
```

</details>

---

## 📘 Explanation — *Why It Works*

💡 **In short:**

* The threat profile explicitly calls out **two defense evasion behaviors**:

  * Using **embedded payloads** to hide malicious code.
  * **Renaming legitimate utilities** to disguise tools and evade detection. 
* These map directly to ATT&CK **defense evasion** sub-techniques:

  * **T1027.009 – Embedded Payloads**: hiding malicious content inside otherwise benign files or structures makes static detection harder.
  * **T1036.003 – Rename Legitimate Utilities**: renaming binaries to look like legitimate system tools helps bypass naive process-name-based detections.
* The challenge doesn’t require us to enumerate all Red Dune Collective TTPs, just to **recognize which ones are defense evasion** and then **translate** them into precise ATT&CK IDs.

This is a classic threat intel / blue team exercise:
**Read the narrative → identify behaviors → map them to ATT&CK for consistent tracking and detection engineering.**

---

## 🧰 Tools & Techniques Used

| 🧩 Tool / Language     | 💡 Purpose                                    |
| ---------------------- | --------------------------------------------- |
| PDF reader             | Open and read `tap-RedDuneCollective.pdf`     |
| MITRE ATT&CK knowledge | Map narrative TTPs to official sub-techniques |
| Note-taking / markdown | Document reasoning and final flag             |

---

## 📚 Key Learnings

| 🔑 Concept                       | 🧠 Takeaway                                                               |
| -------------------------------- | ------------------------------------------------------------------------- |
| MITRE ATT&CK mapping             | Threat reports often describe behaviors that can be mapped to ATT&CK IDs. |
| Defense evasion via obfuscation  | **Embedded payloads** are a form of obfuscation to slip past detections.  |
| Defense evasion via masquerading | **Renaming utilities** is a simple but effective way to masquerade tools. |

---

## 💬 Final Thoughts

> ✨ This challenge is a neat reminder that **good blue-team work is often about careful reading**:
> If you can translate narrative threat intel into structured frameworks like MITRE ATT&CK, you can:
>
> * Build better detections,
> * Track actors more consistently,
> * And share intelligence more effectively across teams.
>   Another Martian-flavored flag captured. 🚀🔴

---
⭐ **Author:** Mathieu N.
🕒 **Date:** December 2025
🏆 **CTF Event:** RTIOC - December CTF 
📍 **Category:** OSINT, Threat Intelligence
---