from botocore.exceptions import ClientError
from flask import Flask, render_template, request, jsonify
import json
import boto3
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CONTACT_RECIPIENT_EMAIL = "honda.m3742@icloud.com"

def main():
    contact_data = load_contact_data()
    start_web_app(contact_data)


def load_contact_data():
    """contact.jsonを読み込む"""
    json_path = Path(__file__).parent / "static" / "contact.json"

    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def start_web_app(contact_data):
    """Webページを起動する"""
    app = create_app(contact_data)
    app.run(debug=True)

def create_app(contact_data):
    """Flaskアプリを作成する"""
    app = Flask(__name__,
        template_folder=Path(__file__).parent
    )

    @app.route("/")
    def contact_page():
        return render_template(
            "contact.html",
            contact_data=contact_data
        )

    @app.route("/contact_send", methods=["POST"])
    def contact_send():
        return send_contact(contact_data)

    @app.route("/switch_language", methods=["POST"])
    def language_switch():
        return switch_language(contact_data)

    return app


def send_contact(contact_data):
    """お問い合わせフォームを処理する"""
    data = request.get_json()

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    subject = data.get("subject", "").strip()
    message = data.get("message", "").strip()
    lang = data.get("lang", "en")

    if not name or not email or not message:
        return jsonify({
            "status": "error",
            "message": "Required fields are missing."
        }), 400
    if lang not in contact_data:
        lang = "en"
    email_body = (
        f"名前: {name}\n"
        f"メール: {email}\n"
        f"件名: {subject}\n\n"
        f"{message}"
    )

    result = send_mail(
        subject=f"[お問い合わせ] {subject}",
        body=email_body,
        recipient=CONTACT_RECIPIENT_EMAIL,
    )

    if result["success"]:
        return jsonify({
            "status": "success",
            "message": contact_data[lang]["successMsg"]
        })

    return jsonify({
        "status": "error",
        "message": result["error"]
    }), 500


def send_mail(subject, body, recipient):
    """Amazon SESでメールを送信する"""

    client = boto3.client(
        "ses",
        region_name=os.environ["AWS_SES_REGION"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )

    try:
        response = client.send_email(
            Source=os.environ["AWS_SES_FROM"],
            ReturnPath=os.environ["AWS_SES_FROM"],
            Destination={
                "ToAddresses": [recipient],
            },
            Message={
                "Subject": {
                    "Data": subject,
                    "Charset": "UTF-8",
                },
                "Body": {
                    "Text": {
                        "Data": body,
                        "Charset": "UTF-8",
                    }
                },
            },
        )

        return {
            "success": True,
            "message_id": response["MessageId"],
        }

    except ClientError as e:
        return {
            "success": False,
            "error": e.response["Error"]["Message"],
        }

def switch_language(contact_data):
    """表示言語を切り替える"""
    data = request.get_json()
    lang = data.get("lang", "en")

    if lang not in contact_data:
        return jsonify({
            "status": "error",
            "message": "Unsupported language"
        }), 400

    return jsonify({
        "status": "success",
        "lang": lang,
        "data": contact_data[lang]
    })


if __name__ == "__main__":
    main()
