import sys
import os
import shutil
import argparse
import traceback
import logging
from operator import truediv
from pathlib import Path
from typing import Optional

# Import from translator.py
from translator import TranslatorManager, package, logger

# Import from iohandler.py
from iohandler import continuous_mode

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Argos Translate Utility")
    parser.add_argument("--reset",
                        action="store_true",
                        help="Force reset all installed models and data")
    parser.add_argument("--from-lang",
                        default="hu",
                        help="Source language code (default: hu)")
    parser.add_argument("--to-lang",
                        default="en",
                        help="Target language code (default: en)")
    parser.add_argument("--text",
                        default="Üdv világ, ez egy teszt fordítás!",
                        help="Text to translate")
    parser.add_argument("--continuous",
                        action="store_true",
                        help="Continuous mode (default: false)")
    parser.add_argument("--debug",
                        action="store_true",
                        help="Enable debug logging")

    return parser.parse_args()


def main():
    """Main entry point for the translation utility."""
    args = parse_arguments()
    print(f"Installed Packages location: {package.get_installed_packages()}")

    # Set debug level if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)

    translator_mgr = TranslatorManager()

    try:
        # Handle reset request if specified
        if args.reset:
            translator_mgr.force_reset()
            if args.text == "Hello, world! This is a test translation.":
                # If no specific translation was requested, exit after reset
                return

        # Initiate translation
        translator_mgr.install_model(args.from_lang, args.to_lang)
        translator = translator_mgr.create_translator(args.from_lang, args.to_lang)

        # Perform continuous translation
        if args.continuous:
            continuous_mode(translator, args)
        else:
            # Perform single translation
            result = translator_mgr.translate_text(
                args.text, args.from_lang, args.to_lang)

            # Display results
            print("\n" + "=" * 40)
            print(f"SOURCE [{args.from_lang}]: {args.text}")
            print(f"TARGET [{args.to_lang}]: {result}")
            print("=" * 40)

    except Exception as e:
        logger.error(f"Translation failed: {e}")
        if args.debug:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()