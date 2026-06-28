import imaplib
import email
from email.header import decode_header
import time
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

# ---------- Configuration ----------
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASS")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not all([EMAIL, PASSWORD, BOT_TOKEN, CHAT_ID]):
    raise Exception("❌ Please set all variables in .env file!")

IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
SENT_FILE = "sent_alerts.txt"

# ---------- Send message to Telegram ----------
def send_telegram_message(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ Message sent to Telegram.")
        else:
            print(f"⚠️ Send error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

# ---------- Connect to email ----------
def connect_to_email():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")
        print("✅ Connected to email.")
        return mail
    except Exception as e:
        print(f"❌ Email connection error: {e}")
        return None

# ---------- Detect real Instagram security alerts ----------
def is_security_email(subject, body):
    """
    Detect real Instagram security alerts
    Returns: (boolean, reason)
    """
    subject_lower = subject.lower()
    body_lower = body.lower()
    full_text = f"{subject_lower} {body_lower}"
    
    # ========== Blacklist (Definitely not security) ==========
    # These are never security-related
    not_security = [
        "new posts", "new post", "see new posts", "tiene publicaciones nuevas",
        "now is easier", "ahora es más fácil", "volver a acceder",
        "suggested for you", "people you may know", "reels", "stories",
        "top posts", "popular", "trending", "followers", "unfollow",
        "liked your", "commented on your", "mentioned you",
        "welcome to", "verify your account", "complete your profile",
        "get the app", "download the app", "try new features",
        "your report", "your request", "thank you for your report"
    ]
    
    for word in not_security:
        if word in full_text:
            return False, f"Non-security email (keyword '{word}')"
    
    # ========== Whitelist (Definitely security) ==========
    # These indicate security alerts
    security_keywords = [
        "new login", "login from new device", "login attempt",
        "security alert", "unusual login", "unusual activity",
        "we detected", "your account was", "password changed",
        "email changed", "recovery email", "two-factor",
        "suspicious activity", "we blocked", "login from",
        "someone tried to", "access your account", "reset password"
    ]
    
    for keyword in security_keywords:
        if keyword in full_text:
            return True, f"Security alert (keyword '{keyword}')"
    
    return False, "Not detected"

# ---------- Extract information from email ----------
def extract_info(subject, body):
    info = {"country": "Unknown", "device": "Unknown", "ip": "Unknown", "time": "Unknown"}
    full_text = f"{subject} {body}"
    
    # Country patterns
    patterns = [
        r"(?:from|in|location|where|from country)\s*[:：]?\s*([A-Za-z]+(?:\s+[A-Za-z]+)?)\s*[.,]",
        r"logged in from\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)",
        r"ورود از\s*([A-Za-z]+(?:\s+[A-Za-z]+)?)",  # Persian: "Login from"
    ]
    for p in patterns:
        m = re.search(p, full_text, re.IGNORECASE)
        if m:
            info["country"] = m.group(1).strip()
            break
    
    # IP address
    ip = re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", full_text)
    if ip:
        info["ip"] = ip.group(0)
    
    # Device/browser
    device = re.search(r"(?:device|browser|platform)\s*[:：]?\s*([^\n,.]+)", full_text, re.IGNORECASE)
    if device:
        info["device"] = device.group(1).strip()
    
    # Time
    time_match = re.search(r"(?:time|date|at|when)\s*[:：]?\s*([^\n,.]+)", full_text, re.IGNORECASE)
    if time_match:
        info["time"] = time_match.group(1).strip()
    
    return info

# ---------- Load sent UIDs ----------
def load_sent_uids():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, "r") as f:
            return set(f.read().splitlines())
    return set()

def save_sent_uid(uid):
    with open(SENT_FILE, "a") as f:
        f.write(f"{uid}\n")

# ---------- Check emails ----------
def check_emails(mail, last_uid, sent_uids):
    try:
        result, data = mail.uid('search', None, f"UID {last_uid + 1}:*")
        if result != 'OK':
            return last_uid, sent_uids
        
        uids = data[0].split()
        if not uids:
            return last_uid, sent_uids
        
        for uid in uids:
            uid_str = uid.decode() if isinstance(uid, bytes) else str(uid)
            
            if uid_str in sent_uids:
                continue
            
            result, msg_data = mail.uid('fetch', uid, '(RFC822)')
            if result != 'OK':
                continue
            
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            subject, encoding = decode_header(msg.get("Subject", ""))[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8", errors="ignore")
            
            from_ = msg.get("From", "")
            if "instagram" not in from_.lower():
                continue
            
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if "attachment" not in str(part.get("Content-Disposition")):
                        try:
                            body += part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        except:
                            pass
            else:
                try:
                    body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                except:
                    body = ""
            
            # Check if it's a security alert
            is_security, reason = is_security_email(subject, body)
            
            if is_security:
                info = extract_info(subject, body)
                alert_msg = (
                    f"🔴 **Instagram Security Alert!**\n"
                    f"📧 Subject: {subject}\n"
                    f"📍 Country: {info['country']}\n"
                    f"💻 Device: {info['device']}\n"
                    f"🌐 IP: {info['ip']}\n"
                    f"⏰ Time: {info['time']}\n\n"
                    f"⚠️ If this wasn't you, change your password immediately!"
                )
                send_telegram_message(alert_msg)
                print(f"✅ Alert sent: {subject} ({reason})")
                sent_uids.add(uid_str)
                save_sent_uid(uid_str)
            else:
                print(f"⏭️ Skipped: {subject} ({reason})")
            
            if int(uid) > last_uid:
                last_uid = int(uid)
        
        return last_uid, sent_uids
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return last_uid, sent_uids

# ---------- Main loop ----------
if __name__ == "__main__":
    print("🛡️ Security Bot (precise filter version)")
    mail = connect_to_email()
    if not mail:
        exit()
    
    sent_uids = load_sent_uids()
    print(f"📋 Previous alerts: {len(sent_uids)}")
    
    last_uid = 0
    send_telegram_message("🛡️ Email alert bot activated!")
    
    while True:
        try:
            if not mail:
                mail = connect_to_email()
                if not mail:
                    time.sleep(60)
                    continue
            last_uid, sent_uids = check_emails(mail, last_uid, sent_uids)
        except Exception as e:
            print(f"❌ Error: {e}")
            mail = None
        time.sleep(120)
