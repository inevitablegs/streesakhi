from phi.agent import Agent
from phi.tools.sql import SQLTools
from phi.model.google import Gemini

# 1) adjust this path if your sqlite file lives elsewhere
db_url = "sqlite:///db.sqlite3"

agent = Agent(
    tools=[SQLTools(db_url=db_url)],
    model=Gemini(id="gemini-2.0-flash-exp", temperature=0.4),
)

agent.print_response("Show me all data from table maa_nutritionentry of id 1 to 28. ", markdown=True)