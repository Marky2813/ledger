import os 
import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
DB = os.getenv("DATABASE_URL")

@app.get("/jobs")
def jobs(skill:str | None):
  sql = """
  SELECT id, company, role, type, mode, salary, url, india_evidence, skills
  FROM hnparser.posts 
  WHERE india_eligible = 'yes'
"""
  params = []
  if skill:
    sql+="""AND EXISTS(
    SELECT 1
    FROM unnest(skills) AS s
    WHERE LOWER(s)=LOWER(%s))"""
    params.append(skill) 
  with psycopg.connect(DB, row_factory=dict_row) as conn: 
    return conn.execute(sql, params).fetchall()