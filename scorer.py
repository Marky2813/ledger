# so we need to build a scorer, this scorer needs to score the overall correctness of the parse and correctness per bucket. let's see how this can be achieved. 
import json
from header import extract_headers

with open("data/raw/evalset.json", "r") as f:
  data = json.load(f)["children"]

with open("../evals.json", "r") as f: 
  match = json.load(f)

results = extract_headers(data)

BUCKETS = ["company", "role", "type", "mode", "salary", "url", "unclassified", "ambiguous"]
stats = {b:{"correct": 0, "total": 0} for b in BUCKETS}
mismatches = []
for i in range(0, len(results)):
  if(match[i]["parseable"]): 
    for bucket in BUCKETS:
        if bucket == "company":
          match[i][bucket] = [match[i][bucket]]
          results[i][bucket] = [results[i][bucket]]
        expected = set(match[i][bucket])
        got = set(results[i][bucket])
        correct = expected & got 
        missing = expected - got 
        extra = got - expected
        stats[bucket]["correct"] = stats[bucket]["correct"] + len(correct)
        stats[bucket]["total"] = stats[bucket]["total"] + len(expected)
        if(missing): 
           mismatches.append([results[i]["id"], bucket, "missing", missing])
        if(extra):
           mismatches.append([results[i]["id"], bucket, "extra", extra])
for bucket in BUCKETS:
   print(bucket, "percentage is", stats[bucket]["correct"]/stats[bucket]["total"]*100)
   print()

print(mismatches)