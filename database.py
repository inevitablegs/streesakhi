from phi.agent import Agent
from phi.tools.sql import SQLTools
from phi.model.google import Gemini

# 1) adjust this path if your sqlite file lives elsewhere
db_url = "sqlite:///db.sqlite3"

# 2) pick the user you want to analyze (e.g. the logged‑in user's PK)
user_id = 2

agent = Agent(
    tools=[SQLTools(db_url=db_url)],
    model=Gemini(id="gemini-2.0-flash-exp", temperature=0.4),
)

prompt = f"""
You are a personalized nutrition coach for a pregnant woman living in the North‑East region of India.  
Her daily food/drink logs for the last 2 days are stored in the table `maa_nutritionentry` with columns:
- `date`  
- `time_slot` (MORNING/NOON/EVENING/NIGHT)  
- `description` (free‑text of what she ate or drank, likely including rice dishes, fish curries, bamboo shoot preparations, fermented chutneys, local greens, seasonal fruits, etc.)  

**Step 1: Data retrieval**  
Use SQL to fetch exactly those rows for `user_id = {user_id}` where `date >= date('now','-1 days')`, sorted by `date ASC`, `time_slot ASC`.  

**Step 2: Nutrient breakdown with regional context**  
From each `description`, infer approximate quantities of:
- **Macros**: protein (e.g. fish, eggs, legumes), carbohydrates (e.g. rice, black rice, sticky rice), fats (e.g. mustard oil, groundnut oil)
- **Key micros**: iron (leafy greens like spinach, mustard greens), calcium (milk, local cheeses, tofu), folate (bamboo shoots, green leafy vegetables), vitamin D (sun‑exposed mushrooms, egg yolks), omega‑3 (freshwater fish), fiber (local vegetables, seasonal fruits), water

Use your knowledge of North‑East Indian recipes (e.g. fish tenga, khar, smoked meats, sohnt–a fermented fish paste) to estimate servings and nutrient content.

**Step 3: Summary of intake**  
Produce a table showing for each nutrient:
- **Total** consumed over the 2‑day period  
- **Daily average**  
- **Recommended range** per ICMR/WHO guidelines for pregnant women in India  

Color‑code cells:  
- 🔴 over‑consumed  
- 🔵 under‑consumed  
- 🟢 on target  

**Step 4: Actionable insights**  
For each nutrient off‑target:
- Brief note on health implications (e.g. “Low iron can worsen anemia, fatigue”)  
- Suggest 2–3 local foods or simple recipes (e.g. “Include a small bowl of saag tutum with mustard greens”, “Snack on boiled rice flakes with jaggery and coconut”)  

**Step 5: Forward recommendations**  
Based on current trends, craft a **2‑day sample meal plan** (breakfast, lunch, dinner, snacks) using North‑East staples (rice, fish, bamboo shoots, fermented chutneys, seasonal fruits) to balance nutrients.

**Bonus features:**  
- A daily **hydration reminder** (“Sip warm water or herbal ginger tea between meals”)  
- A habit tip (“Keep a small jar of roasted chana for quick protein boosts”)  
- A 3‑point “To‑Do” checklist (e.g. “Eat an extra serving of green leafy vegetables tomorrow”)

Deliver the entire report as **Markdown**, with clear headings, tables, and color‑coded nutrient summaries.
"""


# run and print
agent.print_response(prompt, markdown=True)
