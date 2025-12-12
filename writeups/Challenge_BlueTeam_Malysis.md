# 🧩 **Blue Team | Challenge - Malysis**
> 🏷️ *Category:* **Reverse Engineering / Incident Response**
> ⚙️ *Difficulty:* **Easy**
> 🕵️ *Author:* **cybersecurity.ctfd.io**
> 🧠 *Concepts:* ELF analysis, `strings`, disassembly, XOR logic, IOC extraction

---

## 📜 Challenge Description

> 💬
> We received a suspicious binary dropped in a sandbox by operators attributed to **M-APT25 (Red Dune Collective)**.
> We must analyze the malware and extract further IOC info — **notably any embedded Bitcoin addresses**.
>
> Known IOCs:
>
> * **Sha256:** `489ea205dd1717f9f7b8adfc8f76e253926118c4b788cc7df884cdb938ea0073`
> * **Head:** `f0VMRgIBAQAAAAAAAAAAAAMAPgABAAAAgBAAAAAAAAA=`
> * **Names:** `Files.bin`, `WindowsBackupUtility.exe`, `AppHostRegistrationVerifer.exe`
>
> Flag format: `flag{BTC_Address}`

---

## 📦 Provided Files / Data

| 📁 File / Variable | 🔍 Description                     | 💾 Value                                                                  |
| ------------------ | ---------------------------------- | ------------------------------------------------------------------------- |
| `Files.bin`        | Suspicious dropped binary (sample) | —                                                                         |
| `Sha256`           | Known hash IOC                     | `489ea205dd1717f9f7b8adfc8f76e253926118c4b788cc7df884cdb938ea0073`        |
| `Head`             | Base64 header of the file          | `f0VMRgIBAQAAAAAAAAAAAAMAPgABAAAAgBAAAAAAAAA=`                            |
| `Names`            | Observed filenames used by actor   | `Files.bin`, `WindowsBackupUtility.exe`, `AppHostRegistrationVerifer.exe` |

---

## 🧠 Understanding the Problem

🕵️‍♂️ The goal is to reverse the binary enough to locate **embedded indicator strings**, specifically a **Bitcoin-like address** (not necessarily valid BTC format, but recognizable).

---

## 🧩 Step-by-Step Solution

### 🔹 Step 1: Identify the File Type

🧩 *“What does this look like?”*

The provided `Head` value is Base64. Decoding it reveals the magic bytes:

* `0x7F 45 4C 46` → `\x7fELF`

✅ This indicates the binary is an **ELF executable** (likely Linux x64).

Useful quick checks:

```bash
file Files.bin
strings -n 6 Files.bin | head
```

---

### 🔹 Step 2: Triage With Static Strings + Disassembly

Because the prompt hints at embedded IOCs, `strings` is a fast first pass:

```bash
strings -n 6 Files.bin | grep -i -E "btc|addr|wallet|coin"
```

If the address isn’t visible directly, open the binary in a disassembler (examples: **Cutter**, **Ghidra**, **IDA**) and search for:

* suspicious strings / format patterns
* decoding routines (XOR, add/sub loops, byte arrays)
* references to `.rodata` blobs

---

### 🔹 Step 3: Locate the BTC Address Decoder Logic

In the disassembly, the BTC IOC is produced inside a function (named in the decompiler as something like `gen_btc_addr()`).

Key behavior:

* The function only reveals the “BTC Addr” when called with a specific value.
* It checks:

`0xDEADBF4D ^ 0xDEADBEEF == 0x1A2`

So the expected argument is:

* `0x1A2` (decimal **418**)

When that condition is satisfied, the function decodes a 34-byte embedded blob into a readable string:

```
BTC Addr: 1A1zP1eP5QGefi2DMPTfTL5S
```

---

### 🔹 Step 4: Recover the Flag

<details>
<summary>🎯 <b>Click to Reveal the Flag</b></summary>

```
flag{1A1zP1eP5QGefi2DMPTfTL5S}
```

</details>

---

## 📘 Explanation — *Why It Works*

💡 **In short:**

The binary stores the “BTC address” **obfuscated** (as a small byte array) and only **decodes/prints** it when a gating condition is met.
That gate is implemented using a simple XOR identity (with obvious “DEAD/BEEF” constants), making the required input easy to derive.

---

## 🧰 Tools & Techniques Used

| 🧩 Tool / Language     | 💡 Purpose                                 |
| ---------------------- | ------------------------------------------ |
| `file` / Base64 decode | Confirm ELF signature from the header      |
| `strings`              | Quick IOC discovery / keyword searching    |
| Cutter / Ghidra / IDA  | Disassembly + decompilation                |
| (Optional) GDB         | Validate the function behavior dynamically |

---

## 📚 Key Learnings

| 🔑 Concept             | 🧠 Takeaway                                                                     |
| ---------------------- | ------------------------------------------------------------------------------- |
| IOC hunting in malware | Often starts with `strings`, then pivots to code paths that *construct* strings |
| Simple obfuscation     | XOR gates/byte arrays are common and fast to reverse                            |
| “Fake” BTC formats     | Threat actors may embed lookalike addresses purely as identifiers or tags       |

---

## 💬 Final Thoughts

> ✨ A quick win: the challenge reinforces that **basic static analysis + spotting trivial XOR tricks** is enough to extract valuable IOCs from many real-world samples.

---

⭐ **Author:** Mathieu Neron  
🕒 **Date:** December, 2025  
🏆 **CTF Event:** RTIOC – December CTF  
📍 **Category:** Reverse Engineering / Incident Response

---
