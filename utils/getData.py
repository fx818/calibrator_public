from dotenv import load_dotenv
load_dotenv()

# Make the OCR Tool here
def image2text(path=None):
    if not path: return ""


path = "../data/certi2.pdf"
from agentic_doc.parse import parse

# Parse a local PDF and save results to directory
result = parse(path)

with open(f"saves2.txt", "w", encoding="utf-8") as f:
    f.write(result[0].markdown)
# for i, res in enumerate(result):
print("done")
# with open("allsaves/saves.json", "w") as f:
#     f.write(result[0].json())
    
# Print the file path to the JSON file
# print(f"Final result: {result[0].result_path}")
