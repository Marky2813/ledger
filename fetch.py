import json
import requests 

BASE = "https://hn.algolia.com/api/v1"

def find_hiring_threads(n = 3 ):
  resp = requests.get(
    f"{BASE}/search_by_date", 
    params={"tags":"story,author_whoishiring", "hitsPerPage":20}
  )
  resp.raise_for_status()
  hits = resp.json()["hits"]
  return [h for h in hits if "who is hiring" in h["title"].lower()][:n]

def fetch_threads(thread_id):
  resp = requests.get(f"{BASE}/items/{thread_id}")
  resp.raise_for_status
  return resp.json() 


if __name__ == "__main__":
  for t in find_hiring_threads():
    thread = fetch_threads(t["objectID"])
    path = f"data/raw/{t['objectID']}.json"
    with open(path, "w") as f:
      json.dump(thread, f)
    print(f"{t['title']}: {len(thread['children'])} -> {path}")