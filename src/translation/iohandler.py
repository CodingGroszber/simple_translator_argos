import sys

def continuous_mode(translator, args):
    loop_continue = True
    while True:
        try:
            print("Translate input:")
            text_input = sys.stdin.readline()
            result = translator.translate(text_input)
            print(f"Translated [{args.to_lang}]: {result}")
        except KeyboardInterrupt:
            print("\nExiting due to keyboard interrupt.")
            loop_continue = False
            break
        except EOFError:
            print("\nExiting due to end-of-file (Ctrl+D/Ctrl+Z).")
            loop_continue = False
            break


def single_mode(translator, args):
    result = translator.translate(args.text)
    print("\n" + "=" * 40)
    print(f"SOURCE [{args.from_lang}]: {args.text}")
    print(f"TARGET [{args.to_lang}]: {result}")
    print("=" * 40)