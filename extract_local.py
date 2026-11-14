import ollama 
import json
from pydantic import BaseModel 
from typing import Literal, Optional
import os
from anthropic import Anthropic

client = Anthropic(
)

class JobPosting(BaseModel):
  skills:list[str]
  india_eligible:Literal["yes", "no", "unclear"]
  india_evidence:Optional[str]


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
   beta_message = client.beta.messages.create(
    max_tokens=20000,
    system=SYSTEM_PROMPT,
    messages=[
        {
            "content": data,
            "role": "user",
        }
    ],
    model="claude-haiku-5-5",
  )
   return beta_message
   


if __name__ == "__main__":
    list = []
    for post in data: 
       this_post=extract_ollama(json.dumps(post))
       list.append(this_post.model_dump_json(indent=2))
    print(list)
