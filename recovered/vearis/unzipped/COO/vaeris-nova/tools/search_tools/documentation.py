"""
Documentation Tool for Vaeris Nova

Provides capabilities to search and retrieve information from programming documentation.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional

from langchain_core.tools import BaseTool

logger = logging.getLogger("vaeris-nova.tools.documentation")

class DocumentationTool(BaseTool):
    """Tool for searching programming documentation."""
    
    name = "documentation_tool"
    description = """
    Searches programming documentation for a given query.
    Input should include the language/framework and the query to search for.
    Returns relevant documentation from sources like MDN, Python docs, etc.
    """
    
    def __init__(self):
        """Initialize the documentation tool."""
        super().__init__()
        
        # Define documentation sources
        self.doc_sources = {
            "python": {
                "name": "Python Documentation",
                "base_url": "https://docs.python.org/3/search.html",
                "search_params": {"q": None}
            },
            "javascript": {
                "name": "MDN Web Docs (JavaScript)",
                "base_url": "https://developer.mozilla.org/api/v1/search",
                "search_params": {"q": None, "locale": "en-US"}
            },
            "html": {
                "name": "MDN Web Docs (HTML)",
                "base_url": "https://developer.mozilla.org/api/v1/search",
                "search_params": {"q": None, "locale": "en-US", "topic": "html"}
            },
            "css": {
                "name": "MDN Web Docs (CSS)",
                "base_url": "https://developer.mozilla.org/api/v1/search",
                "search_params": {"q": None, "locale": "en-US", "topic": "css"}
            },
            "react": {
                "name": "React Documentation",
                "base_url": "https://react.dev/search",
                "search_params": {"q": None}
            },
            "nodejs": {
                "name": "Node.js Documentation",
                "base_url": "https://nodejs.org/api/",
                "search_params": {"search": None}
            }
        }
        
        # Define programming language mappings
        self.language_mappings = {
            "js": "javascript",
            "py": "python",
            "jsx": "react",
            "reactjs": "react",
            "node": "nodejs",
            "node.js": "nodejs"
        }
    
    def _run(
        self, 
        query: str, 
        language: str = "python",
        max_results: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Search programming documentation.
        
        Args:
            query: Documentation query to search for
            language: Programming language or framework
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary containing documentation search results
        """
        logger.info(f"Searching {language} documentation for: {query}")
        
        try:
            # Normalize language
            language = language.lower()
            language = self.language_mappings.get(language, language)
            
            # Check if the specified language is supported
            if language not in self.doc_sources:
                return {
                    "success": False,
                    "error": "Unsupported language",
                    "message": f"Documentation for {language} is not supported. Supported languages: {', '.join(self.doc_sources.keys())}",
                    "query": query,
                    "language": language
                }
            
            # Get documentation from the appropriate source
            doc_source = self.doc_sources[language]
            return self._search_documentation(query, language, doc_source, max_results)
            
        except Exception as e:
            logger.error(f"Error searching documentation: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to search {language} documentation for: {query}",
                "query": query,
                "language": language
            }
    
    def _search_documentation(
        self, 
        query: str, 
        language: str,
        doc_source: Dict[str, Any],
        max_results: int
    ) -> Dict[str, Any]:
        """
        Search documentation from a specific source.
        
        Args:
            query: Documentation query to search for
            language: Programming language or framework
            doc_source: Documentation source information
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary containing documentation search results
        """
        try:
            # Prepare search parameters
            search_params = doc_source["search_params"].copy()
            search_key = list(search_params.keys())[0]  # Get the parameter name for the query
            search_params[search_key] = query
            
            # Send request
            response = requests.get(
                doc_source["base_url"],
                params=search_params,
                headers={"User-Agent": "VaerisNova/0.1"}
            )
            
            # Handle different response formats
            if language in ["javascript", "html", "css"]:
                # MDN API
                results = self._parse_mdn_results(response, max_results)
            elif language == "python":
                # Python docs - needs HTML parsing
                results = self._simulate_python_docs_results(query, max_results)
            else:
                # Generic handling for other documentation sources
                results = self._simulate_docs_results(language, query, max_results)
            
            return {
                "success": True,
                "query": query,
                "language": language,
                "source": doc_source["name"],
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error searching {language} documentation: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to search {language} documentation for: {query}",
                "query": query,
                "language": language
            }
    
    def _parse_mdn_results(self, response, max_results: int) -> List[Dict[str, str]]:
        """
        Parse MDN API search results.
        
        Args:
            response: Response from the MDN API
            max_results: Maximum number of results to return
            
        Returns:
            List of formatted search results
        """
        try:
            data = response.json()
            
            if "documents" not in data:
                return []
            
            results = []
            for doc in data["documents"][:max_results]:
                results.append({
                    "title": doc.get("title", ""),
                    "summary": doc.get("summary", ""),
                    "url": f"https://developer.mozilla.org{doc.get('mdn_url', '')}",
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing MDN results: {e}")
            return []
    
    def _simulate_python_docs_results(self, query: str, max_results: int) -> List[Dict[str, str]]:
        """
        Create simulated Python documentation results.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of simulated search results
        """
        # Common Python documentation topics
        common_topics = {
            "list": {
                "title": "list - Built-in Types",
                "summary": "Lists are mutable sequences, typically used to store collections of homogeneous items.",
                "url": "https://docs.python.org/3/library/stdtypes.html#list"
            },
            "dict": {
                "title": "dict - Built-in Types",
                "summary": "A dictionary is a mapping object that maps hashable values to arbitrary objects.",
                "url": "https://docs.python.org/3/library/stdtypes.html#dict"
            },
            "string": {
                "title": "str - Built-in Types",
                "summary": "Textual data in Python is handled with str objects, or strings.",
                "url": "https://docs.python.org/3/library/stdtypes.html#str"
            },
            "class": {
                "title": "Classes - Python Tutorial",
                "summary": "Classes provide a means of bundling data and functionality together.",
                "url": "https://docs.python.org/3/tutorial/classes.html"
            },
            "function": {
                "title": "Functions - Python Tutorial",
                "summary": "Functions are defined with the def keyword and can accept parameters.",
                "url": "https://docs.python.org/3/tutorial/controlflow.html#defining-functions"
            }
        }
        
        # Check if query matches any common topics
        results = []
        query_terms = query.lower().split()
        
        for term in query_terms:
            if term in common_topics:
                results.append(common_topics[term])
        
        # If no exact matches, create generic results
        if not results:
            results = [{
                "title": f"Search results for '{query}' - Python Documentation",
                "summary": f"Python documentation related to '{query}'. The official Python documentation contains comprehensive information about the language and its standard library.",
                "url": f"https://docs.python.org/3/search.html?q={query}&check_keywords=yes&area=default"
            }]
        
        return results[:max_results]
    
    def _simulate_docs_results(self, language: str, query: str, max_results: int) -> List[Dict[str, str]]:
        """
        Create simulated documentation results for languages without API access.
        
        Args:
            language: Programming language
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of simulated search results
        """
        docs_urls = {
            "react": f"https://react.dev/search?q={query}",
            "nodejs": f"https://nodejs.org/api/?search={query}"
        }
        
        return [{
            "title": f"Search results for '{query}' - {language.capitalize()} Documentation",
            "summary": f"Documentation related to '{query}' in {language}. Please visit the official documentation for detailed information.",
            "url": docs_urls.get(language, f"https://www.google.com/search?q={query}+{language}+documentation")
        }]
    
    async def _arun(
        self, 
        query: str, 
        language: str = "python",
        max_results: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """Asynchronous version of _run"""
        return self._run(query, language, max_results, **kwargs)