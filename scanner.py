import requests
from bs4 import BeautifulSoup
import urllib.parse


class WebSecurityScanner:
    def __init__(self, target_url, max_depth=1):
        self.target_url = target_url
        self.max_depth = max_depth
        self.visited = set()
        self.vulnerabilities = []

    def crawl(self, url, depth=0):
        if depth > self.max_depth or url in self.visited:
            return
        try:
            self.visited.add(url)
            resp = requests.get(url, timeout=5)
            soup = BeautifulSoup(resp.text, "html.parser")
            for link in soup.find_all('a', href=True):
                next_url = urllib.parse.urljoin(url, link['href'])
                if next_url.startswith(self.target_url):
                    self.crawl(next_url, depth + 1)
        except Exception as e:
            pass

    def check_xss(self, url):
        payload = "<script>alert('XSS')</script>"
        try:
            resp = requests.get(url, params={"input": payload}, timeout=5)
            if payload in resp.text:
                self.vulnerabilities.append({"type": "XSS", "url": url})
        except:
            pass

    def check_sql_injection(self, url):
        payloads = ["' OR '1'='1", '" OR "1"="1', "'; DROP TABLE users; --"]
        for payload in payloads:
            test_url = url
            if '?' in url:
                test_url += f"&id={payload}"
            else:
                test_url += f"?id={payload}"
            try:
                resp = requests.get(test_url, timeout=5)
                if any(error in resp.text.lower() for error in ['sql', 'mysql', 'database', 'syntax error']):
                    self.vulnerabilities.append({"type": "SQL Injection", "url": test_url})
                    break  # Found SQL injection, no need to test other payloads
            except:
                pass

    def scan(self):
        self.crawl(self.target_url)
        for url in self.visited:
            self.check_xss(url)
            self.check_sql_injection(url)
        return self.vulnerabilities
