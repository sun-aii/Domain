import os
import time
import requests
import dns.resolver
import smtplib

from datetime import datetime
from email.mime.text import MIMEText


DOMAINS = os.getenv(
    "DOMAINS",
    "xxx.com,xxx.xyz,xxx.top"
).split(",")


INTERVAL = int(
    os.getenv(
        "INTERVAL",
        "60"
    )
)


SMTP_SERVER = os.getenv(
    "SMTP_SERVER",
    "smtp.qq.com"
)


SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "465"
    )
)


MAIL_USER = os.getenv("MAIL_USER")
MAIL_PASS = os.getenv("MAIL_PASS")
MAIL_TO = os.getenv("MAIL_TO")


NOTIFY_FILE = "notified.txt"


def load_notified():

    if not os.path.exists(NOTIFY_FILE):
        return set()

    with open(
        NOTIFY_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return set(
            line.strip()
            for line in f.readlines()
            if line.strip()
        )


def save_notified(domain):

    with open(
        NOTIFY_FILE,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(domain + "\n")

def send_mail(title, content):

    if not MAIL_USER or not MAIL_PASS or not MAIL_TO:

        print("邮箱配置为空，跳过发送")

        return


    msg = MIMEText(
        content,
        "plain",
        "utf-8"
    )


    msg["Subject"] = title
    msg["From"] = MAIL_USER
    msg["To"] = MAIL_TO


    try:

        server = smtplib.SMTP_SSL(
            SMTP_SERVER,
            SMTP_PORT
        )


        server.login(
            MAIL_USER,
            MAIL_PASS
        )


        server.sendmail(
            MAIL_USER,
            MAIL_TO,
            msg.as_string()
        )


        server.quit()


        print("邮件发送成功")


    except Exception as e:

        print(
            "邮件发送失败:",
            e
        )



def check_rdap(domain):

    try:

        url = (
            "https://rdap.centralnic.com/xyz/domain/"
            + domain
        )


        response = requests.get(
            url,
            timeout=10
        )


        if response.status_code == 404:

            return True


    except Exception as e:

        print(
            "RDAP错误:",
            e
        )


    return False



def check_dns(domain):

    try:

        dns.resolver.resolve(
            domain,
            "NS"
        )

        return False


    except:

        return True



def check_domain(domain, notified_domains):


    domain = domain.strip()


    rdap_status = check_rdap(domain)

    dns_status = check_dns(domain)



    print(
        datetime.now(),
        "|",
        domain,
        "| RDAP:",
        rdap_status,
        "| DNS:",
        dns_status
    )



    # RDAP确认不存在，并且没有提醒过

    if rdap_status and domain not in notified_domains:


        message = f"""
🚨 XYZ域名释放提醒

域名:
{domain}

时间:
{datetime.now()}

RDAP:
{rdap_status}

DNS:
{dns_status}

请立即检查注册！
"""


        send_mail(
            "🚨 域名释放提醒 " + domain,
            message
        )


        save_notified(domain)

        notified_domains.add(domain)

# =====================
# 启动
# =====================

notified_domains = load_notified()


print("======================")
print("Domain Monitor Started")
print("Domains:", DOMAINS)
print("Interval:", INTERVAL, "seconds")
print("======================")


while True:


    for domain in DOMAINS:

        check_domain(
            domain,
            notified_domains
        )


    time.sleep(INTERVAL)
