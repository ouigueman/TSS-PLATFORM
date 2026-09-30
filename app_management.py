# app_management.py
import subprocess
import time
import requests
import sys
import os
import signal

# ========== CONFIGURATION ==========
MAIN_APP_FILE = "app.py"
MAIN_APP_Name = "TSS Platform"
MAIN_APP_PORT = 5000
MANAGEMENT_PORT = 5111
CHECK_INTERVAL = 15               # Seconds between checks
HEALTH_CHECK_PATH = "/"           # Change to "/health" if your app has that route
HEALTH_CHECK_TIMEOUT = 10         # Increased from 5 — gives app more time to respond
RESTART_WAIT = 8                  # Seconds to wait after launching before checking
CONFIRM_DOWN_CHECKS = 2           # Must fail THIS many checks in a row before alerting
TELEGRAM_BOT_TOKEN = "8716536042:AAGZsFb-QF_5BQD5Bvfmc908_BXPxcasyCM"
TELEGRAM_CHAT_ID = "-1003975805335"
# ===================================

main_process = None
consecutive_failures = 0          # Tracks how many checks in a row have failed


def send_telegram_message(message):
    """Send alert message via Telegram bot"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("[✓] Telegram alert sent successfully")
        else:
            print(f"[✗] Failed to send Telegram alert: {response.text}")
    except Exception as e:
        print(f"[✗] Error sending Telegram message: {e}")


def is_app_running(port):
    """
    Check if the main app is responding on the specified port.

    Key fixes vs original:
    - Accepts ANY HTTP response (including 4xx/5xx) as proof the server is up.
      A 404 or 500 still means the process is alive and listening — only a
      ConnectionError or Timeout means it's truly down.
    - Timeout raised to HEALTH_CHECK_TIMEOUT so a slow-starting app isn't
      wrongly declared dead.
    """
    try:
        response = requests.get(
            f"http://localhost:{port}{HEALTH_CHECK_PATH}",
            timeout=HEALTH_CHECK_TIMEOUT,
            allow_redirects=True
        )
        # ANY HTTP response means the server is alive.
        # Even a 404/500 proves the process is listening on the port.
        return True
    except requests.exceptions.ConnectionError:
        # Nothing listening on that port at all.
        return False
    except requests.exceptions.Timeout:
        # Server didn't reply in time — count as down.
        return False
    except Exception as e:
        print(f"[!] Unexpected error checking app status: {e}")
        return False


def start_main_app():
    """Start the main app.py using subprocess"""
    global main_process
    try:
        print(f"[*] Starting {MAIN_APP_Name} on port {MAIN_APP_PORT}...")

        # Kill anything already squatting on that port before starting fresh.
        kill_existing_process_on_port(MAIN_APP_PORT)

        main_process = subprocess.Popen(
            [sys.executable, MAIN_APP_FILE],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        print(f"[*] Waiting {RESTART_WAIT}s for app to initialise...")
        time.sleep(RESTART_WAIT)

        if is_app_running(MAIN_APP_PORT):
            message = (
                f"✅ <b>App Restarted Successfully</b>\n\n"
                f"{MAIN_APP_Name} is now running on port {MAIN_APP_PORT}"
            )
            send_telegram_message(message)
            print("[✓] Main app started successfully")
            return True
        else:
            # Grab stderr output to help diagnose startup failures
            stderr_output = ""
            if main_process.poll() is not None:
                _, err = main_process.communicate(timeout=2)
                stderr_output = err.decode(errors="replace")[-500:]  # last 500 chars

            print(f"[✗] App started but not responding on port {MAIN_APP_PORT}")
            if stderr_output:
                print(f"[✗] App stderr: {stderr_output}")
            return False

    except Exception as e:
        error_msg = f"❌ <b>Failed to start app</b>\n\nError: {str(e)}"
        send_telegram_message(error_msg)
        print(f"[✗] Error starting main app: {e}")
        return False


def kill_existing_process_on_port(port):
    """Kill any process using the specified port"""
    try:
        result = subprocess.run(
            f"lsof -ti:{port} | xargs kill -9",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"[*] Killed existing process on port {port}")
    except Exception:
        pass


def main():
    global consecutive_failures

    print("=" * 50)
    print("App Management Monitor")
    print(f"Monitoring: {MAIN_APP_FILE} on port {MAIN_APP_PORT}")
    print(f"Check interval: {CHECK_INTERVAL}s | Confirm-down threshold: {CONFIRM_DOWN_CHECKS} checks")
    print("=" * 50)

    # Initial startup
    if not is_app_running(MAIN_APP_PORT):
        print("[!] Main app is not running. Starting it now...")
        start_main_app()
    else:
        print("[✓] Main app is already running")

    # Monitoring loop
    while True:
        try:
            if not is_app_running(MAIN_APP_PORT):
                consecutive_failures += 1
                print(
                    f"[!] Check failed ({consecutive_failures}/{CONFIRM_DOWN_CHECKS}) "
                    f"at {time.strftime('%Y-%m-%d %H:%M:%S')}"
                )

                if consecutive_failures >= CONFIRM_DOWN_CHECKS:
                    # Confirmed down — alert and restart
                    print(f"[!] {MAIN_APP_Name} confirmed DOWN. Restarting...")
                    send_telegram_message(
                        f"⚠️ <b>ALERT: App is DOWN</b>\n\n"
                        f"{MAIN_APP_Name} failed {CONFIRM_DOWN_CHECKS} consecutive checks "
                        f"on port {MAIN_APP_PORT}\nAttempting to restart..."
                    )

                    if start_main_app():
                        print("[✓] Restart successful")
                        consecutive_failures = 0
                    else:
                        print("[✗] Restart failed. Manual intervention may be needed")
                        send_telegram_message(
                            f"🔥 <b>CRITICAL: Manual intervention needed</b>\n\n"
                            f"Failed to restart {MAIN_APP_Name}"
                        )
                else:
                    print(f"[!] Waiting for next check to confirm before alerting...")

            else:
                if consecutive_failures > 0:
                    print(f"[✓] App recovered after {consecutive_failures} failed check(s)")
                    consecutive_failures = 0
                print(f"[✓] {MAIN_APP_Name} is healthy at {time.strftime('%H:%M:%S')}")

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n[*] Shutting down app management...")
            if main_process:
                main_process.terminate()
            sys.exit(0)
        except Exception as e:
            error_msg = f"⚠️ <b>Management App Error</b>\n\n{str(e)}"
            send_telegram_message(error_msg)
            print(f"[!] Unexpected error: {e}")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        from flask import Flask
        import threading

        management_app = Flask(__name__)

        @management_app.route('/health')
        def health():
            return "Management App is running", 200

        def run_management_server():
            management_app.run(port=MANAGEMENT_PORT, host='0.0.0.0', use_reloader=False)

        server_thread = threading.Thread(target=run_management_server, daemon=True)
        server_thread.start()
        print(f"[*] Management health check available on port {MANAGEMENT_PORT}")
    except ImportError:
        print("[!] Flask not installed - skipping management health endpoint")
    except Exception as e:
        print(f"[!] Could not start management server: {e}")

    main()
