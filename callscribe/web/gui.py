"""GUI launcher for CallScribe web interface."""

import argparse
import webbrowser
import threading
import time
from callscribe.web.app import run_server, get_local_ip


def open_browser(host, port, delay=1.5):
    """Open browser after a short delay."""
    time.sleep(delay)
    url = f"http://localhost:{port}" if host == '0.0.0.0' else f"http://{host}:{port}"
    print(f"Opening browser: {url}")
    webbrowser.open(url)


def main():
    """Main entry point for GUI."""
    parser = argparse.ArgumentParser(description="CallScribe Web Interface")

    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0 for network access)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=3000,
        help="Port to run on (default: 3000)"
    )

    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't automatically open browser"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in debug mode"
    )

    args = parser.parse_args()

    # Open browser in background thread
    if not args.no_browser:
        browser_thread = threading.Thread(
            target=open_browser,
            args=(args.host, args.port),
            daemon=True
        )
        browser_thread.start()

    # Start server
    run_server(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
