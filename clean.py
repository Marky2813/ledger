import re
import html

def strip_html(text):
  text = html.unescape(text)
  text = re.sub("<.*?>", "", text)
  return text
