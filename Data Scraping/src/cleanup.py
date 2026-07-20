import json
import datetime

with open("../data/personas.json", "r", encoding="utf-8") as file:
    data = json.load(file)

for persona in data:
    name = persona["name"]

    if ":" in name:
        actual_name, occupation = name.split(":", 1)
        persona["name"] = actual_name.strip()
        persona["occupation"] = occupation.strip()
    else:
        persona["occupation"] = None

with open("../data/personas.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4)

with open("../data/episodes.json", "r", encoding="utf-8") as file:
    data = json.load(file)

for episode in data:
    date = episode["air_date"]

    format = datetime.datetime.strptime(date, "%B %d, %Y").strftime("%Y-%m-%d")
    episode["air_date"] = format

with open("../data/episodes.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4)
