from app.tools import *

from core.tools.category import ToolCategory
from core.tools.toolkit import Toolkit
from config.settings import settings

# test SerpApiTool
from app.tools.serpapi import SerpApiTool

serp_api_config = {
    "api_key": settings.SERPAPI_API_KEY
}
serp_api_tool = SerpApiTool(serp_api_config)
# # test SerpApiTool.search_google
search_config = {
    "num_results": 5
}
results = serp_api_tool.search_google("who is PM of USA", search_config)
print(results)

# # test SerpApiTool.search_youtube
# search_config = {
#     "num_results": 5
# }
# results = serp_api_tool.search_youtube("who is PM of USA", search_config)
# print(results)