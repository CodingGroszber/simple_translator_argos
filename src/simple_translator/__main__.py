"""
Argos Translate English-to-Russian Script
Requirements: argostranslate package installed (pip install argostranslate)
"""

import sys
import os
from argostranslate import package, translate


def install_model(from_code: str, to_code: str) -> None:
    try:
        installed = translate.get_installed_languages()
        from_lang = next(
            (lang for lang in installed if lang.code == from_code), None)
        if from_lang:
            exists = any(t.to_lang.code ==
                         to_code for t in from_lang.translations_from)
            if exists:
                print(f"Model {from_code}->{to_code} already installed.")
                return

        package.update_package_index()
        available = package.get_available_packages()
        pkg = next((p for p in available if p.from_code ==
                   from_code and p.to_code == to_code), None)
        if not pkg:
            raise RuntimeError(
                f"No available package for {from_code}->{to_code}")

        print(f"Downloading and installing {from_code}->{to_code}...")
        path = pkg.download()
        package.install_from_path(path)
        print("Model installed.")
    except Exception as e:
        print(f"Model installation failed: {e}", file=sys.stderr)
        raise


def create_translator(from_code: str, to_code: str):
    installed = translate.get_installed_languages()
    from_lang = next(
        (lang for lang in installed if lang.code == from_code), None)
    if not from_lang:
        raise RuntimeError(f"Source language {from_code} not installed.")
    to_lang_obj = next(
        (t.to_lang for t in from_lang.translations_from if t.to_lang.code == to_code), None)
    if not to_lang_obj:
        raise RuntimeError(
            f"Target language {to_code} not supported by {from_code}.")
    translation = from_lang.get_translation(to_lang_obj)
    return translation


def main() -> None:
    """Main execution flow"""
    try:
        # Configuration
        FROM_LANG = "en"
        TO_LANG = "ru"
        TEXT_TO_TRANSLATE = "Hello, world! This is a test translation."

        # Ensure model is installed
        install_model(FROM_LANG, TO_LANG)

        # Create translator
        translator = create_translator(FROM_LANG, TO_LANG)

        # Perform translation
        result = translator.translate(TEXT_TO_TRANSLATE)
        print(f"\nOriginal: {TEXT_TO_TRANSLATE}")
        print(f"Translated: {result}")

    except Exception as e:
        print(f"Translation process failed: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
