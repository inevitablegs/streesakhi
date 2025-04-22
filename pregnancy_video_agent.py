import os
import googleapiclient.discovery
import googleapiclient.errors
import functools
from phi.model.google import Gemini
from phi.agent import Agent
import os

API_KEY = os.getenv("YOUTUBE_API_KEY") # Replace with your actual key

def _find_pregnancy_video_global_internal(query: str, api_key: str) -> str:
    """
    Internal function to search YouTube for top 3 videos.
    Returns a string with video URLs separated by newlines or an error message.
    """
    if not query:
        return "Error: No search query provided."

    try:
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=api_key)
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=3,
            order="relevance"
        )
        response = request.execute()

        video_urls = []
        if response and 'items' in response:
            for item in response['items']:
                if 'videoId' in item.get('id', {}):
                    video_id = item['id']['videoId']
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    video_urls.append(video_url)

        if video_urls:
            return "\n".join(video_urls)
        else:
            return "No relevant videos found."

    except googleapiclient.errors.HttpError as e:
        error_content = e.content.decode('utf-8')
        if e.resp.status == 403:
            return "Error: YouTube API quota exceeded."
        elif e.resp.status == 400:
            return "Error: Invalid request."
        else:
            return f"Error: YouTube API error ({e.resp.status})."
    except Exception as e:
        return f"Error: {str(e)}"

def youtube_search_tool(query: str) -> str:
    """
    Searches YouTube for pregnancy-related videos and returns URLs only.
    Returns one URL per line or error message.
    """
    if not API_KEY or API_KEY == "YOUR_API_KEY":
        return "Error: API key not configured."

    return _find_pregnancy_video_global_internal(query=query, api_key=API_KEY)

if __name__ == "__main__":
    if not API_KEY or API_KEY == "YOUR_API_KEY":
        print("CRITICAL ERROR: YouTube API Key not configured.")
        exit()

    user_query = input("Enter your pregnancy-related query: ")
    if not user_query:
        print("No query entered.")
        exit()

    try:
        agent = Agent(
            model=Gemini(id="gemini-2.0-flash-exp", temperature=0.2),
            tools=[youtube_search_tool],
            temperature=0.3,
            # debug_mode=True,
            instructions=[
                "Use youtube_search_tool when user asks for pregnancy-related videos.",
                "Return the exact output from the tool without any modification.",
                "Do not add any text or formatting to the tool's response."
            ],
            markdown=True,
            show_tool_calls=True
        )

        response = agent.run(user_query)
        print("\nYouTube Links:")
        print(response.content if hasattr(response, "content") else str(response))


    except Exception as e:
        print(f"Error: {e}")
