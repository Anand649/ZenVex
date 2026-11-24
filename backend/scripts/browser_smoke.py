"""Exercise the built React app served by FastAPI with synthetic inputs."""

import os
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright


def check_unavailable_then_retry(page, endpoint, submit):
    # Intercept only the scan request so retry still exercises the real backend.
    def unavailable(route):
        route.fulfill(status=503, json={"detail": "Scan service temporarily unavailable"})

    page.route(endpoint, unavailable)
    try:
        submit.click()
        expect(page.get_by_text("Scan service temporarily unavailable", exact=True)).to_be_visible()
        expect(submit).to_be_enabled()
    finally:
        page.unroute(endpoint, unavailable)

    with page.expect_response(endpoint) as response:
        submit.click()
    assert response.value.ok
    return response.value.json()


def main():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    with subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)]
    ) as server:
        try:
            for _ in range(100):
                try:
                    with urlopen(f"{base}/health", timeout=1):
                        break
                except OSError:
                    if server.poll() is not None:
                        raise RuntimeError("Uvicorn exited before becoming ready")
                    time.sleep(0.1)
            else:
                raise RuntimeError("Uvicorn did not become ready")

            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel=os.getenv("ZENVEX_BROWSER_CHANNEL"))
                page = browser.new_page(viewport={"width": 1440, "height": 900})
                page.goto(base)
                navigation = page.get_by_role("navigation")
                navigation.get_by_role("button", name="Message Scanner").click()
                page.get_by_placeholder("Paste the suspicious message", exact=False).fill(
                    "😀 Update your KYC immediately: https://example.invalid"
                )
                report = check_unavailable_then_retry(
                    page, f"{base}/api/v1/scan/text",
                    page.get_by_role("button", name="Execute Threat Analysis"),
                )
                assert report["input_type"] == "text"
                expect(page.locator("mark").filter(has_text="https://example.invalid")).to_have_text(
                    "https://example.invalid"
                )

                navigation.get_by_role("button", name="URL Intelligence").click()
                page.get_by_placeholder("Enter suspicious link", exact=False).fill("https://example.invalid")
                report = check_unavailable_then_retry(
                    page, f"{base}/api/v1/scan/url", page.get_by_role("button", name="Inspect URL"),
                )
                assert report["input_type"] == "url"
                assert report["urls"][0]["reputation_checked"] is False
                expect(page.get_by_role("heading", name="Analyzed Content & Extracted Signatures")).to_be_visible()
                browser.close()
        finally:
            server.terminate()


if __name__ == "__main__":
    main()
