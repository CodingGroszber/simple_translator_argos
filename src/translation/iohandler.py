# iohandler.py (modified to use input() for EOFError on stdin close)
import sys


def continuous_mode(translator, args):
    is_pipe = args.pipe or not sys.stdin.isatty()
    while True:
        try:
            if not is_pipe:
                text_input = input("Translate input: ")
            else:
                text_input = input()
            if not text_input:
                continue
            result = translator.translate(text_input)
            if is_pipe:
                # Simple output for pipe mode, with flush
                print(f"{result}_ok", flush=True)
            else:
                print(f"Translated [{args.to_lang}]: {result}", flush=True)
        except EOFError:
            break
        except KeyboardInterrupt:
            if not is_pipe:
                print("\nExiting due to keyboard interrupt (Ctrl+C).")
            break


def single_mode(translator, args):
    is_pipe = args.pipe or not sys.stdin.isatty()
    result = translator.translate(args.text)
    if is_pipe:
        print(f"{result}_ok", flush=True)  # Simple output for pipe mode
    else:
        print("\n" + "=" * 40)
        print(f"SOURCE [{args.from_lang}]: {args.text}")
        print(f"TARGET [{args.to_lang}]: {result}")
        print("=" * 40)
