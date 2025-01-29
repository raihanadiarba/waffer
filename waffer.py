import argparse
import requests
import time
import random
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from colorama import init, Fore, Style

init()

INFO = Fore.CYAN
SUCCESS = Fore.LIGHTGREEN_EX 
ERROR = Fore.LIGHTRED_EX
WARNING = Fore.YELLOW
RESET = Style.RESET_ALL

DEFAULT_EXTENSIONS = [
    ".xls", ".xml", ".xlsx", ".json", ".pdf", ".sql", ".doc", ".docx", ".pptx", ".txt", 
    ".zip", ".tar.gz", ".tgz", ".bak", ".7z", ".rar", ".log", ".cache", ".secret", ".db",
    ".backup", ".yml", ".gz", ".config", ".csv", ".yaml", ".md", ".md5", ".exe", ".dll",
    ".bin", ".ini", ".bat", ".sh", ".tar", ".deb", ".rpm", ".iso", ".img", ".apk", ".msi",
    ".dmg", ".tmp", ".crt", ".pem", ".key", ".pub", ".asc"
]

ALL_EXTENSIONS = [".env", ".htaccess", ".htpasswd", ".conf", ".inc", ".config", ".settings", ".ini", ".cfg",
                 ".properties", ".toml", "web.config", "robots.txt", "sitemap.xml", "crossdomain.xml",
                 ".well-known", ".bak", ".backup", ".old", ".save", ".orig", ".temp", ".tmp", ".swp", ".swo",
                 "~", ".copy", "._old", ".draft", "*-BACKUP-*", "*-backup-*", ".php~", ".php.bak", ".php.old",
                 ".php.swp", ".phps", ".asp~", ".aspx~", ".jsp~", ".jsx~", ".js~", ".vue~", ".rb~", ".py~",
                 ".go~", ".java~", ".class", ".git", ".svn", ".hg", ".idea", ".vscode", "node_modules/",
                 "vendor/", ".sqlite", ".sqlite3", ".mdb", ".sql", ".mysql", ".pgsql", ".mongodb", ".redis",
                 ".frm", ".ibd", ".myd", ".myi", ".dbf"] + DEFAULT_EXTENSIONS

# List of User Agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

class WebArchiveScanner:
    def __init__(self, threads=10):
        self.threads = threads
        self.found_files = []
        self.lock = Lock()
        self.user_agent_lock = Lock()
        self.total_urls = 0
        self.verbose = False
        self.time_delay = 0
        self.current_user_agent_index = 0
        self.session = requests.Session()
        self.rate_limit_count = 0
        self.rate_limit_threshold = 3

    def get_next_user_agent(self):
        with self.user_agent_lock:
            user_agent = USER_AGENTS[self.current_user_agent_index]
            self.current_user_agent_index = (self.current_user_agent_index + 1) % len(USER_AGENTS)
            return user_agent

    def verify_snapshot(self, url):
        max_retries = 5
        base_delay = 2
        headers = {
            'User-Agent': self.get_next_user_agent(),
            'Accept': 'application/json,text/html,application/xhtml+xml,application/xml;q=0.9',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        }

        for attempt in range(max_retries):
            try:
                delay = self.time_delay + random.uniform(0, 1)
                if delay > 0:
                    time.sleep(delay)

                if self.verbose:
                    print(f"{INFO}[*] Verifying snapshot for:{RESET} {url}")
                    print(f"{INFO}[*] Using User-Agent:{RESET} {headers['User-Agent']}")

                verify_url = f"https://archive.org/wayback/available?url={quote(url)}"
                
                response = self.session.get(
                    verify_url,
                    headers=headers,
                    timeout=10,
                    allow_redirects=True
                )

                if response.status_code == 429:
                    with self.lock:
                        self.rate_limit_count += 1
                        if self.rate_limit_count >= self.rate_limit_threshold:
                            self.time_delay = min(self.time_delay + 1, 5)
                    
                    retry_after = int(response.headers.get('Retry-After', base_delay * (2 ** attempt)))
                    wait_time = retry_after + random.uniform(0, 2)
                    
                    if self.verbose:
                        print(f"{WARNING}[!] Rate limited. Switching User-Agent and waiting {wait_time:.1f}s...{RESET}")
                    
                    headers['User-Agent'] = self.get_next_user_agent()
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()
                data = response.json()
                result = bool(data.get('archived_snapshots'))

                with self.lock:
                    self.rate_limit_count = max(0, self.rate_limit_count - 1)

                if self.verbose:
                    if result:
                        print(f"{SUCCESS}[+] Snapshot found for: {RESET}{url}")
                    else:
                        print(f"{WARNING}[-] No snapshot found for: {RESET}{url}")
                return result

            except requests.RequestException as e:
                wait_time = base_delay * (2 ** attempt) + random.uniform(0, 2)
                
                if attempt < max_retries - 1:
                    if self.verbose:
                        print(f"{WARNING}[!] Attempt {attempt + 1}/{max_retries} failed, retrying in {wait_time:.1f}s: {e}{RESET}")
                    headers['User-Agent'] = self.get_next_user_agent()
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"{ERROR}[!] Max retries reached for {url}: {e}{RESET}")
                    return False

            except Exception as e:
                print(f"{ERROR}[!] Unexpected error for {url}: {e}{RESET}")
                return False

    def get_args(self):
        parser = argparse.ArgumentParser(
            description="Web Archive File Finder - A powerful tool for finding sensitive files from Internet Archive's Wayback Machine",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
Examples:
    Basic usage:
        python3 waffer.py -u example.com
        
    Using all extensions:
        python3 waffer.py -u example.com -e all
        
    Using custom extensions:
        python3 waffer.py -u example.com -e custom -c .pdf,.doc,.txt
        
    Using URL list from file:
        python3 waffer.py -l urls.txt
        
    Without extension filtering:
        python3 waffer.py -u example.com -e none
        
    Verbose output with delay:
        python3 waffer.py -u example.com -v -ts 1
            ''')
        
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-u', '--url', help='Target domain (e.g., example.com)')
        group.add_argument('-l', '--list', help='File containing list of URLs')
        
        parser.add_argument('-e', '--extension', choices=['default', 'all', 'custom', 'none'],
                          default='default', help='Extension type to search (default: default)')
        parser.add_argument('-c', '--custom', help='Custom extensions (comma-separated, e.g., .pdf,.doc,.txt)')
        parser.add_argument('-t', '--threads', type=int, default=10, help='Number of concurrent threads (default: 10)')
        parser.add_argument('-o', '--output', help='Output file name (optional)')
        parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
        parser.add_argument('-ts', '--time-sec', type=float, default=0, help='Time delay between requests in seconds (default: 0)')
        
        return parser.parse_args()

    def get_extensions(self, args):
        if args.extension == 'default':
            return DEFAULT_EXTENSIONS
        elif args.extension == 'all':
            return ALL_EXTENSIONS
        elif args.extension == 'none':
            return ['']
        elif args.extension == 'custom':
            if not args.custom:
                print(f"{ERROR}[!]Error: Custom extensions required with -c flag{RESET}")
                exit(1)
            return [ext.strip() for ext in args.custom.split(',')]

    def get_wayback_urls(self, domain):
        url = f"https://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=txt&fl=original&collapse=urlkey"
        try:
            response = requests.get(url)
            response.raise_for_status()
            urls = response.text.splitlines()
            if self.verbose:
                print(f"{SUCCESS}[+] Successfully retrieved {RESET}{len(urls)} URLs")
            return urls
        except requests.RequestException as e:
            print(f"{ERROR}[!] Error fetching URLs:{RESET} {e}")
            return []

    def process_url(self, url, extensions):
        if extensions == ['']:
            if self.verify_snapshot(url):
                with self.lock:
                    self.found_files.append(url)
                    print(f"{SUCCESS}[+] Found: {RESET}{url}")
        else:
            for ext in extensions:
                if url.lower().endswith(ext.lower()):
                    if self.verify_snapshot(url):
                        with self.lock:
                            self.found_files.append(url)
                            print(f"{SUCCESS}[+] Found: {RESET}{url}")
                    break

    def run(self):
        args = self.get_args()
        self.threads = args.threads
        self.verbose = args.verbose
        self.time_delay = args.time_sec
        extensions = self.get_extensions(args)

        print(f"{INFO}[*]{RESET} Starting waffer")
        print(f"{INFO}[*]{RESET} Using {self.threads} threads")

        if self.verbose:
            if self.time_delay > 0:
                print(f"{INFO}[*] Time delay: {self.time_delay} seconds{RESET}")
            if args.output:
                print(f"{INFO}[*] Results will be saved to: {args.output}{RESET}")

        if args.list:
            try:
                with open(args.list, 'r') as f:
                    urls = f.read().splitlines()
                if self.verbose:
                    print(f"{SUCCESS}[+] Loaded {len(urls)} URLs from {args.list}{RESET}")
            except FileNotFoundError:
                print(f"{ERROR}[!] Error: File {args.list} not found{RESET}")
                return
        else:
            urls = self.get_wayback_urls(args.url)

        self.total_urls = len(urls)
        if self.verbose:
            print(f"{INFO}[*] Total URLs to process: {self.total_urls}{RESET}")

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(self.process_url, url, extensions) for url in urls]
            for future in futures:
                future.result()

        print(f"\n{SUCCESS}Total files found: {len(self.found_files)}{RESET}")
        
        if args.output:
            with open(args.output, 'w') as f:
                for url in self.found_files:
                    f.write(f"{url}\n")
            print(f"{SUCCESS}Results saved to {args.output}{RESET}")
        else:
            print(f"\n{INFO}Found URLs:{RESET}")
            for url in self.found_files:
                print(f"{SUCCESS}{RESET}{url}")

def print_banner():
    banner = f"""
                __  __           
__      ____ _ / _|/ _| ___ _ __ 
\\ \\ /\\ / / _` | |_| |_ / _ \\ '__|
 \\ V  V / (_| |  _|  _|  __/ |   
  \\_/\\_/ \\__,_|_| |_|  \\___|_| {WARNING}v1.1{INFO}
     Web Archive File Finder {RESET}
    """
    print(banner)

if __name__ == "__main__":
    print_banner()
    scanner = WebArchiveScanner()
    scanner.run()
