import pytest 
from header import extract_headers 

@pytest.mark.parametrize("header, bucket, expected", [
    ("Discord | Senior Software Engineer, Application Security | Remote", "role",
     "Senior Software Engineer, Application Security"),
    ("Acme | Engineer | Full Time", "type", "Full Time"),
    ("Acme | Engineer | FULL-TIME", "type", "FULL-TIME"),
    ("Freeform | Software Engineers | Onsite", "role", "Software Engineers"),
    ("Sumble | Multiple Roles | Remote", "role", "Multiple Roles")
])

def test_everything(header, bucket, expected):
  post = [{"id": 1, "text": header + "<p>body"}]
  assert expected in extract_headers(post)[0][bucket][0]

def test_company_link(): 
  h = [{
    "id":1,
    "text":"Snout <a href=\"https://snout.com/\">https://snout.com/</a> | Engineer<p></p>"}]
  r = extract_headers(h)
  assert r[0]["company"] == "Snout"
  assert r[0]["url"][0] == "https://snout.com/"

