import smtplib
import os
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
MAIL_TO = os.getenv("MAIL_TO", "")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")


def _build_body(results, source_type):
    lines = [f"【{source_type}スクレイピング結果】\n"]
    for r in results:
        name = r.get("name", "")
        failures = r.get("failures", [])
        releases = r.get("releases", [])
        if not failures and not releases:
            continue
        lines.append(f"\n■ {name} ({r.get('url', '')})")
        if failures:
            lines.append("  [障害情報]")
            for item in failures:
                lines.append(f"    - {item['title']} : {item['url']}")
        if releases:
            lines.append("  [リリース情報]")
            for item in releases:
                lines.append(f"    - {item['title']} : {item['url']}")
    return "\n".join(lines)


def send_mail(results, source_type):
    if not SMTP_USER or not MAIL_TO:
        return False, "メール設定が未完了ですわ"
    body = _build_body(results, source_type)
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = MAIL_TO
    msg["Subject"] = f"[情報収集] {source_type} スクレイピング結果"
    msg.attach(MIMEText(body, "plain", "utf-8"))
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, MAIL_TO, msg.as_string())
        return True, "メール送信成功"
    except Exception as e:
        return False, str(e)


def send_slack(results, source_type):
    if not SLACK_WEBHOOK_URL:
        return False, "Slack Webhook URLが未設定ですわ"
    body = _build_body(results, source_type)
    try:
        res = requests.post(SLACK_WEBHOOK_URL, json={"text": body}, timeout=10)
        res.raise_for_status()
        return True, "Slack送信成功"
    except Exception as e:
        return False, str(e)
