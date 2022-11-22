import os
import tomllib
import win32gui
from fuzzywuzzy import fuzz


with open("config.toml", "rb") as f:
    try:
        config = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        print(e)
        print("config.toml is invalid")
        input("Press enter to exit...")
        exit(1)

try:
    root = config["user"]["root"]
    root = os.path.normpath(root)
    dirs = next(os.walk(root))[1]

except StopIteration:
    print("No directories found or root is invalid!")
    print(f"user root: {root}")
    input("Press enter to exit...")
    exit(1)

version = config["dev"]["version"]


def set_window(columns, lines, color):
    hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowText(hwnd, f"Coeus ({version})")

    os.system("cls")
    os.system(f"mode con: cols={columns} lines={lines}")
    os.system(f"color {color}")
    os.system(f"title Coeus ({version})")


def header():
    header = config["dev"]["ascii"]
    header += f"\n     Root: {root}\n"
    header += f"  Version: {version}\n"
    return header


def sanitize_input(user_input):
    user_input = user_input.lower()
    # we need to clean up some edge cases
    # but can't think of anymore right now
    return user_input


def random_alphanumeric(length: int):
    import random
    import string

    opts = string.ascii_lowercase + string.digits
    return random.choice(opts) * length


def get_fuzz_ratio(string_1, string_2):
    string_1 = string_1.lower()
    string_2 = string_2.lower()

    # gotta be better ways within fuzzywuzzy to do this
    # but this works for now
    # accuracy is just not good enough for my liking

    ratio = fuzz.token_set_ratio(string_1, string_2)
    return ratio


def autocomplete(
    options, user_input, ratio_threshold=config["user"]["ratio_threshold"]
):

    # 56 is the default ratio threshold
    # it can be changed by the user
    # but anything below seemed to just be noise
    matches = {}
    for match in options:
        ratio = get_fuzz_ratio(user_input, match)
        unique_key = random_alphanumeric(4)

        if ratio >= ratio_threshold:
            matches[match] = ratio, unique_key

        else:
            # we need a better way to get matches that may be letter for letter matches
            # but not enough to be considered a match
            # current solution may be the best
            if match.startswith(user_input) and match not in matches:
                matches[match] = ratio, unique_key

    # format of matches is now ((ratio, (unique key)), match)
    # with highest ratio descending
    # the unique_key is only here because we lose matches if they have the same ratio
    # for some reason???
    matches = {
        k: v
        for k, v in sorted(matches.items(), key=lambda item: item[1][0], reverse=True)
    }

    matches = dict(list(matches.items())[:26])

    if all(ratio[0] == 0 for ratio in matches.values()):
        return {}
    else:
        return matches


def main():
    try:
        set_window(
            config["window"]["columns"],
            config["window"]["lines"],
            config["window"]["color"],
        )
        print(header())
        while True:
            user_input = sanitize_input(input("  >>> "))
            os.system("cls")
            print(header())
            print(f"  >>> {user_input}")
            if user_input == "exit" or user_input == "cls":
                break
            else:
                matches = autocomplete(dirs, user_input)
                print("")
                if not matches:
                    print("  No matches found")
                for match, ratio in matches.items():
                    if any(ratio[0] == 100 for ratio in matches.values()):
                        print(f"  {ratio[0]:3}: {match}")
                    else:
                        print(f"  {ratio[0]:2}: {match}")
                print("")

    except KeyboardInterrupt:
        pass

    except Exception as e:
        print(e)
        input("Press enter to continue...")

    finally:
        # we need to reset the window, display the cursor,
        # clear the screen, and make sure the window isn't on top at all times anymore
        exit(0)


if __name__ == "__main__":
    main()
