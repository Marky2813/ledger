# this is a script to find out how many posts have pipes in them
# children array mei jo bhi posts hain, unpe traverse karo. unke text field ko check karo and then calculate the percentage

import json 

with open("data/raw/49156683.json", "r") as f:
  data = json.load(f)["children"]

count = 0

for d in data: 
  if "|" in d["text"]:
    count += 1  

print(f"Percentage of posts with pipes: {count/len(data)*100:.2f}%")