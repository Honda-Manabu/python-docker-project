import threading

import pytest
from werkzeug.serving import make_server

import project


@pytest.fixture(scope="module")
def live_server():
    """Start the Flask server for testing."""

    contact_data = project.load_contact_data()
    app = project.create_app(contact_data)

    server = make_server("127.0.0.1", 5001, app)

    thread = threading.Thread(
        target=server.serve_forever
    )

    thread.start()

    yield "http://127.0.0.1:5001"

    server.shutdown()
    thread.join()


@pytest.fixture
def page(playwright, live_server):
    """Create a Playwright browser page."""

    browser = playwright.chromium.launch(
        headless=True
    )

    page = browser.new_page()

    page.goto(live_server, wait_until="networkidle")

    yield page

    browser.close()

def test_contact_send_integration(page, monkeypatch):
    """Perform an integration test from the browser to `/contact_send`"""

    def fake_send_mail(subject, body, recipient):
        assert subject == "[お問い合わせ] 統合テスト"
        assert "名前: テスト太郎" in body
        assert "メール: test@example.com" in body
        assert "件名: 統合テスト" in body
        assert "統合テスト本文" in body
        assert recipient == project.CONTACT_RECIPIENT_EMAIL

        return {
            "success": True,
            "message_id": "integration-test-message",
        }

    monkeypatch.setattr(
        project,
        "send_mail",
        fake_send_mail
    )

    page.click("#lang-btn-ja")

    page.wait_for_function(
        "() => document.querySelector('#contact-heading').innerText !== ''"
    )

    page.fill("#field-name", "テスト太郎")
    page.fill("#field-email", "test@example.com")
    page.fill("#field-subject", "統合テスト")
    page.fill("#field-message", "統合テスト本文")

    page.click("#btn-send")

    page.wait_for_selector(
        "#form-response-area",
        state="visible"
    )
