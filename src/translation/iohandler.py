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