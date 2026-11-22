import json 
from header import extract_headers
import os
from datetime import datetime, timezone
import psycopg
from psycopg.types.json import Jsonb
from dotenv import load_dotenv

load_dotenv()

with open("data/raw/50338728.json", "r") as f:
  raw_data = json.load(f)
  
THREAD_ID = raw_data["objectId"]
data = raw_data["children"]
extracted_data = extract_headers(data)
pairs = []
for i in range(0, len(data)): 
  if(extracted_data[i]["parseable"]):
    pairs.append((extracted_data[i], data[i]))




INSERT = """
INSERT INTO hnparser.posts
  (id, company, role, type, mode, salary, url, unclassified, ambiguous, skills, india_evidence, india_eligible,
  posted_at, thread_id, raw)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (id) DO NOTHING 
"""

def to_row(record, post, thread_id): 
  return (post["id"], record["company"], record["role"], record["type"], record["mode"], record["salary"], 
  record["url"], record["unclassified"], record["ambiguous"], record["skills"], record["india_evidence"], record["india_eligible"], 
  datetime.fromtimestamp(post["created_at_i"], tz=timezone.utc), thread_id, Jsonb(post))

# psycopg connecetion
with psycopg.connect(os.getenv("DATABASE_URL")) as conn: 
  with conn.cursor() as cur: 
    rows = [to_row(r, p, THREAD_ID) for r, p in pairs]
    cur.executemany(INSERT, rows)