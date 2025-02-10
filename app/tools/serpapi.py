from pydantic import BaseModel, Field

from app.utils.package import install_package
from core import logger
from core.tools import Toolkit
from core.tools.category import ToolCategory
from core.tools.toolkit import tool, tool_func


class SerpApiConfig(BaseModel):
    api_key: str = Field(..., description="SerpApi API key")


class SearchConfig(BaseModel):
    num_results: int = Field(10, description="Number of results to return")


@tool(
    SerpApiConfig,
    title="SerpApi Tools",
    description="Tools for interacting with SerpApi",
    icon="serpapi",
    category=ToolCategory.Search,
)
class SerpApiTool(Toolkit):
    @property
    def api_key(self) -> str:
        return self.configuration.get("api_key", "")

    @tool_func(SearchConfig, title="Search Google")
    def search_google(self, query: str, _config: dict):
        """
        search_google(query, _config)

        Performs a Google search query using the provided configuration and returns
        the organic search results. The function utilizes the SerpAPI library to
        execute the search. If the library is not installed, it will attempt to
        install it and retry the search. Any errors during execution are logged and
        returned in the response.

        Args:
            query (str): The search query string.
            _config (dict): Configuration dictionary containing parameters for the
                search such as the number of results.

        Returns:
            list: A list of dictionaries containing the organic search results.
                  Returns a dictionary with an "error" key in case of exceptions.
        """
        try:
            from serpapi import GoogleSearch

            with GoogleSearch({"q": query, "num": _config.get("num_results"), "api_key": self.api_key}) as search:
                results = search.get_dict()
                return results.get("organic_results", [])
        except ImportError:
            install_package("google-search-results")
            self.search_google(query, _config)
        except Exception as e:
            logger.exception(e)
            return {"error": str(e)}

    @tool_func(SearchConfig, title="Search YouTube")
    def search_youtube(self, query: str, _config: dict):
        """
        Search for YouTube videos based on a query and configuration.

        This method uses the YoutubeSearch tool from the SerpAPI library to fetch video
        results from YouTube. The `num_results` is determined from the configuration
        provided. If the SerpAPI library is missing, the script attempts to install it
        and retries the search. Any exceptions that occur during the execution are
        logged, and an error response is returned.

        Args:
            query: str
                The search query to use for fetching YouTube results.
            _config: dict
                A configuration dictionary that may include query-specific options,
                such as the number of results to fetch and other relevant parameters.

        Returns:
            list | dict
                Returns a list of video result dictionaries if successful. If an
                exception occurs, a dictionary containing an error message is returned.
        """
        try:
            from serpapi import YoutubeSearch

            with YoutubeSearch({"q": query, "num": _config.get("num_results"), "api_key": self.api_key}) as search:
                results = search.get_dict()
                return results.get("videos", [])

        except ImportError:
            install_package("google-search-results")
            self.search_youtube(query, _config)
        except Exception as e:
            logger.exception(e)
            return {"error": str(e)}
