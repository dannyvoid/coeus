import os, random, string
from fuzzywuzzy import fuzz

root = "path/to/your/root"
root = os.path.normpath(root)

try:
    dirs = next(os.walk(root))[1]
except StopIteration:
    print("No directories found or root is invalid!")
    print(f"Root: {root}")
    input("Press enter to exit...")
    exit()

version = "1.0.0"


def ascii_header():
    header = r"""
 ▄████▄  ▒█████ ▓█████ █    ██  ██████ 
▒██▀ ▀█ ▒██▒  ██▓█   ▀ ██  ▓██▒██    ▒ 
▒▓█    ▄▒██░  ██▒███  ▓██  ▒██░ ▓██▄   
▒▓▓▄ ▄██▒██   ██▒▓█  ▄▓▓█  ░██░ ▒   ██▒
▒ ▓███▀ ░ ████▓▒░▒████▒▒█████▓▒██████▒▒
░ ░▒ ▒  ░ ▒░▒░▒░░░ ▒░ ░▒▓▒ ▒ ▒▒ ▒▓▒ ▒ ░
  ░  ▒    ░ ▒ ▒░ ░ ░  ░░▒░ ░ ░░ ░▒  ░ ░

    """

    return header


def random_alphanumeric(length: int):
    opts = string.ascii_lowercase + string.digits
    return random.choice(opts) * length


def get_fuzz_ratio(string_1, string_2):
    string_1 = string_1.lower()
    string_2 = string_2.lower()
    return fuzz.token_set_ratio(string_1, string_2)


def autocomplete(options, user_input, ratio_threshold=56):
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

    return matches


def main():
    try:
        os.system("cls")
        os.system("color 0a")
        os.system(f"title Coeus ({version})")
        print(ascii_header())
        print(f"Version: {version}\n")

        while True:
            user_input = input(">>> ")
            if user_input == "":
                print("You must type something")
            if user_input == "exit" or user_input == "cls":
                break
            else:
                matches = autocomplete(dirs, user_input)
                if matches:
                    print("")
                for model, ratio in matches.items():
                    if any(ratio[0] == 100 for ratio in matches.values()):
                        print(f"{ratio[0]:3}: {model}")
                    else:
                        print(f"{ratio[0]}: {model}")
                print("")

    except KeyboardInterrupt:
        pass

    except Exception as e:
        print(e)
        input("Press enter to continue...")


if __name__ == "__main__":
    main()