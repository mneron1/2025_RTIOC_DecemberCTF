````markdown
# 🧩 **Blue Team | Challenge - Caught Attacker**

> 🏷️ *Category:* **Forensics / Network**
> ⚙️ *Difficulty:* **Medium**
> 🕵️ *Author:* **cybersecurity.ctfd.io**
> 🧠 *Concepts:* PCAP analysis, TLS decryption, Wireshark, HTTP/2, Content-Disposition, credential access tooling (mimikatz)

---

## 📜 Challenge Description

> 💬  
> Antivirus has detected suspicious network activity originating on a workstation in the accounting team and raised an Incident in the Security Information & Event Management (SIEM) solution.
>  
> Initial analysis by the Level 1 Incident Response Team indicates the machine was compromised and an attacker attempted to download a password extraction tool.  
> The Level 1 Team isolated the affected system and captured all relevant network traffic in a PCAP file. Luckily this machine also saved the SSL key logs.
>  
> Analyze the provided packet capture and determine the exact filename of the malicious tool the attacker tried to download.  
>  
> The flag for this challenge is the full filename of the tool that the attacker tried to download.  
> The filename contains the name of the tool and can be submitted with or without the file extension.  
>  
> ❗ Do **NOT** download or reconstruct the tool from the link in the PCAP – it’s not required and will trigger AV.

---

## 📦 Provided Files / Data

| 📁 File / Variable    | 🔍 Description                                 | 💾 Value     |
| --------------------- | ---------------------------------------------- | ------------ |
| `pcap.pcapng`         | Full packet capture from the compromised host  | —            |
| `sslkeylog.log`       | TLS (pre-)master secrets log for this session  | —            |

---

## 🧠 Understanding the Problem

🕵️‍♂️ Before jumping in, let’s restate the goal:

We’re given:

- A **network capture** of a compromised Windows workstation.
- The **SSL key log**, which allows us to decrypt HTTPS/TLS traffic.

We need to:

- Use the PCAP + SSL key log to **decrypt the traffic**,
- Identify **which malicious password extraction tool** was downloaded,
- Extract the **exact filename** (e.g. `toolname-version.zip`),
- Submit that filename as the flag.

This is a classic **network forensics + TLS decryption** challenge: the real evidence (the tool name) is hidden inside encrypted HTTP/2 over TLS, and the SSL key log is the key to unlocking it.

---

## 🧩 Step-by-Step Solution

### 🔹 Step 1: Initial Observation

🧩 *“What does this look like?”*

1. Open `pcap.pcapng` in **Wireshark**.
2. Without TLS decryption, most of the interesting traffic shows up as **TLS** or **HTTP/2 over TLS** with no readable payload.
3. Some cleartext HTTP/HTTPS hosts look benign:
   - `www.msftconnecttest.com`
   - `ocsp.digicert.com`
   - `windowsupdate.microsoft.com`
   - `edge.microsoft.com`
4. Suspicious clue: the challenge text mentions a **password extraction tool** (often mimikatz, LaZagne, etc.), so we expect:
   - A download from a public hosting source (GitHub, direct site, etc.),
   - Or Defender/SmartScreen fetching a copy for analysis.

Conclusion: we need **TLS decryption** to see the actual HTTP requests and responses and identify the downloaded file.

---

### 🔹 Step 2: Enable TLS Decryption in Wireshark

To leverage the provided `sslkeylog.log`:

1. In Wireshark:
   - `Edit → Preferences… → Protocols → TLS`
2. Set:
   - **(Pre)-Master-Secret log filename** → select `sslkeylog.log`.
3. Click **OK**, then reload the capture (`Ctrl+R`) so Wireshark re-parses packets with decryption enabled.

Now, when we apply HTTP-related filters, Wireshark can show **decrypted HTTP/HTTPS and HTTP/2** traffic.

Useful filters:

```wireshark
http || http2
````

For requests:

```wireshark
http.request.method == "GET"
```

We can also look specifically for likely downloads:

```wireshark
http && (frame contains ".zip" || frame contains ".exe" || frame contains "Content-Disposition")
```

---

### 🔹 Step 3: Find the Suspicious Download

With decryption enabled and `http.request.method == "GET"` applied, we inspect the GET requests.

Among mostly normal system traffic, we find an interesting HTTP/2 stream:

```http
:method: GET
:authority: codeload.github.com
:scheme: https
:path: /gentilkiwi/mimikatz/zip/refs/tags/2.2.0-20220919
upgrade-insecure-requests: 1
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0
accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
...
```

Key observations:

* **Host**: `codeload.github.com` – GitHub’s file download CDN.
* **Path**: `/gentilkiwi/mimikatz/zip/refs/tags/2.2.0-20220919`

  * `gentilkiwi/mimikatz` is the official GitHub repo for **mimikatz**, a well-known credential dumping / password extraction tool.
  * The path indicates a **zip archive for the tagged release `2.2.0-20220919`**.

This strongly suggests the user (or attacker-controlled process) is downloading **mimikatz** from GitHub.

To confirm the exact filename, we need to look at the HTTP/2 response headers.

---

### 🔹 Step 4: Inspect the HTTP/2 Stream and Extract the Filename

In Wireshark:

1. Right-click the suspicious packet (the GET to `codeload.github.com`).
2. Choose **Follow → HTTP/2 Stream** (or **Follow → TLS Stream** and view the decoded HTTP/2 payload).
3. In the followed stream, we see the server’s response:

```http
:status: 200
access-control-allow-origin: https://render.githubusercontent.com
content-disposition: attachment; filename=mimikatz-2.2.0-20220919.zip
content-security-policy: default-src 'none'; style-src 'unsafe-inline'; sandbox
content-type: application/zip
cross-origin-resource-policy: cross-origin
etag: W/"e9b3327cae042dea45ae502f6bafa99c1dd73c88ab8e96527596f3885bbd25d1"
strict-transport-security: max-age=31536000
vary: Authorization,Accept-Encoding
x-content-type-options: nosniff
x-frame-options: deny
x-xss-protection: 1; mode=block
date: Tue, 25 Nov 2025 00:31:20 GMT
x-github-request-id: C620:2F23D3:12CA4:4B815:6924F8D8
```

The critical header is:

```http
content-disposition: attachment; filename=mimikatz-2.2.0-20220919.zip
```

This header tells the browser exactly which **filename** to use when saving the file.

So, the **malicious tool** being downloaded is:

> `mimikatz-2.2.0-20220919.zip`

According to the challenge statement, the tool name (with extension optional) is what we must use for the flag.

---

### 🔹 Step 5: Recover the Flag

<details>
<summary>🎯 <b>Click to Reveal the Flag</b></summary>

```text
flag{mimikatz-2.2.0-20220919}
```

</details>

> Note: The actual downloaded file on disk would be `mimikatz-2.2.0-20220919.zip`, but the platform accepts the filename with or without the `.zip` extension.

---

## 📘 Explanation — *Why It Works*

💡 **In short:**

* HTTPS/TLS normally hides the HTTP methods, URLs, and headers from casual inspection.
* The provided `sslkeylog.log` contains **(pre-)master secrets** for the TLS sessions, which allows Wireshark to:

  * Derive the session keys,
  * Decrypt TLS records,
  * Reconstruct HTTP/HTTPS or HTTP/2 streams as if they were plaintext.
* By decrypting the stream to `codeload.github.com`, we can:

  * See the `GET` request to the mimikatz repository,
  * Read the response headers,
  * Inspect the `Content-Disposition` header, which exposes the **true filename**:

    * `filename=mimikatz-2.2.0-20220919.zip`.

In a real IR scenario, this ties the incident to **mimikatz**, a well-known credential dumping tool, which directly supports the hypothesis that the attacker attempted to deploy a **password extraction utility** on the compromised host.

---

## 🧰 Tools & Techniques Used

| 🧩 Tool / Language | 💡 Purpose                                            |
| ------------------ | ----------------------------------------------------- |
| 🕸️ Wireshark      | PCAP analysis and TLS decryption                      |
| 🔑 SSL Key Log     | (Pre-)master secrets to enable HTTPS decryption       |
| 🔎 HTTP/2 follow   | Reconstruct and inspect full HTTP/2 request/response  |
| 🎯 Filters         | `http`, `http2`, `http.request.method == "GET"`, etc. |

---

## 📚 Key Learnings

| 🔑 Concept                   | 🧠 Takeaway                                                            |
| ---------------------------- | ---------------------------------------------------------------------- |
| TLS decryption with key logs | SSL key logs turn opaque TLS streams into fully inspectable HTTP       |
| Content-Disposition headers  | Often reveal the exact filename of downloaded content                  |
| Living-off-legit-services    | Attackers frequently use GitHub and other legit platforms for tools    |
| Mimikatz as a threat signal  | Network evidence of mimikatz download is a strong credential-theft IOC |

Examples:

* 🔐 **Visibility matters**: With just the PCAP, traffic looked like generic TLS; with the key log, we see a **precise mimikatz download**.
* 🧩 **Header inspection**: Even if URLs are messy, `Content-Disposition` reliably exposes filenames.
* 🛡️ **Threat hunting**: Downloads from `gentilkiwi/mimikatz` or filenames matching `mimikatz*.zip` should be high signal in logs.

---

## 💬 Final Thoughts

> ✨ This challenge is a perfect example of how **blue team forensics + the right artifacts** (like an SSL key log) turn a “black box” TLS session into clear evidence.
> We didn’t need to detonate or reconstruct the binary — just careful network analysis and HTTP header inspection was enough to attribute the activity to **mimikatz** and extract the filename for the flag.
> Another incident understood, and another flag captured. 🏴‍☠️🔍

---
⭐ **Author:** Mathieu Neron  
🕒 **Date:** December 2025  
🏆 **CTF Event:** RTIOC – December CTF  
📍 **Category:** Forensics / Network
---