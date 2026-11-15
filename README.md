# ⚡ Telegram Chat & Account Cleaner (v2.5 PRO MAX)
### 👑 Author: **mnhatrealz**

```text
  ███╗   ███╗███╗   ██╗██╗  ██╗ █████╗ ████████╗██████╗ ███████╗ █████╗ ██╗     ███████╗
  ████╗ ████║████╗  ██║██║  ██║██╔══██╗╚══██╔══╝██╔══██╗██╔════╝██╔══██╗██║     ╚══███╔╝
  ██╔████╔██║██╔██╗ ██║███████║███████║   ██║   ██████╔╝█████╗  ███████║██║       ███╔╝ 
  ██║╚██╔╝██║██║╚██╗██║██╔══██║██╔══██║   ██║   ██╔══██╗██╔══╝  ██╔══██║██║      ███╔╝  
  ██║ ╚═╝ ██║██║ ╚████║██║  ██║██║  ██║   ██║   ██║  ██║███████╗██║  ██║███████╗███████╗
  ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝
```

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Telethon MTProto](https://img.shields.io/badge/Telethon-MTProto%201.45%2B-cyan.svg)](https://github.com/LonamiWebs/Telethon)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Anti-Ban Protection](https://img.shields.io/badge/Protection-Anti--Ban%20%26%20SpamBot-brightgreen.svg)]()
[![Multi-Account](https://img.shields.io/badge/Multi--Account-Profile%20Isolation-orange.svg)]()
[![Bilingual](https://img.shields.io/badge/Languages-English%20%7C%20Ti%E1%BA%BFng%20Vi%E1%BB%87t-yellow.svg)]()

A high-performance, asynchronous Python automation tool built with **Telethon** (official Telegram MTProto protocol). Designed to clean up cluttered Telegram accounts at blazing speeds: leave bulk groups/channels, wipe spam bots, delete private 1-on-1 chats, filter dead/inactive groups, purge synced contacts, and bypass Telegram SpamBot detection with state-of-the-art velocity controls.

---

## 🌟 Key Features

| Feature | Description |
| :--- | :--- |
| 🔍 **Keyword-Based Spam Filter** | Automatically targets and leaves groups/channels containing spam keywords (`crypto`, `casino`, `bet`, `18+`, `trading`, `scam`, `giveaway`, etc.). Supports custom keyword input. |
| 💤 **Dead / Inactive Groups Cleaner** | Calculates the timestamp of the last message in each group and leaves inactive groups older than 30, 60, 90, 180 days (or custom threshold). |
| 📇 **Telegram Contacts Cleaner** | Address book cleanup tool: bulk-delete ghost/deleted accounts (`Deleted Account`) or completely wipe synced contacts with a single click. |
| 👤 **Multi-Account Profile Isolation** | Manage multiple Telegram accounts seamlessly. Sessions are saved in isolated profiles under `sessions/` with zero cross-contamination. |
| 🔒 **Guest / Temporary Mode** | Log in without saving the session on disk. Sessions are automatically purged upon exit for public or shared machines. |
| 💬 **Direct Chat Deletion & Bot Blocker** | Wipes 1-on-1 conversations (both sides where possible) and sends permanent `Block` requests to bots to prevent future spam. |
| 💣 **Account Nuke Mode (Clean Slate)** | Leaves all groups and channels, blocks all bots, and deletes all 1-on-1 chats in one streamlined pass. |
| 🌐 **Bilingual Interface (EN / VI)** | Full dual-language support: switch between **English** and **Tiếng Việt** instantly from the menu. |
| 🛡️ **Anti-Ban Velocity Safeguards** | Features randomized jitter delays (1.5s - 3.0s), batch cooling intervals, intelligent `FloodWaitError` countdowns, and automatic `PeerFloodError` emergency halts. |
| 👑 **Admin & Owner Safeguards** | Protects your owned groups and administrator privileges from accidental departure. |
| 📋 **Whitelist Protection** | Specify critical groups or channels in `whitelist.txt` (by Chat ID or `@username`) to permanently exempt them. |
| 👁️ **Dry-Run Inspection Mode** | Preview the full list and quantity of matching dialogs without executing any leave or delete actions. |

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- **Python 3.8+** installed on your system.
- Git (optional, for cloning).

### 2. Install Dependencies
Open Terminal / PowerShell / Command Prompt in the repository folder and run:
```bash
pip install -r requirements.txt
```

### 3. Obtain Telegram API Credentials (One-time Setup)
Telegram MTProto requires your own `API ID` and `API HASH`:
1. Log in with your phone number at: **[https://my.telegram.org](https://my.telegram.org)**.
2. Click on **API development tools**.
3. Enter any application title and short name, then click **Create application**.
4. Copy the two generated values:
   - **`App api_id`** (numbers, e.g. `24787002`)
   - **`App api_hash`** (32-character hex string, e.g. `fd0fb6a5ab0497d2abdcaf59ecf9dfbc`)

---

## 🚀 Running the Tool

### Quick Launch
- **Windows:** Double-click [`run.bat`](run.bat).
- **Cross-Platform (CLI):**
  ```bash
  python auto_leave_telegram.py
  ```

On first launch, you will be prompted to enter your `API ID` and `API HASH`. They will be securely saved in your local `config.json` so you never have to re-enter them.

---

## 📋 Interactive Menu Overview

```text
 [1] 🔴 Leave GROUPS only (Groups & Supergroups) - Keep Channels & DMs
 [2] 📢 Leave CHANNELS only (Broadcast Channels) - Keep Groups & DMs
 [3] ⚡ Leave BOTH Groups & Channels - Keep Direct Messages
 [4] 💬 DELETE DIRECT CHATS (1-1 Messages & Block + Wipe Bots)
 [5] 💣 NUKE EVERYTHING (Leave Groups + Channels + Wipe Chats & Bots - CLEAN SLATE)
 [6] 🔍 LEAVE GROUPS BY SPAM KEYWORDS (Keyword Filter: crypto, casino, bet, 18+...)
 [7] 💤 LEAVE DEAD / INACTIVE GROUPS (No activity > 30, 60, 90 days)
 [8] 📇 CONTACTS CLEANER (Bulk wipe synced contacts & Deleted Accounts)
 [9] 👁️  Dry-Run Scan (Preview list, do NOT leave/delete)
 [L] 🌐 CHANGE LANGUAGE / ĐỔI NGÔN NGỮ (English / Tiếng Việt)
 [S] ⚙️  Safety Settings (Delay, Cooldown & API)
 [A] 🔄 SWITCH ACCOUNT (Return to account list)
 [X] 🗑️  LOG OUT CURRENT ACCOUNT (Remove session from this PC)
 [0] 🚪 Exit Program
```

*(Note: Telegram System Service Notifications `777000` and `Saved Messages` are permanently protected and will never be deleted).*

---

## ⚙️ Configuration Reference (`config.json`)

Settings can be modified either via the in-app settings menu (`[S]`) or by editing `config.json` directly:

```json
{
    "api_id": 24787002,
    "api_hash": "fd0fb6a5ab0497d2abdcaf59ecf9dfbc",
    "phone": "",
    "session_name": "tele_session",
    "language": "en",
    "min_delay_seconds": 1.5,
    "max_delay_seconds": 3.0,
    "batch_size": 15,
    "batch_cooldown_seconds": 30,
    "skip_admin_or_owned": true,
    "auto_flood_wait": true
}
```

### Parameter Details:
- `language`: Interface language (`"en"` for English, `"vi"` for Vietnamese).
- `min_delay_seconds` & `max_delay_seconds`: Randomized sleep interval between actions.
- `batch_size`: Number of chats to leave/delete before triggering a cooldown.
- `batch_cooldown_seconds`: Cooldown pause duration between batches.
- `skip_admin_or_owned`: Automatically bypasses groups/channels where you are Owner or Admin.
- `auto_flood_wait`: Automatically counts down Telegram `FloodWait` time limits and resumes.

---

## 🛡️ Whitelist Setup (`whitelist.txt`)

To ensure certain groups or channels are never touched, add their Chat IDs or `@usernames` to [`whitelist.txt`](whitelist.txt):

```text
# Example Chat ID:
-1001234567890

# Example @username:
@family_group
@important_news
```

---

## 🔒 Security & Privacy Notice

- **Local Storage Only:** All session data and API keys are stored strictly on your local machine.
- **Git Protection:** Your `.gitignore` is pre-configured to strictly ignore `config.json`, `sessions/`, and all `*.session` files. Your credentials will **never** be committed or leaked to remote repositories.
- **Zero Third-Party Telemetry:** This tool communicates directly with Telegram official MTProto servers via Telethon.

---

## 👨‍💻 Author & Contributions

- Developed with ❤️ by **[mnhatrealz](https://github.com/Mnhatrealz)**.
- Repository: [https://github.com/Mnhatrealz/telegram-chat-cleaner](https://github.com/Mnhatrealz/telegram-chat-cleaner)
- Feel free to submit Issues and Pull Requests!
