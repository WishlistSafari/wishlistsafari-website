"""Tell Bing (and other IndexNow engines) about every page in sitemap.xml.
Run after publishing changes: python3 tools/indexnow.py
Key file: 07d9996fd25c986f1de9e70828c04914.txt at the site root (do not delete)."""
import json, re, urllib.request
KEY = '07d9996fd25c986f1de9e70828c04914'
urls = re.findall(r'<loc>([^<]*)</loc>', open('sitemap.xml').read())
body = json.dumps({"host": "wishlistsafari.com", "key": KEY,
                   "keyLocation": f"https://wishlistsafari.com/{KEY}.txt", "urlList": urls}).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body,
                             headers={'Content-Type': 'application/json; charset=utf-8'})
print(urllib.request.urlopen(req).status, len(urls), 'URLs submitted')
