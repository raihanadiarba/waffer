# 🔍 WAFFER (Web Archive File Finder)

<p align="center">
  A powerful tool for finding sensitive files from Internet Archive's Wayback Machine (archive.org)
</p>

## 🌟 About
WAFFER is a multi-threaded tool designed to search and retrieve files from the Wayback Machine's extensive archive of over 916 billion web pages. It leverages archive.org's API to discover potentially sensitive files that were archived over time.

## ✨ Features

- 🚀 **Powered by Wayback Machine** - Searches through archive.org's massive historical database
- 🔄 **Multi-threaded scanning** for faster archive searching
- 🎯 **Smart file filtering** with multiple extension sets:
  - Default sensitive files
  - Extended file types
  - Custom extensions
  - No filtering option
- ⏱️ **Rate limiting** to respect archive.org's servers
- 📝 **Detailed logging** with verbose mode
- 🎨 **Colored output** for better readability

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/raihanadiarba/waffer.git
cd waffer
```

2. Install dependencies:
```bash
pip install colorama requests
```

## 📖 Usage

Basic syntax:
```bash
python3 waffer.py [-u URL | -l FILE] [-e {default,all,custom,none}] [-c EXTENSIONS] [-t THREADS] [-o OUTPUT] [-v] [-ts DELAY]
```

### 🎮 Arguments

| Argument | Description |
|----------|-------------|
| `-u, --url` | Target domain to search in Wayback Machine |
| `-l, --list` | File containing list of URLs to search |
| `-e, --extension` | Extension type to search (default/all/custom/none) |
| `-c, --custom` | Custom extensions (comma-separated) |
| `-t, --threads` | Number of concurrent threads (default: 10) |
| `-o, --output` | Save results to file |
| `-v, --verbose` | Show detailed progress |
| `-ts, --time-sec` | Delay between requests to archive.org |

### 📚 Examples

1. Search domain in Wayback Machine:
```bash
python3 waffer.py -u example.com
```

2. Search with all extensions and verbose output:
```bash
python3 waffer.py -u example.com -e all -v
```

3. Custom file types with output file:
```bash
python3 waffer.py -u example.com -e custom -c .pdf,.doc,.txt -o results.txt
```

4. Scan multiple URLs with rate limiting:
```bash
python3 waffer.py -l urls.txt -ts 1
```

## 🔍 Extension Sets

### Default Extensions
Common sensitive files including:
- Documents (.pdf, .doc, .docx)
- Data files (.xml, .json, .sql)
- Archives (.zip, .tar.gz, .7z)
- Configuration (.yml, .config, .ini)
- Security files (.key, .pem, .crt)

### All Extensions
Extended set including:
- Web configuration (.env, .htaccess)
- Backup files (*-BACKUP-*, .bak)
- Development (.git, .svn)
- Database files (.sql, .sqlite)
- And many more...

## 📥 Accessing Found Files

After the tool finds URLs, you can access the archived files using these methods:

1. **Direct Wayback Machine Access**:
   - Take the found URL: `http://example.com/file.pdf`
   - Visit: `https://web.archive.org/web/*/http://example.com/file.pdf`
   - Select the snapshot date you want to view

2. **Automated URL Format**:
   - Format: `https://web.archive.org/web/<timestamp>/<url>`
   - Example: `https://web.archive.org/web/20230101000000/http://example.com/file.pdf`

3. **Latest Snapshot**:
   - Use: `https://web.archive.org/web/2/http://example.com/file.pdf`
   - This automatically redirects to the most recent archive

4. **First Snapshot**:
   - Use: `https://web.archive.org/web/0/http://example.com/file.pdf`
   - This shows the oldest archived version

## ⚠️ Disclaimer

This tool is designed for security research and should be used responsibly. Always:
- Respect archive.org's terms of service
- Use appropriate delays between requests
- Only scan domains you have permission to test

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.


## Credit
This tool was inspired by @coffinxp. Thanks to them for the great idea!
