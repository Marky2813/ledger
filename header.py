import json 
import html
import re

with open("data/raw/49922569.json", "r") as f:
  data = json.load(f)["children"]

# split it at the paragraph tags and store it in the extract_headers list. traverse over data, then extract the header from the head and store it in the extract_headers list

extract_headers = []
for d in data:  
  if "<p>" in d["text"] and "|" in d["text"]: 
    # extract the header and put it in the extract_headers array
      current = {}
      header = d["text"].split("<p>")[0]
      header = html.unescape(header)
      header = header.split("|")
      current["company"] = header[0].strip()
      current["url"] = None
      for i in range(1, len(header)):
         if "href" in header[i].strip().lower() or "http" in header[i].strip().lower():
            current["url"] = re.search(r'href="([^"]+)"', header[i].strip()).group(1)
            print(current)
            print()
      extract_headers.append(current)
