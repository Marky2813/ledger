import os 
import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
app = FastAPI()
DB = os.getenv("DATABASE_URL")

class Job(BaseModel): 
  id: int
  company: str
  role: list[str]
  type: list[str]
  mode: list[str]
  salary: list[str]
  url: list[str]
  india_evidence: str 
  skills: list[str]
  hn_url: str

@app.get("/jobs", response_model=list[Job])
def jobs(skill:str | None = None):
  sql = """
  SELECT id, company, role, type, mode, salary, url, india_evidence, skills, 'https://news.ycombinator.com/item?id=' || id AS hn_url
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
  try:  
    with psycopg.connect(DB, row_factory=dict_row) as conn: 
      return conn.execute(sql, params).fetchall()
  except Exception as e:
      raise HTTPException(status_code=500, detail=f"${e}") 



@app.get("/skills")
def skills():
  sql = """
  SELECT unnest(skills) AS skill, count(*)
  FROM hnparser.posts
  WHERE india_eligible='yes'
  GROUP BY skill
  ORDER BY count(*) DESC; 
""" 
  try:
    with psycopg.connect(DB, row_factory=dict_row) as conn: 
      return conn.execute(sql).fetchall()
  except Exception as e:
      raise HTTPException(status_code=500, detail=f"${e}")  

