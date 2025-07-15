#!/usr/bin/env python3

import subprocess
import os
import shutil
import gzip
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# ---------- ASCII Banner ----------
ASCII_GORIB = r"""
       ___
     _(o o)_
   // \_=_/ \\
  ||  (_)   ||
  || Gorib 🧢||
  ||_______||
   |       |
  /|_______|\\
 /_|_______|_\\
   ||     ||
  /_\_   _/_\\
    /_\ /_\\
"""

def display_banner():
    print(ASCII_GORIB)

# ---------- Paths & Files ----------
input_file = "subdomains_alive.txt"
output_dir = "output"
katana_output = os.path.join(output_dir, "katana_urls.txt")
wayback_output = os.path.join(output_dir, "wayback_urls.txt")
gau_output = os.path.join(output_dir, "gau_urls.txt")
combined_output = os.path.join(output_dir, "combined_urls.txt")
alive_output = os.path.join(output_dir, "alive_urls.txt")
signal_output = os.path.join(output_dir, "signal_urls.txt")

# ---------- Required Tools ----------
required_tools = ["katana", "waybackurls", "gau", "httpx"]

def check_dependencies():
    missing = [tool for tool in required_tools if shutil.which(tool) is None]
    if missing:
        print(f"[!] Missing tools: {', '.join(missing)}. Install before continuing.")
        exit(1)

def ensure_input_file():
    if not os.path.isfile(input_file):
        print(f"[!] Input file not found: {input_file}")
        exit(1)

def setup_output_dir():
    os.makedirs(output_dir, exist_ok=True)

# ---------- Shell Execution ----------
def run_cmd(desc, cmd):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [+] {desc}")
    try:
        result = subprocess.run(cmd, shell=True, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[!] Error in '{desc}':\n{e.stderr}")
        exit(1)

# ---------- URL Collection ----------
def run_katana():
    cmd = f"cat {input_file} | xargs -P 10 -I {{}} katana -list {{}} -silent -o {katana_output}"
    run_cmd("Running Katana", cmd)

def run_waybackurls():
    cmd = f"cat {input_file} | waybackurls > {wayback_output}"
    run_cmd("Fetching Wayback URLs", cmd)

def run_gau():
    cmd = (
        f"cat {input_file} | gau --threads 10 --subs "
        f"--blacklist jpg,jpeg,png,gif,svg,woff "
        f"--providers wayback,commoncrawl,otx,urlscan "
        f"--verbose --o {gau_output}"
    )
    run_cmd("Running gau", cmd)

def combine_urls():
    cmd = f"cat {katana_output} {wayback_output} {gau_output} | sort -u > {combined_output}"
    run_cmd("Combining and deduplicating URLs", cmd)

def check_alive():
    cmd = f"httpx -l {combined_output} -silent > {alive_output}"
    run_cmd("Checking alive URLs with httpx", cmd)

# ---------- Filtering ----------
def filter_signal_urls(input_path, output_path):
    patterns = [
        r'\?.+=', r'/api/', r'\.php$', r'\.aspx$', r'/auth', r'token',
        r'login', r'redirect', r'callback', r'/config', r'\.js'
    ]
    with open(input_path, 'r') as src, open(output_path, 'w') as dest:
        for line in src:
            if any(re.search(p, line) for p in patterns):
                dest.write(line)
    print(f"[✓] Signal-rich URLs saved to {output_path}")

# ---------- Compression ----------
def compress_file(path, toggle=True):
    if not toggle:
        return
    with open(path, 'rb') as f_in, gzip.open(path + ".gz", 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    print(f"[+] Compressed: {path}.gz")

# ---------- Cleanup ----------
def clean_temp_files():
    for f in [katana_output, wayback_output, gau_output, combined_output]:
        if os.path.exists(f):
            os.remove(f)
            print(f"[-] Removed: {f}")

# ---------- Summary ----------
def count_lines(path):
    try:
        with open(path, 'r') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

# ---------- Main ----------
if __name__ == "__main__":
    display_banner()
    print(f"[+] Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    ensure_input_file()
    check_dependencies()
    setup_output_dir()

    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(run_katana)
        executor.submit(run_waybackurls)
        executor.submit(run_gau)

    combine_urls()
    check_alive()
    filter_signal_urls(alive_output, signal_output)
    compress_file(signal_output)
    clean_temp_files()

    final_count = count_lines(signal_output)
    print(f"[✓] Done. {final_count} signal-rich alive URLs saved to {signal_output}.gz")
