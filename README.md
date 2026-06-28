# Instagram-Security-Bot
Instagram Security Bot - Centralized Alert System (Email-Based, No Password Sharing)
# 🛡️ Instagram Security Alert Bot (Community Edition)

**A simple open-source bot that reads Instagram security alerts from your email and forwards them to Telegram in real-time.**

---

## ✨ Features

- ✅ **Automated Email Monitoring** – Checks your Gmail inbox every 2 minutes for Instagram security emails.
- ✅ **Smart Detection** – Distinguishes real security alerts (logins, password changes) from promotional emails (new posts, suggestions, etc.).
- ✅ **Information Extraction** – Pulls out country, IP address, device/browser, and time from each alert.
- ✅ **Telegram Notifications** – Sends instant alerts to your Telegram with all extracted details.
- ✅ **No Instagram Password Required** – Works entirely via email; completely legal and compliant with Instagram's terms.
- ✅ **Duplicate Prevention** – Keeps track of already-sent alerts so you never get spammed.
- ✅ **Lightweight & Open Source** – Runs on any computer with Python 3.8+.

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher installed on your system.
- A Gmail account (for reading alerts).
- A Telegram bot token (get one from [@BotFather](https://t.me/botfather)).

### 2. Clone the Repository
```bash
git clone https://github.com/mahdigamer-prog/instagram-security-bot-community.git
cd instagram-security-bot-community

### 3 Install Dependencies
pip install -r requirements.txt

### 4 Configure Environment Variables
Create a .env file in the project folder with the following content:

EMAIL=your-email@gmail.com
EMAIL_PASS=your-app-password
BOT_TOKEN=123456:ABC-DEF
CHAT_ID=123456789
-----------------------------------------
Important: Use an App Password for Gmail, not your main password.
Generate one at: Google Account → Security → App Passwords.

Run the Bot
python main.py

You'll see:
🛡️ Security Bot (precise filter version)
✅ Connected to email.
🛡️ Email alert bot activated!
----------------------------------------------------------------------
 How It Works
The bot connects to your Gmail via IMAP.

It fetches new emails from Instagram (based on the sender address).

It checks the subject and body against a blacklist (promotional keywords) and a whitelist (security keywords).

If a security alert is detected, it extracts:

🌍 Country (e.g., "Turkey", "Germany")

💻 Device/Browser (e.g., "Chrome on Windows")

🌐 IP Address

⏰ Time of the login attempt

It sends a formatted alert to your Telegram chat.

The UID of each processed email is saved to sent_alerts.txt to prevent duplicates.

📁 Project Structure
.
├── main.py    # Main bot script
├── requirements.txt     # Python dependencies
├── .env                 # Configuration (not committed)
├── sent_alerts.txt      # Tracks already-sent alerts
└── README.md            # This file

⭐ Pro Version (For Businesses)
This Community Edition is for individual users with one Instagram account.

If you need:

👥 Multi‑user support – Monitor multiple Instagram accounts for different clients.

🛡️ Admin panel – Manage users, view statistics, change plans.

📊 Alert history – Search and filter past alerts.

🔔 SMS & other messengers – Get alerts via SMS, WhatsApp, or Iranian messengers.

💼 White‑label branding – Rebrand the bot for your own company.

❓ FAQ
Q: Why do I need to give my email password?
A: The password is stored only in your local .env file and is never shared or transmitted anywhere. You can also use an App Password for extra security.

Q: Does this violate Instagram's terms?
A: No. The bot never logs into Instagram. It only reads emails that Instagram sends to you, which is completely legal.

Q: Can I use this with Outlook/Yahoo?
A: Currently only Gmail is supported (via IMAP). Support for other providers may be added in the future.

Q: How often does it check emails?
A: Every 2 minutes (120 seconds). You can change this by modifying the time.sleep(120) value in the code.


Contact us for the Pro version:
📧mahdi.gamer@gmail.com



