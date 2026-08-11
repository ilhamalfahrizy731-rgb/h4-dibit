import json
import os
import random
import signal
import sys
import time
from datetime import datetime

FILE_NAME = "wordlist.json"
LOG_FILE = "generator_activity.log"
AUTOSAVE_THRESHOLD = 50

# ==========================================
# COLOR PALETTE & STYLING
# ==========================================
C_RESET = "\033[0m"
C_BOLD = "\033[1m"

CYAN = "\033[38;5;51m"
NEON_GREEN = "\033[38;5;82m"
BRIGHT_RED = "\033[38;5;196m"
YELLOW = "\033[38;5;226m"
PURPLE = "\033[38;5;141m"
GRAY = "\033[38;5;240m"
WHITE = "\033[38;5;255m"

# Box Width: 58 Characters Inner Width
BOX_TOP = "╔" + "═" * 58 + "╗"
BOX_MID = "╠" + "═" * 58 + "╣"
BOX_BOT = "╚" + "═" * 58 + "╝"


def get_ascii_header():
    return f"""{CYAN}{C_BOLD}
   ██╗  ██╗██╗  ██╗    ██████╗ ██╗██████╗ ██╗████████╗
   ██║  ██║██║  ██║    ██╔══██╗██║██╔══██╗██║╚══██╔══╝
   ███████║███████║    ██║  ██║██║██████╔╝██║   ██║   
   ██╔══██║╚════██║    ██║  ██║██║██╔══██╗██║   ██║   
   ██║  ██║     ██║    ██████╔╝██║██████╔╝██║   ██║   
   ╚═╝  ╚═╝     ╚═╝    ╚═════╝ ╚═╝╚═════╝ ╚═╝   ╚═╝   
             HIGH-SPEED WORDLIST ENGINE v4.0{C_RESET}"""


def format_row(content):
    """Menghitung panjang teks murni tanpa ANSI color code agar bingkai presisi."""
    plain_text = content
    for code in [
        C_RESET,
        C_BOLD,
        CYAN,
        NEON_GREEN,
        BRIGHT_RED,
        YELLOW,
        PURPLE,
        GRAY,
        WHITE,
    ]:
        plain_text = plain_text.replace(code, "")

    padding = 58 - len(plain_text)
    return f"{CYAN}║{C_RESET}{content}{' ' * padding}{CYAN}║{C_RESET}"


class WordlistGenerator:

    def __init__(self, filename, digit_length):
        self.filename = filename
        self.digit_length = digit_length
        self.wordlist = set()
        self.total_attempts = 0
        self.total_duplicates = 0
        self.start_time = time.time()
        self.save_counter = 0

        self.load_existing_data()

    def log_event(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] {message}\n")

    def load_existing_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        valid_items = [
                            str(item)
                            for item in data
                            if len(str(item)) == self.digit_length
                        ]
                        self.wordlist = set(valid_items)
                        self.log_event(
                            f"Loaded {len(self.wordlist)} items ({self.digit_length} digits)"
                        )
            except Exception as e:
                self.log_event(f"Load error: {str(e)}")

    def save_data(self):
        try:
            with open(self.filename, "w") as f:
                json.dump(sorted(list(self.wordlist)), f, indent=2)
            self.log_event(f"Saved {len(self.wordlist)} items")
        except Exception as e:
            self.log_event(f"Save error: {str(e)}")

    def render_dashboard(self):
        os.system("clear" if os.name == "posix" else "cls")
        print(get_ascii_header())
        print(f"{CYAN}{BOX_TOP}{C_RESET}")

        print(
            format_row(
                f" {WHITE}Target File    :{C_RESET} {YELLOW}{self.filename}{C_RESET}"
            )
        )
        print(
            format_row(
                f" {WHITE}Length Mode    :{C_RESET} {PURPLE}{self.digit_length} Digit (Custom Pattern){C_RESET}"
            )
        )
        print(
            format_row(
                f" {WHITE}Generator Mode :{C_RESET} {NEON_GREEN}UNLIMITED LOOP (Ctrl+C to Stop){C_RESET}"
            )
        )
        print(
            format_row(
                f" {WHITE}Loaded Items   :{C_RESET} {YELLOW}{len(self.wordlist):,} item(s){C_RESET}"
            )
        )

        print(f"{CYAN}{BOX_BOT}{C_RESET}\n")

    def run(self):
        self.render_dashboard()

        format_spec = f"0{self.digit_length}d"
        max_val = (10**self.digit_length) - 1

        print(
            f"{GRAY}[SYS] Initializing high-speed thread... Generator is active.{C_RESET}\n"
        )

        while True:
            self.total_attempts += 1

            raw_num = random.randint(0, max_val)
            angka_str = f"{raw_num:{format_spec}}"

            elapsed_sec = int(time.time() - self.start_time)
            mins, secs = divmod(elapsed_sec, 60)
            time_str = f"{mins:02d}:{secs:02d}"

            if angka_str in self.wordlist:
                self.total_duplicates += 1
                status = (
                    f"\r {BRIGHT_RED}✖ [DUPLICATE]{C_RESET} {WHITE}{angka_str}{C_RESET} "
                    f"{GRAY}│{C_RESET} Rejected: {BRIGHT_RED}{self.total_duplicates:,}{C_RESET} "
                    f"{GRAY}│{C_RESET} Unique: {NEON_GREEN}{len(self.wordlist):,}{C_RESET} "
                    f"{GRAY}│{C_RESET} Time: {YELLOW}{time_str}{C_RESET}"
                )
                sys.stdout.write(status)
                sys.stdout.flush()
            else:
                self.wordlist.add(angka_str)
                self.save_counter += 1

                status = (
                    f"\r {NEON_GREEN}✔ [ADDED]{C_RESET} {WHITE}{C_BOLD}{angka_str}{C_RESET}     "
                    f"{GRAY}│{C_RESET} Rejected: {BRIGHT_RED}{self.total_duplicates:,}{C_RESET} "
                    f"{GRAY}│{C_RESET} Unique: {NEON_GREEN}{len(self.wordlist):,}{C_RESET} "
                    f"{GRAY}│{C_RESET} Time: {YELLOW}{time_str}{C_RESET}"
                )
                sys.stdout.write(status)
                sys.stdout.flush()

                if self.save_counter >= AUTOSAVE_THRESHOLD:
                    self.save_data()
                    self.save_counter = 0

            time.sleep(0.0001)


def show_cyber_menu():
    os.system("clear" if os.name == "posix" else "cls")
    print(get_ascii_header())
    print(f"\n{CYAN}{BOX_TOP}{C_RESET}")

    print(format_row(f" {WHITE}{C_BOLD}SELECT GENERATION MODE:{C_RESET}"))
    print(f"{CYAN}{BOX_MID}{C_RESET}")
    print(
        format_row(
            f" {NEON_GREEN}[1]{C_RESET} {WHITE}4-Digit Mode   (0000 - 9999)      -> Unlimited{C_RESET}"
        )
    )
    print(
        format_row(
            f" {NEON_GREEN}[2]{C_RESET} {WHITE}6-Digit Mode   (000000 - 999999)  -> Unlimited{C_RESET}"
        )
    )
    print(
        format_row(
            f" {NEON_GREEN}[3]{C_RESET} {WHITE}Custom Length  (Define manually)   -> Unlimited{C_RESET}"
        )
    )
    print(
        format_row(
            f" {BRIGHT_RED}[0]{C_RESET} {WHITE}Exit Generator{C_RESET}"
        )
    )

    print(f"{CYAN}{BOX_BOT}{C_RESET}\n")

    prompt = f"{CYAN}┌──({NEON_GREEN}user@wordlist{CYAN})-[{WHITE}~{CYAN}]\n└─{YELLOW}# Select option (1/2/3/0): {C_RESET}"
    choice = input(prompt).strip()

    if choice == "1":
        return 4
    elif choice == "2":
        return 6
    elif choice == "3":
        try:
            custom_prompt = (
                f"\n{CYAN}└─{YELLOW}# Enter custom digit length (e.g. 5, 8, 10): {C_RESET}"
            )
            custom_len = int(input(custom_prompt))
            if custom_len > 0:
                return custom_len
            else:
                print(f"\n{BRIGHT_RED}[!] Digit must be greater than 0!{C_RESET}")
                time.sleep(1.2)
                return show_cyber_menu()
        except ValueError:
            print(f"\n{BRIGHT_RED}[!] Input must be a number!{C_RESET}")
            time.sleep(1.2)
            return show_cyber_menu()
    elif choice == "0":
        print(f"\n{GRAY}[SYS] Exiting program. Goodbye!{C_RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{BRIGHT_RED}[!] Invalid option selection!{C_RESET}")
        time.sleep(1.2)
        return show_cyber_menu()


def main():
    digit_length = show_cyber_menu()
    generator = WordlistGenerator(FILE_NAME, digit_length)

    def shutdown_handler(sig, frame):
        print(f"\n\n{CYAN}{BOX_TOP}{C_RESET}")
        print(
            format_row(
                f" {YELLOW}{C_BOLD}PROCESS TERMINATED BY USER (SIGINT){C_RESET}"
            )
        )
        print(f"{CYAN}{BOX_MID}{C_RESET}")
        print(
            format_row(
                f" {WHITE}Total Generation Attempts : {YELLOW}{generator.total_attempts:,}{C_RESET}"
            )
        )
        print(
            format_row(
                f" {WHITE}Unique Numbers Saved      : {NEON_GREEN}{len(generator.wordlist):,}{C_RESET}"
            )
        )
        print(
            format_row(
                f" {WHITE}Duplicates Prevented      : {BRIGHT_RED}{generator.total_duplicates:,}{C_RESET}"
            )
        )
        print(f"{CYAN}{BOX_MID}{C_RESET}")
        print(format_row(f" {GRAY}[SYS] Saving database to file...{C_RESET}"))
        generator.save_data()
        print(
            format_row(
                f" {NEON_GREEN}[✓] Data successfully secured in {FILE_NAME}{C_RESET}"
            )
        )
        print(f"{CYAN}{BOX_BOT}{C_RESET}\n")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    generator.run()


if __name__ == "__main__":
    main()