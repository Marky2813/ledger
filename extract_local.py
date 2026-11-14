import ollama 
import json
from pydantic import BaseModel 
from typing import Literal, Optional
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(
   api_key=os.getenv("ANTHROPIC_API_KEY")
)

class JobPosting(BaseModel):
  skills:list[str]
  india_eligible:Literal["yes", "no", "unclear"]
  india_evidence:Optional[str]

schema = {
    "type": "object",
    "properties": {
        "skills": {"type": "array", "items": {"type": "string"}},
        "india_evidence": {"type": "string"},
        "india_eligible": {"type": "string", "enum": ["yes", "no", "unclear"]},
    },
    "required": ["skills", "india_evidence", "india_eligible"],
    "additionalProperties": False,
}

SYSTEM_PROMPT="""You extract structured data from Hacker News "Who is Hiring" job posts.
skills:
- A skill is a technology: a programming language, framework, library,
  database, cloud platform, or infrastructure tool.
- Not a skill: soft skills ("communication"), domains ("fintech",
  "payments"), job functions ("DevOps", "machine learning"), or company names.
- Include it only if the job uses it. "Team previously at Snowflake" is not
  the skill Snowflake; "our data lives in Snowflake" is.
- Empty list if none.

india_evidence (fill this BEFORE india_eligible):
- Copy the exact text, character for character, that decides eligibility.
- Copy it from the post. Do not reword it.
- null if nothing in the post mentions location, region or remote scope.

india_eligible:
- "no" if ANY part of the post restricts location to a country or region
  that is not India (e.g. "US only", "must be based in the EU",
  "authorized to work in the US"), or the job is onsite outside India.
  A restriction anywhere in the post overrides "Remote" in the header.
- "yes" if it allows worldwide/global/anywhere, any timezone, or names
  India, APAC or Asia, or an Indian city, with no restriction elsewhere.
- "unclear" for everything else, including plain "Remote" with no region.

Return only JSON, no markdown.
"""

with open("data/raw/evalset.json", "r") as f:
  data = json.load(f)["children"]

def extract_ollama(post_text:str, model: str = "qwen3:8b") -> JobPosting: 
  response = ollama.chat(
    model = model, 
    messages = [
      {"role":"system", "content":SYSTEM_PROMPT},
      {"role":"user", "content":post_text},
    ], 
    format = JobPosting.model_json_schema(), 
    think = False,
    options = {
      "temperature":0, 
      "num_predict":512
    }
  )
  return JobPosting.model_validate_json(response.message.content)

def extract_haiku(data:str):
   beta_message = client.messages.create(
    max_tokens=20000,
    system=SYSTEM_PROMPT,
    messages=[
        {
            "content": data,
            "role": "user",
        }
    ],
    output_config={"format": {"type": "json_schema", "schema": schema}},
    model="claude-haiku-5-5",
  )
   try: 
   
      resp = json.loads(beta_message.content[1].text)
      return resp
   except json.JSONDecodeError as e:
    print(beta_message.content[1].text)
    print("Invalid JSON syntax:", e)
   


if __name__ == "__main__":
    resp = []
    resp.append(extract_haiku(json.dumps(data[0])))
    print(resp)