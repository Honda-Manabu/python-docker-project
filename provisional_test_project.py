import pytest

import json
from botocore.exceptions import ClientError
import project

@pytest.fixture
def contact_data():
    return {
        "ja": {
            "title": "お問い合わせ",
            "name": "お名前",
            "email": "メールアドレス",
            "subject": "件名",
            "message": "お問い合わせ内容",
        },
        "en": {
            "title": "Contact",
            "name": "Name",
            "email": "Email",
            "subject": "Subject",
            "message": "Message",
        },
    }

@pytest.fixture
def app(monkeypatch, contact_data):

    captured_app = {}

    def fake_run(self, debug=True):
        captured_app["app"] = self

    monkeypatch.setattr(project.Flask, "run", fake_run)


    project.start_web_app(contact_data)

    return captured_app["app"]


@pytest.fixture
def client(app):

    return app.test_client()


def test_load_contact_data():
    data = project.load_contact_data()

    assert isinstance(data, dict)

    assert "ja" in data
    assert "en" in data


def test_start_web_app_page(client):
    response = client.get("/")

    assert response.status_code == 200

    assert response.data

def test_send_contact_success(client, monkeypatch):
    def fake_send_mail(subject, body, recipient):
        assert subject == "[お問い合わせ] テスト件名"

        assert "名前: テスト太郎" in body
        assert "メール: test@example.com" in body
        assert "件名: テスト件名" in body
        assert "本文です" in body

        assert recipient == project.CONTACT_RECIPIENT_EMAIL

        return {
            "success": True,
            "message_id": "test-message-id",
        }

    monkeypatch.setattr(project, "send_mail", fake_send_mail)

    response = client.post(
        "/contact_send",
        json={
            "name": "テスト太郎",
            "email": "test@example.com",
            "subject": "テスト件名",
            "message": "本文です",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["message"] == "メールが送信されました。"


def test_send_contact_fields_missing(client):
    response = client.post(
        "/contact_send",
        json={
            "name": "",
            "email": "test@example.com",
            "subject": "テスト",
            "message": "",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == "Required fields are missing."

def test_send_mail_error(client, monkeypatch):
    def fake_send_mail(subject, body, recipient):
        return {
            "success": False,
            "error": "SES送信エラー",
        }

    monkeypatch.setattr(project, "send_mail", fake_send_mail)

    response = client.post(
        "/contact_send",
        json={
            "name": "テスト太郎",
            "email": "test@example.com",
            "subject": "テスト件名",
            "message": "本文です",
        },
    )

    assert response.status_code == 500

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == "SES送信エラー"


def test_send_mail_success(monkeypatch):
    class FakeSESClient:
        def send_email(self, **kwargs):

            assert kwargs["Source"] == "from@example.com"
            assert kwargs["ReturnPath"] == "from@example.com"

            assert kwargs["Destination"] == {
                "ToAddresses": ["to@example.com"]
            }

            assert kwargs["Message"]["Subject"]["Data"] == "テスト件名"
            assert kwargs["Message"]["Subject"]["Charset"] == "UTF-8"

            assert kwargs["Message"]["Body"]["Text"]["Data"] == "テスト本文"
            assert kwargs["Message"]["Body"]["Text"]["Charset"] == "UTF-8"

            return {
                "MessageId": "test-message-id"
            }

    def fake_boto3_client(
        service_name,
        region_name,
        aws_access_key_id,
        aws_secret_access_key,
    ):
        assert service_name == "ses"
        assert region_name == "ap-northeast-1"
        assert aws_access_key_id == "test-access-key"
        assert aws_secret_access_key == "test-secret-key"

        return FakeSESClient()

    monkeypatch.setattr(project.boto3, "client", fake_boto3_client)
    monkeypatch.setenv("AWS_SES_REGION", "ap-northeast-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test-access-key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test-secret-key")
    monkeypatch.setenv("AWS_SES_FROM", "from@example.com")

    result = project.send_mail(
        subject="テスト件名",
        body="テスト本文",
        recipient="to@example.com",
    )

    assert result["success"] is True
    assert result["message_id"] == "test-message-id"

def test_send_mail_client_error(monkeypatch):
    class FakeSESClient:
        def send_email(self, **kwargs):
            raise ClientError(
                {
                    "Error": {
                        "Code": "MessageRejected",
                        "Message": "Email address is not verified.",
                    }
                },
                "SendEmail",
            )

    def fake_boto3_client(
        service_name,
        region_name,
        aws_access_key_id,
        aws_secret_access_key,
    ):
        return FakeSESClient()

    monkeypatch.setattr(project.boto3, "client", fake_boto3_client)
    monkeypatch.setenv("AWS_SES_REGION", "ap-northeast-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test-access-key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test-secret-key")
    monkeypatch.setenv("AWS_SES_FROM", "from@example.com")

    result = project.send_mail(
        subject="テスト件名",
        body="テスト本文",
        recipient="to@example.com",
    )

    assert result["success"] is False
    assert result["error"] == "Email address is not verified."


def test_switch_language_ja(client):
    response = client.post(
        "/switch_language",
        json={"lang": "ja"},
    )

    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "success"
    assert data["lang"] == "ja"
    assert "data" in data


def test_switch_language_invalid(client):
    response = client.post(
        "/switch_language",
        json={"lang": "fr"},
    )

    assert response.status_code == 400

    data = response.get_json()
    assert data["status"] == "error"
    assert data["message"] == "Unsupported language"
