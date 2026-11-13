import json 
import html
import re
# split it at the paragraph tags and store it in the extract_headers list. traverse over data, then extract the header from the head and store it in the extract_headers list

def extract_headers(data):
   ROLE_WORDS = {
      "engineer", "engineering", "developer", "scientist", "researcher",
      "designer", "manager", "lead", "architect", "analyst", "intern",
      "devrel", "founding", "founder", "cto", "head", "director",
      "swe", "sre", "staff", "associate", "positions", "roles", "robotics", 
      "ai", "ml", "data", "product", "ux", "ui", "qa", "test", "eng", 
      "sales", "systems", "infra", "infrastructure", "market", 
      "engineers", "developers", "scientists", "designers", "managers"
   }
   extract_headers = []
   ambiguous_headers = []
   for d in data:  
      if "<p>" in d["text"] and "|" in d["text"]: 
         # extract the header and put it in the extract_headers array
            header = d["text"].split("<p>", 1)[0] or d["text"].split("\n", 1)[0]
            body = d["text"].split("<p>", 1)[1].lower() or d["text"].split("\n", 1)[1].lower()
            header = html.unescape(header)
            header = header.split("|")
            current = {
         "id": d["id"],
         "parseable":True,
         "company": "",
         "url": [],
         "role": [],
         "mode": [],
         "type": [],
         "salary": [],
         "unclassified": [],
         "ambiguous": [],
      }
            if "href" in header[0].lower() or "http" in header[0].lower():
               current["url"].append(re.search(r'href="([^"]+)"', header[0]).group(1))
               header[0] = re.sub(r'<a\b[^>]*>.*?</a>', '', header[0])
               header[0] = re.sub(r'[()]', '', header[0])
            current["company"] = header[0].strip()
            for i in range(1, len(header)):
               header[i] = header[i].split("\n")[0]
               if "href" in header[i].lower() or "http" in header[i].lower():
                  current["url"].append(re.search(r'href="([^"]+)"', header[i]).group(1))
                  header[i] = re.sub(r'<a\b[^>]*>.*?</a>', '', header[i])
               clean = re.sub(r"[^\w\s]", " ", header[i]).lower()
               header[i] = header[i].strip()
               low = header[i].lower()
               if header[i] == "":
                  continue
               is_salary = any(sym in low for sym in "$€£¥₹")
               is_type = any(sym in low for sym in ["full-time", "part-time", "fulltime", "full time", "parttime", "contract", "internship", "freelance"])
               is_mode = any(sym in low for sym in ["remote", "onsite", "on-site", "hybrid", "in person"])
               is_role = bool(set(clean.split()) & ROLE_WORDS)
               signals = {
                  "salary": is_salary,
                  "type": is_type,
                  "mode": is_mode,
                  "role": is_role
               }
               fired = []
               for label, hit in signals.items():
                  if hit: 
                     fired.append(label) 
               if len(fired) == 1:
                  current[fired[0]].append(header[i])
               elif len(fired) == 0:
                  current["unclassified"].append(header[i])
               else: 
                  current["ambiguous"].append(header[i])
            extract_headers.append(current)
      else:
         extract_headers.append({
            "id":d["id"],
            "parseable":False
         })             
   return extract_headers