"""
Web Search Tool for Vaeris Nova

Provides capabilities to search the web for information.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Union
from bs4 import BeautifulSoup

from langchain_core.tools import BaseTool

logger = logging.getLogger("vaeris-nova.tools.web_search")

class WebSearchTool(BaseTool):
    """Tool for searching the web for information."""
    
    name = "web_search_tool"
    description = """
    Searches the web for information on a given query.
    Input should be a search query string.
    Returns search results with relevant information.
    """
    
    def __init__(
        self,
        serper_api_key: str = None,
        serpapi_api_key: str = None,
        ddg_proxy: str = None
    ):
        """
        Initialize the web search tool.
        
        Args:
            serper_api_key: API key for Serper.dev
            serpapi_api_key: API key for SerpAPI
            ddg_proxy: URL for DuckDuckGo proxy
        """
        super().__init__()
        
        # Set API keys from parameters or environment variables
        self.serper_api_key = serper_api_key or os.environ.get("SERPER_API_KEY")
        self.serpapi_api_key = serpapi_api_key or os.environ.get("SERPAPI_API_KEY")
        self.ddg_proxy = ddg_proxy or os.environ.get("DDG_PROXY_URL")
        
        # Default to using DuckDuckGo if no API keys are available
        self.default_engine = "duckduckgo"
        
        # If Serper API key is available, use it as the default
        if self.serper_api_key:
            self.default_engine = "serper"
        # Otherwise, if SerpAPI key is available, use it
        elif self.serpapi_api_key:
            self.default_engine = "serpapi"
    
    def _run(
        self, 
        query: str, 
        engine: str = None, 
        num_results: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Search the web for information.
        
        Args:
            query: Search query string
            engine: Search engine to use ('serper', 'serpapi', 'duckduckgo')
            num_results: Number of results to return
            
        Returns:
            Dictionary containing search results
        """
        logger.info(f"Searching web for: {query}")
        
        # Use specified engine or fall back to default
        engine = engine or self.default_engine
        
        try:
            # Choose search implementation based on engine
            if engine == "serper" and self.serper_api_key:
                return self._search_serper(query, num_results)
            elif engine == "serpapi" and self.serpapi_api_key:
                return self._search_serpapi(query, num_results)
            else:
                # Fall back to DuckDuckGo
                return self._search_duckduckgo(query, num_results)
                
        except Exception as e:
            logger.error(f"Error searching web: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to search web for: {query}"
            }
    
    def _search_serper(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Search the web using Serper.dev API.
        
        Args:
            query: Search query string
            num_results: Number of results to return
            
        Returns:
            Dictionary containing search results
        """
        try:
            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": query,
                "num": num_results
            }
            
            response = requests.post(
                "https://google.serper.dev/search",
                headers=headers,
                json=payload
            )
            
            response.raise_for_status()
            search_results = response.json()
            
            # Process and format results
            formatted_results = []
            
            # Process organic results
            if "organic" in search_results:
                for result in search_results["organic"][:num_results]:
                    formatted_results.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "source": "serper.dev"
                    })
            
            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "count": len(formatted_results),
                "engine": "serper"
            }
            
        except Exception as e:
            logger.error(f"Error with Serper search: {e}")
            raise
    
    def _search_serpapi(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Search the web using SerpAPI.
        
        Args:
            query: Search query string
            num_results: Number of results to return
            
        Returns:
            Dictionary containing search results
        """
        try:
            params = {
                "q": query,
                "num": num_results,
                "api_key": self.serpapi_api_key
            }
            
            response = requests.get(
                "https://serpapi.com/search",
                params=params
            )
            
            response.raise_for_status()
            search_results = response.json()
            
            # Process and format results
            formatted_results = []
            
            # Process organic results
            if "organic_results" in search_results:
                for result in search_results["organic_results"][:num_results]:
                    formatted_results.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "source": "serpapi"
                    })
            
            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "count": len(formatted_results),
                "engine": "serpapi"
            }
            
        except Exception as e:
            logger.error(f"Error with SerpAPI search: {e}")
            raise
    
    def _search_duckduckgo(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Search the web using DuckDuckGo.
        
        Args:
            query: Search query string
            num_results: Number of results to return
            
        Returns:
            Dictionary containing search results
        """
        try:
            # Use custom proxy if available
            if self.ddg_proxy:
                params = {
                    "q": query,
                    "max_results": num_results
                }
                
                response = requests.get(
                    self.ddg_proxy,
                    params=params
                )
                
                response.raise_for_status()
                return response.json()
            
            # Otherwise, fall back to a simple scraping approach
            # Note: This is not ideal and may break if the site structure changes
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(
                f"https://html.duckduckgo.com/html/?q={query}",
                headers=headers
            )
            
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")
            results = soup.find_all("div", class_="result")
            
            formatted_results = []
            for result in results[:num_results]:
                title_element = result.find("a", class_="result__a")
                snippet_element = result.find("a", class_="result__snippet")
                
                if title_element and snippet_element:
                    title = title_element.text.strip()
                    link = title_element.get("href", "")
                    snippet = snippet_element.text.strip()
                    
                    formatted_results.append({
                        "title": title,
                        "link": link,
                        "snippet": snippet,
                        "source": "duckduckgo"
                    })
            
            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "count": len(formatted_results),
                "engine": "duckduckgo"
            }
            
        except Exception as e:
            logger.error(f"Error with DuckDuckGo search: {e}")
            
            # Return a minimal error response with empty results to allow the agent to continue
            return {
                "success": False,
                "query": query,
                "results": [],
                "count": 0,
                "engine": "duckduckgo",
                "error": str(e),
                "message": "Search failed, but here's what we know about the query."
            }
    
    async def _arun(
        self, 
        query: str, 
        engine: str = None, 
        num_results: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """Asynchronous version of _run"""
        return self._run(query, engine, num_results, **kwargs)