# 🧩 **Shellz**

> 🏷️ *Category:* **Forensics / OT / Misc**
> ⚙️ *Difficulty:* **Medium**
> 🕵️ *Author:* **RTIOC – December CTF (Cybersecurity Space)**
> 🧠 *Concepts:* Linux jump host, OT/SCADA footprinting, filesystem backups, MySQL dump analysis, hash cracking (MD5)

*Template based on my generic CTF writeup format.* 

---

## 📜 Challenge Description

> 💬
> **Shellz**
>
> Well done resetting that password.
>
> You may not have much time until the victim notices the password reset email. Use the new password to logon to a public jump host used by OT Engineers we found during target Nmap scanning.
>
> See if you can find another set of credentials that will let us pivot to the Operational Technology (OT) environment.
>
> Look for password files, .env files, database exports, cached connections , etc.
>
> **Flag format:**
> `flag{new_password_you_found}` **OR** `new_password_you_found`
>
> Jump host:
> `https://cybersecurity-red-apac-pmel-jh05.chals.io/`

---

## 📦 Provided Files / Data

| 📁 File / Variable | 🔍 Description                                     | 💾 Value                                             |
| ------------------ | -------------------------------------------------- | ---------------------------------------------------- |
| — (web shell)      | Jump host used by OT engineers                     | `https://cybersecurity-red-apac-pmel-jh05.chals.io/` |
| Prior challenge    | Valid creds for user **a.horton** (password reset) | —                                                    |
| Files on host      | OT/SCADA configs, backups, PLC programs, DB dump   | —                                                    |

*(This challenge is more “live host forensics” than standalone files.)*

---

## 🧠 Understanding the Problem

We already compromised an OT engineer’s account (`a.horton`) in the previous OSINT task and were given access to a **public jump host**.

The new objective:

* Log into that jump box.
* **Hunt for additional credentials** that would let us pivot into the **OT environment**:

  * password files
  * `.env` / config files
  * **database exports**
  * cached connections / keys
* Submit the **new password we discover** as the flag.

So this is essentially:

> **Do light host forensics on an OT jump host, leverage backups & SCADA artifacts, and recover an application password.**

---

## 🧩 Step-by-Step Solution

### 🔹 Step 1: Initial Observation – Root on an OT Jump Host

Using the credentials from the previous challenge, we log into:

```text
https://cybersecurity-red-apac-pmel-jh05.chals.io/
```

We immediately see:

```bash
whoami
# -> root

hostname
# -> apac-pmel-jh05

pwd
# -> /root
```

So the “OT jump host” is a Debian box where we land **directly as root** (nice!).

We list home directories:

```bash
ls -la /home
```

Output (simplified):

```text
/home
├── a.horton
├── admin
└── i.benjamin
```

`a.horton` and `i.benjamin` match real OT engineers. That’s our first strong clue we’re on the right box.

Inside `/home/a.horton`:

```bash
ls -la /home/a.horton
```

We see:

* `OpenPLC-projects/`
* `stardust/`
* shell dotfiles

So this host clearly has **PLC / SCADA engineering artifacts**.

---

### 🔹 Step 2: OT/PLC Artifacts & the “FLAG” Hint

We inspect the `stardust` folder:

```bash
cd /home/a.horton/stardust
ls
cat program-info.md
```

Contents (simplified):

```text
# Stardust PLC Primary Controller

[ Ladder Logic Diagram ... ]

Rung 5:
    IX0    IX1    IX2                         FLAG
 ──┤   ├──┤ / ├──┤   ├───────────────────────(     )─────
```

This is a **ladder logic program** showing some PLC inputs and coils. The final rung drives a coil literally named **`FLAG`**.

Interpretation:

* It’s not the actual flag, but a **nudge**:

  * “You’re in the right *domain* (PLC / OT). Keep digging for actual credentials.”

We also look at the `OpenPLC-projects` XMLs (`water-pump.xml`, `alarm-light.xml`). They describe PLC programs, not credentials. So we move on.

---

### 🔹 Step 3: Spotting the Real Goldmine – `.backup` and SCADA

Listing the filesystem root:

```bash
ls -la /
```

We see some unusual directories:

```text
.backup
DMA
IRQ
doorbell
...
test2
```

`DMA`, `IRQ`, `doorbell` are empty, but `.backup` is promising:

```bash
cd /.backup
ls -la
```

Example contents:

```text
backup_20250315_143022/
backup_20250722_143015/
```

These look like **timestamped system backups**. Exactly what we’d expect from a SCADA/OT environment taking regular snapshots.

Exploring the older backup:

```bash
cd /.backup/backup_20250315_143022
find . -maxdepth 5 -type f
```

We find SCADA-related files like:

* `/opt/scada/config/server.json`
* `/var/scada/config/system.conf`
* `/data/historian/process_data.csv`

`server.json` (old version):

```json
{
  "server_port": 8080,
  "modbus_port": 502,
  "update_rate": 100,
  "log_level": "INFO",
  "database": {
    "host": "localhost",
    "port": 3306,
    "name": "scada_db",
    "user": "scada_user"
  },
  "version": "2.0"
}
```

`system.conf` (old):

```ini
# SCADA System Configuration v2.0
SERVER_IP=192.168.1.100
HMI_PORT=8080
HISTORIAN_DB=/data/historian/process.db
ALARM_EMAIL=admin@company.local
BACKUP_INTERVAL=3600
```

These configs show us:

* A **SCADA server** using MySQL: `scada_db`, user `scada_user`.
* A historian DB path.
* But **no password yet**.

The historian CSV is just telemetry data (temperatures/pressure/flow), no creds.

So this backup mainly teaches us **what** components exist.

---

### 🔹 Step 4: Newer Backup – Finding the SCADA DB Dump

Now we pivot to the **newer backup**:

```bash
cd /.backup/backup_20250722_143015
find . -maxdepth 5 -type f
```

Key hits:

```text
./opt/scada/config/server.json
./opt/openplc/programs/main.st
./home/a.horton/stardust/program-info.md
./home/a.horton/Documents/OpenPLC-projects/water-pump.xml
./home/a.horton/Documents/OpenPLC-projects/alarm-light.xml
./var/scada/config/system.conf
./var/scada/logs/system.log
./var/lib/mysql/scada_db_backup.sql
./var/lib/mysql/backup_info.txt
./var/log/openplc.log
./etc/systemd/system/openplc.service
./etc/systemd/system/scada.service
./data/historian/process_data.csv
```

The **juicy one** is:

> `./var/lib/mysql/scada_db_backup.sql` → a **database export**

`backup_info.txt` is just metadata:

```text
Database Backup Information
===========================
Backup Date: 2025-03-22 23:00:15
Database: scada_db
Size: 2.4 MB
Tables: 5
Records: 1547
```

But `scada_db_backup.sql` is where the magic happens.

---

### 🔹 Step 5: Analyzing the MySQL Dump – Extracting Users

We display the SQL dump:

```bash
cd /.backup/backup_20250722_143015/var/lib/mysql
cat scada_db_backup.sql
```

Among table definitions and inserts, the interesting part is the `users` table:

```sql
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id int NOT NULL AUTO_INCREMENT,
    username varchar(50) NOT NULL UNIQUE,
    password varchar(100) NOT NULL,
    role varchar(20) DEFAULT 'operator',
    last_login datetime DEFAULT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;

INSERT INTO users VALUES 
(1,'admin','a833548a4e37a662c397ce117bd23628','administrator','2025-03-22 08:15:00'),
(2,'i.benjamin','773e1e3d8b43064f63e037aa59cabdac','administrator','2025-07-15 14:23:00'),
(3,'a.horton','e8c77935613252dd7ab073a96044eb65','engineer','2025-07-21 16:44:00'),
(4,'service','3fa230d1d46a0fc44b38a512e0d2f76f','service','2025-07-22 09:30:00');
```

We now have:

* SCADA application usernames:

  * `admin`
  * `i.benjamin`
  * `a.horton`
  * `service`
* Their **password hashes**:

  * `a833548a4e37a662c397ce117bd23628`
  * `773e1e3d8b43064f63e037aa59cabdac`
  * `e8c77935613252dd7ab073a96044eb65`
  * `3fa230d1d46a0fc44b38a512e0d2f76f`

Those are **32-hex-character strings** → classic **MD5**-style hashes.

This is exactly what the challenge description meant by:

> “…look for database exports…”

We’ve found a **credential set** — now we just need to crack one of the hashes to get the plaintext password.

---

### 🔹 Step 6: Cracking the Hash – Recovering `scadaninja!`

On our **local machine**, we save the hashes:

```text
a833548a4e37a662c397ce117bd23628:admin
773e1e3d8b43064f63e037aa59cabdac:i.benjamin
e8c77935613252dd7ab073a96044eb65:a.horton
3fa230d1d46a0fc44b38a512e0d2f76f:service
```

We then use a common wordlist (e.g. `rockyou.txt`) with `hashcat` or `john`. Example with `hashcat`:

```bash
# Mode 0 = raw MD5
hashcat -m 0 -a 0 hashes.txt /path/to/rockyou.txt
hashcat -m 0 --show hashes.txt
```

Cracking result (the relevant one):

```text
e8c77935613252dd7ab073a96044eb65:a.horton:scadaninja!
```

So:

* User: `a.horton`
* Password: **`scadaninja!`**

This is:

* A **new credential** we discovered from the SCADA database export.
* Perfectly aligned with the OT / SCADA theme (*“ninja” in SCADA land*).

It matches the challenge requirement of “another set of credentials that will let us pivot to the OT environment”.

Per the challenge text, the flag format can be either:

* `flag{new_password_you_found}`
* or just `new_password_you_found`

So `scadaninja!` itself is the accepted flag.

---

### 🔹 Step 7: Recover the Flag

<details>
<summary>🎯 <b>Click to Reveal the Flag</b></summary>

```text
scadaninja!
```

</details>

*(Submitting `scadaninja!` is sufficient, though `flag{scadaninja!}` follows the usual CTF aesthetic.)*

---

## 📘 Explanation — *Why It Works*

💡 **In short:**

1. The jump host is used by OT engineers and contains **SCADA and PLC artifacts**.
2. OT systems often take **filesystem/database backups**, which get stored locally.
3. Inside `.backup`, we found:

   * SCADA configs
   * PLC programs
   * MySQL database dumps
4. The SCADA database dump (`scada_db_backup.sql`) includes a **`users` table** with hashed passwords.
5. By extracting the hashes and cracking them offline with standard tools/wordlists, we recover a **valid application password** used by an OT engineer: `scadaninja!`.

This mimics a **real-world attack path**:

> Compromise an engineer → pivot to jump host → loot backups → extract app/DB creds → pivot deeper into OT environment.

---

## 🧰 Tools & Techniques Used

| 🧩 Tool / Language          | 💡 Purpose                                  |
| --------------------------- | ------------------------------------------- |
| `ls`, `cat`, `find` (Linux) | Enumerate filesystem, inspect backups/files |
| MySQL dump parsing          | Identify `users` table and hashed passwords |
| Hashcat / John              | Crack MD5 hashes from SCADA DB              |
| Wordlist (e.g. rockyou)     | Recover weak / themed passwords             |

---

## 📚 Key Learnings

| 🔑 Concept             | 🧠 Takeaway                                                                |
| ---------------------- | -------------------------------------------------------------------------- |
| OT/SCADA footprints    | OT jump hosts often hold configs, backups, and DB dumps in plain sight.    |
| Backups as goldmines   | `.backup` / `var/lib/mysql` / `data/historian` are high-value targets.     |
| Hash cracking          | Application passwords are often MD5’d and easily crackable with wordlists. |
| Lateral movement in OT | Engineer accounts and service creds are key pivot points into OT.          |

---

## 💬 Final Thoughts

> ✨ This challenge is a great example of how **host forensics + basic DB knowledge + hash cracking** can yield powerful credentials in an OT environment.
> It’s not always about fancy exploits — often it’s about **looking where admins leave their backups** and understanding what those files represent.

Another flag captured — **SCADA ninja unlocked** 🥷⚡

---

## 🧾 Optional: Reusable Writeup Footer (for GitHub)

```markdown
---
⭐ Author: Mathieu N.  
🕒 Date: December 2025  
🏆 CTF Event: RTIOC – December CTF  
📍 Category: Forensics / OT / Misc
---
```