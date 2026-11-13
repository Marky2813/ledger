import ollama 
from pydantic import BaseModel 
from typing import Literal, Optional

class JobPosting(BaseModel):
  skills:list[str]
  india_eligible:Literal["yes", "no", "unclear"]
  india_evidence:Optional[str]


SYSTEM_PROMPT="""You extract structured data from Hacker News "Who is Hiring" posts.
Rules:
- Use only what the post says. If a field isn't stated, use null. Never guess.
- skills: a list of skills required for the job like python, javascript, react, mongoDB, etc. Skills should be technologies and not professions like software engineering 
- india_eligible: "yes" only if the post allows remote worldwide, mentions India,
  or a region that includes India. "no" if it restricts to other countries/regions
  or requires work authorization elsewhere. Otherwise "unclear".
- india_evidence: copy the exact phrase you based india_eligible on."""

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


if __name__ == "__main__":
    sample = (
        "Temporal Technologies | Multiple positions in United States - WORK FROM HOME | FULL-TIME |<p>Temporal offers an entirely new way to build scalable and reliable applications. Temporal enables developers to focus on writing important business logic, and not on managing state or worrying about the underlying infrastructure. Backed by top VC firms, we have built a team of professionals from various successful start-ups and well-known technology companies.<p>We&#x27;re looking for senior level engineers for multiple roles - <a href=\"https:&#x2F;&#x2F;www.temporal.io&#x2F;careers\" rel=\"nofollow\">https:&#x2F;&#x2F;www.temporal.io&#x2F;careers</a><p>FEATURED ROLES:<p>Senior Software Engineer, Observability"
    )
    job = extract_ollama(sample)
    print(job.model_dump_json(indent=2))
