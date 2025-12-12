# 🧩 **Red Team | Challenge - One Time Memory Pad**

> 🏷️ *Category:* **Cryptography, Discovery, Steganography**
> ⚙️ *Difficulty:* **Medium**
> 🕵️ *Author:* **cybersecurity.ctfd.io**
> 🧠 *Concepts:* XOR, One-Time Pad (OTP), keystream reuse, image forensics

---

## 📜 Challenge Description

> 💬
> Aftering failing to get a shell from the open port some other members fuzzed the process further and were able to extract 2 images from the machines memory.
> They look like random noise but we think they've both been encrypted with the same XOR based key. At least that's the info the team was able to pull from memory.
> Can you recover the original images?

---

## 📦 Provided Files / Data

| 📁 File / Variable | 🔍 Description                              | 💾 Value |
| ------------------ | ------------------------------------------- | -------- |
| `picture1.bmp`     | Obfuscated bitmap image (suspected XOR/OTP) | —        |
| `picture2.bmp`     | Obfuscated bitmap image (suspected XOR/OTP) | —        |

---

## 🧠 Understanding the Problem

🕵️‍♂️ The two BMP images did not display meaningful content by themselves.
Given the “multiple levels of obfuscation” hint and the presence of **two similar binary blobs**, a strong hypothesis is **XOR-based encryption** (often presented as “OTP”).

If the same OTP/keystream is reused across two messages:

* `C1 = P1 ⊕ K`
* `C2 = P2 ⊕ K`
* `C1 ⊕ C2 = (P1 ⊕ K) ⊕ (P2 ⊕ K) = P1 ⊕ P2` ✅

So XORing the two ciphertexts can cancel the key and reveal structure/text.

---

## 🧩 Step-by-Step Solution

### 🔹 Step 1: Identify the files and format

* Confirm both files are BMPs (standard bitmap headers)
* Note: XORing entire files may corrupt headers, so we preserve the BMP header and XOR only the pixel array.

---

### 🔹 Step 2: Locate the BMP pixel data offset

In a BMP, the pixel array offset is stored at bytes `10..13` (little-endian).
We use that to avoid breaking the header.

---

### 🔹 Step 3: XOR the pixel data to recover the hidden message

```python
from pathlib import Path

b1 = Path("picture1.bmp").read_bytes()
b2 = Path("picture2.bmp").read_bytes()

# BMP pixel array offset is at bytes 10..13 (little-endian)
off = int.from_bytes(b1[10:14], "little")

# Keep header from picture1, XOR the pixel data
out = b1[:off] + bytes(a ^ b for a, b in zip(b1[off:], b2[off:]))

Path("recovered.bmp").write_bytes(out)
print("Wrote recovered.bmp - open it to read the flag.")
```

🧾 **Result:**
Opening `recovered.bmp` reveals readable text containing the flag.

---

### 🔹 Step 4: Recover the Flag

<details>
<summary>🎯 <b>Click to Reveal the Flag</b></summary>

```
flag{dont_reuse_your_OTP_keys_4f9a2c8b}
```

</details>

---

## 📘 Explanation — *Why It Works*

💡 **In short:**

This works because a “One-Time Pad” is only secure if the key/keystream is truly random **and never reused**.
When the same keystream `K` encrypts two different plaintexts, XORing the ciphertexts cancels out `K`, leaving `P1 ⊕ P2`. With structured formats like BMPs (and especially if one plaintext contains text/solid areas), the result becomes visually readable and leaks the hidden content.

---

## 🧰 Tools & Techniques Used

| 🧩 Tool / Language  | 💡 Purpose                                 |
| ------------------- | ------------------------------------------ |
| 🐍 Python           | XOR processing and BMP reconstruction      |
| 🖼️ Image Viewer    | Open `recovered.bmp` to read the message   |
| 🧠 Crypto reasoning | Identify OTP/keystream reuse vulnerability |

---

## 📚 Key Learnings

| 🔑 Concept            | 🧠 Takeaway                                                       |
| --------------------- | ----------------------------------------------------------------- |
| OTP / XOR             | XOR “encryption” is fragile if misused                            |
| Keystream reuse       | Reusing an OTP key breaks confidentiality                         |
| File format awareness | Preserving headers (BMP offset) makes recovery clean and viewable |

---

## 💬 Final Thoughts

> ✨ This challenge is a clean demonstration of a classic crypto failure: **reusing an OTP key**.
> By XORing the two BMP ciphertexts while preserving the header, the hidden transmission signature (agent codename/flag) was recovered.

---
⭐ **Author:** Mathieu Neron  
🕒 **Date:** Dec, 2025  
🏆 **CTF Event:** RTIOC – December CTF  
📍 **Category:** Forensics / Crypto
---