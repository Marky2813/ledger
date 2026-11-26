from fastapi.testclient import TestClient
from api import app 

def test_jobs_returns_list():
  r = TestClient(app).get("/jobs")
  assert r.status_code == 200
  assert isinstance(r.json(), list)

def test_jobs_with_skill(): 
  r = TestClient(app).get("/jobs?skill=python")
  jobs = r.json()
  for job in jobs:
    assert "Python" in job["skills"]