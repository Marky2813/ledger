import ollama 
from pydantic import BaseModel 

class JobPosting(BaseModel):
  skills:list[str]
  india_eligible:Literal["yes", "no", "unclear"]
  india_evidence:Optional[str]


  SYSTEM_PROMPT="""You extract structured data from Hacker News "Who is Hiring" posts.
Rules:
- Use only what the post says. If a field isn't stated, use null. Never guess.
- skills: a list of skills required for the job like python, javascript, react, mongoDB, etc. 
- india_eligible: "yes" only if the post allows remote worldwide, mentions India,
  or a region that includes India. "no" if it restricts to other countries/regions
  or requires work authorization elsewhere. Otherwise "unclear".
- india_evidence: copy the exact phrase you based india_eligible on."""

def extract_ollama(post_text:str, model: str = "quen3:8b") -> JobPosting: 
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
    return JobPOsting.model_validate_json(response.message.content)
  )


  if __name__ == "__main__":
    sample = (
        "Acme Robotics | Senior Backend Engineer, ML Engineer | Remote (US/EU timezones only) | "
        "$150k-$190k + equity. We build warehouse robots. Python, Go, Postgres. "
        "Email jobs@acme.example"
    )
    job = extract_ollama(sample)
    print(job.model_dump_json(indent=2))
