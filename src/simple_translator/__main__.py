# translator.py (unchanged; no modifications needed here)
from argostranslate import package, translate
import sys
import os
import shutil
import argparse
import traceback
import logging
from pathlib import Path
from typing import Optional

# Path definitions
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"
DOWNLOAD_DIR = ASSETS_DIR / "packages"
MODELS_DIR = ASSETS_DIR / "models"
ARGOS_DATA_DIR = MODELS_DIR

# Set the environment variable before importing argostranslate
os.environ["ARGOS_PACKAGES_DIR"] = str(MODELS_DIR)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


class TranslatorManager:
    """Manager class for translation operations."""

    def __init__(self):
        """Initialize the translator manager and ensure directories exist."""
        # Ensure required directories exist
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        MODELS_DIR.mkdir(parents=True, exist_ok=True)

    def install_model(self, from_code: str, to_code: str) -> bool:
        """
        Install the translation model for the given language pair if not already installed.

        Args:
            from_code: Source language code
            to_code: Target language code

        Returns:
            bool: True if installation was successful, False otherwise
        """
        try:
            # Check if model is already installed and usable
            installed_languages = translate.get_installed_languages()
            from_lang = next((lang for lang in installed_languages
                             if lang.code == from_code), None)

            if from_lang:
                is_installed = any(t.to_lang.code == to_code
                                   for t in from_lang.translations_from)
                if is_installed:
                    logger.info(
                        f"Model {from_code}->{to_code} already installed.")
                    return True

            # Update package index and find the required model
            logger.info("Updating package index...")
            package.update_package_index()
            available_packages = package.get_available_packages()

            model = next((p for p in available_packages
                         if p.from_code == from_code and p.to_code == to_code), None)
            if not model:
                raise ValueError(
                    f"No translation model available for {from_code}->{to_code}")

            # Define the model path with a consistent naming convention
            model_filename = f"{from_code}_{to_code}.argosmodel"
            model_path = DOWNLOAD_DIR / model_filename

            # Download the model if it doesn't exist
            if not model_path.exists():
                logger.info(f"Downloading model to {model_path}...")
                downloaded_path = model.download()
                # Move downloaded file to the packages directory
                shutil.move(downloaded_path, model_path)
                logger.info(f"Model downloaded successfully to {model_path}")
            else:
                logger.info(f"Using existing model at {model_path}")

            # Install the model
            logger.info("Installing model...")
            package.install_from_path(str(model_path))
            logger.info("Model installed successfully.")
            return True

        except Exception as e:
            logger.error(f"Model installation failed: {e}")
            logger.debug(traceback.format_exc())
            return False

    def create_translator(self, from_code: str, to_code: str) -> translate.ITranslation:
        """
        Create a translator object for the given language codes.

        Args:
            from_code: Source language code
            to_code: Target language code

        Returns:
            translate.ITranslation: Translator object

        Raises:
            ValueError: If the language pair is not available
        """
        installed = translate.get_installed_languages()
        from_lang = next(
            (lang for lang in installed if lang.code == from_code), None)

        if not from_lang:
            raise ValueError(f"Source language '{from_code}' not installed.")

        translation = None
        for trans in from_lang.translations_from:
            if trans.to_lang.code == to_code:
                translation = trans
                break

        if not translation:
            raise ValueError(
                f"Target language '{to_code}' not supported by source '{from_code}'.")

        return translation

    def translate_text(self, text: str, from_code: str, to_code: str) -> str:
        """
        Translate text from one language to another.

        Args:
            text: Text to translate
            from_code: Source language code
            to_code: Target language code

        Returns:
            str: Translated text
        """
        self.install_model(from_code, to_code)
        translator = self.create_translator(from_code, to_code)
        return translator.translate(text)

    def uninstall_all_models(self) -> None:
        """Uninstall all installed Argos Translate packages."""
        installed_packages = package.get_installed_packages()
        for pkg in installed_packages:
            logger.info(f"Uninstalling {pkg.from_code} → {pkg.to_code}")
            package.uninstall_package(pkg)
        logger.info("All models uninstalled.")

    def wipe_argos_data(self) -> None:
        """Remove Argos Translate internal data directory."""
        if ARGOS_DATA_DIR.exists():
            logger.info(f"Removing Argos data directory: {ARGOS_DATA_DIR}")
            shutil.rmtree(ARGOS_DATA_DIR)
            logger.info("Data directory removed.")

    def force_reset(self) -> None:
        """Reset all Argos Translate models and data."""
        logger.info("Performing complete reset of all models and data...")
        self.uninstall_all_models()
        self.wipe_argos_data()
        logger.info("Reset completed successfully.")
<<<<<<< Updated upstream:src/simple_translator/__main__.py


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Argos Translate Utility")
    parser.add_argument("--reset", action="store_true",
                        help="Force reset all installed models and data")
    parser.add_argument("--from-lang", default="en",
                        help="Source language code (default: en)")
    parser.add_argument("--to-lang", default="de",
                        help="Target language code (default: de)")
    parser.add_argument("--text",
                        default="Hello, world! This is a test translation.",
                        help="Text to translate")
    parser.add_argument("--debug", action="store_true",
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

        # Perform translation
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
=======
>>>>>>> Stashed changes:src/translation/translator.py
