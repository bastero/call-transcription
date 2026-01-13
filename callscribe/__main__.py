"""Main entry point for CallScribe package."""

import sys


def main():
    """Route to appropriate interface based on arguments."""
    if len(sys.argv) > 1 and sys.argv[1] == 'gui':
        # Launch web GUI
        from callscribe.web.gui import main as gui_main
        # Remove 'gui' from argv so argparse works correctly
        sys.argv.pop(1)
        gui_main()
    else:
        # Launch CLI
        from callscribe.main import main as cli_main
        cli_main()


if __name__ == "__main__":
    main()
