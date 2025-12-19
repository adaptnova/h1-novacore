"""
Wikipedia Tool for Vaeris Nova

Provides capabilities to search and retrieve information from Wikipedia.
"""

import logging
from typing import Dict, List, Any, Optional

from langchain_core.tools import BaseTool

logger = logging.getLogger("vaeris-nova.tools.wikipedia")

class WikipediaTool(BaseTool):
    """Tool for searching and retrieving information from Wikipedia."""
    
    name = "wikipedia_tool"
    description = """
    Searches Wikipedia for information on a given topic.
    Input should be a topic to search for.
    Returns relevant Wikipedia article content.
    """
    
    def _setup_wikipedia(self):
        """Set up the Wikipedia API client lazily."""
        try:
            import wikipedia
            self.wikipedia = wikipedia
            return True
        except ImportError:
            logger.error("Wikipedia library not installed. Install with 'pip install wikipedia'.")
            return False
    
    def _run(
        self, 
        query: str, 
        lang: str = "en",
        sentences: int = 3,
        include_links: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Search Wikipedia for information.
        
        Args:
            query: Topic to search for
            lang: Language code (default: 'en' for English)
            sentences: Number of sentences to return in the summary
            include_links: Whether to include links in the response
            
        Returns:
            Dictionary containing Wikipedia article information
        """
        logger.info(f"Searching Wikipedia for: {query}")
        
        # Set up Wikipedia API if not already done
        if not hasattr(self, "wikipedia"):
            if not self._setup_wikipedia():
                return {
                    "success": False,
                    "error": "Wikipedia library not installed",
                    "message": "Please install the 'wikipedia' library with 'pip install wikipedia'."
                }
        
        try:
            # Set language
            self.wikipedia.set_lang(lang)
            
            # Search for the topic
            search_results = self.wikipedia.search(query)
            
            if not search_results:
                return {
                    "success": False,
                    "error": "No results found",
                    "message": f"No Wikipedia articles found for query: {query}",
                    "query": query
                }
            
            # Get the most relevant article
            try:
                page = self.wikipedia.page(search_results[0])
            except self.wikipedia.DisambiguationError as e:
                # Handle disambiguation pages by picking the first option
                page = self.wikipedia.page(e.options[0])
            
            # Get article summary
            summary = page.summary
            
            # Limit to specified number of sentences
            if sentences > 0:
                summary_sentences = summary.split('. ')
                limited_summary = '. '.join(summary_sentences[:sentences])
                if not limited_summary.endswith('.'):
                    limited_summary += '.'
            else:
                limited_summary = summary
            
            # Create the response
            response = {
                "success": True,
                "query": query,
                "title": page.title,
                "summary": limited_summary,
                "url": page.url,
                "lang": lang
            }
            
            # Include additional info if requested
            if include_links:
                response["links"] = page.links[:20]  # Limit to 20 links
            
            return response
            
        except Exception as e:
            logger.error(f"Error searching Wikipedia: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to search Wikipedia for: {query}",
                "query": query
            }
    
    async def _arun(
        self, 
        query: str, 
        lang: str = "en",
        sentences: int = 3,
        include_links: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Asynchronous version of _run"""
        return self._run(query, lang, sentences, include_links, **kwargs)