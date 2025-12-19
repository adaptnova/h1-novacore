"""
Model Router - Dynamic model selection for Vaeris Nova

This module provides dynamic model selection based on task requirements,
allowing Vaeris to switch between different LLMs for optimal performance.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
# Azure OpenAI is not installed in this environment
# from langchain_azure_openai import AzureChatOpenAI

logger = logging.getLogger("vaeris-nova.model_router")

# Model capabilities mapping
MODEL_CAPABILITIES = {
    # OpenAI models
    "gpt-4o": {
        "reasoning": 0.95,
        "creativity": 0.90,
        "knowledge": 0.92,
        "instruction_following": 0.95,
        "cost_efficiency": 0.75,
        "long_context": 0.85
    },
    "gpt-4o-mini": {
        "reasoning": 0.85,
        "creativity": 0.82,
        "knowledge": 0.84,
        "instruction_following": 0.90,
        "cost_efficiency": 0.87,
        "long_context": 0.75
    },
    "gpt-4-turbo": {
        "reasoning": 0.93,
        "creativity": 0.90,
        "knowledge": 0.91,
        "instruction_following": 0.94,
        "cost_efficiency": 0.70,
        "long_context": 0.90
    },
    "gpt-3.5-turbo": {
        "reasoning": 0.75,
        "creativity": 0.70,
        "knowledge": 0.72,
        "instruction_following": 0.85,
        "cost_efficiency": 0.95,
        "long_context": 0.60
    },
    
    # Anthropic models
    "claude-3-opus": {
        "reasoning": 0.95,
        "creativity": 0.85,
        "knowledge": 0.90,
        "instruction_following": 0.97,
        "cost_efficiency": 0.65,
        "long_context": 0.93
    },
    "claude-3-sonnet": {
        "reasoning": 0.88,
        "creativity": 0.82,
        "knowledge": 0.85,
        "instruction_following": 0.92,
        "cost_efficiency": 0.78,
        "long_context": 0.90
    },
    "claude-3-haiku": {
        "reasoning": 0.80,
        "creativity": 0.75,
        "knowledge": 0.78,
        "instruction_following": 0.85,
        "cost_efficiency": 0.90,
        "long_context": 0.85
    },
    
    # Google models
    "gemini-pro": {
        "reasoning": 0.85,
        "creativity": 0.82,
        "knowledge": 0.88,
        "instruction_following": 0.87,
        "cost_efficiency": 0.92,
        "long_context": 0.80
    },
    "gemini-ultra": {
        "reasoning": 0.93,
        "creativity": 0.90,
        "knowledge": 0.92,
        "instruction_following": 0.92,
        "cost_efficiency": 0.75,
        "long_context": 0.88
    },
    
    # Mistral models
    "mistral-large": {
        "reasoning": 0.87,
        "creativity": 0.80,
        "knowledge": 0.85,
        "instruction_following": 0.90,
        "cost_efficiency": 0.85,
        "long_context": 0.88
    },
    "mistral-medium": {
        "reasoning": 0.80,
        "creativity": 0.75,
        "knowledge": 0.78,
        "instruction_following": 0.85,
        "cost_efficiency": 0.92,
        "long_context": 0.80
    },
    "mistral-small": {
        "reasoning": 0.70,
        "creativity": 0.65,
        "knowledge": 0.68,
        "instruction_following": 0.80,
        "cost_efficiency": 0.98,
        "long_context": 0.70
    }
}

class ModelRouter:
    """
    Dynamic model router that selects the appropriate LLM based on task requirements.
    """
    
    def __init__(
        self,
        default_model: str = "gpt-4o",
        model_preferences: Dict[str, float] = None,
        api_key_env_vars: Dict[str, str] = None
    ):
        """
        Initialize the model router.
        
        Args:
            default_model: Default model to use when no specific requirements are provided
            model_preferences: Custom model preferences to override defaults
            api_key_env_vars: Custom environment variable names for API keys
        """
        self.default_model = default_model
        self.model_capabilities = MODEL_CAPABILITIES
        
        # Update with custom preferences if provided
        if model_preferences:
            for model, prefs in model_preferences.items():
                if model in self.model_capabilities:
                    self.model_capabilities[model].update(prefs)
        
        # Set up API key environment variable names
        self.api_key_env_vars = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY",
            "mistral": "MISTRAL_API_KEY",
            "azure_openai": "AZURE_OPENAI_API_KEY",
        }
        
        # Override with custom environment variable names if provided
        if api_key_env_vars:
            self.api_key_env_vars.update(api_key_env_vars)
        
        # Cache for model instances
        self.model_cache = {}
        
        logger.info(f"ModelRouter initialized with default model: {default_model}")
    
    def get_model(
        self,
        model_name: str = None,
        temperature: float = 0.7,
        streaming: bool = True,
        **kwargs
    ) -> BaseChatModel:
        """
        Get a model by name with specified parameters.
        
        Args:
            model_name: Name of the model to use (defaults to self.default_model)
            temperature: Temperature setting for the model
            streaming: Whether to enable streaming responses
            **kwargs: Additional model-specific parameters
            
        Returns:
            Initialized LangChain chat model
        """
        if model_name is None:
            model_name = self.default_model
        
        # Check cache first
        cache_key = f"{model_name}_{temperature}_{streaming}"
        if cache_key in self.model_cache:
            return self.model_cache[cache_key]
        
        model = None
        
        # OpenAI models
        if model_name.startswith("gpt-"):
            api_key = os.environ.get(self.api_key_env_vars["openai"])
            if not api_key:
                logger.warning(f"OpenAI API key not found in environment variable {self.api_key_env_vars['openai']}")
            
            # Use environment settings if available
            openai_api_base = os.environ.get("OPENAI_API_URL", None)
            
            model_kwargs = {
                "model": model_name,
                "temperature": temperature,
                "streaming": streaming
            }
            
            # Add API base if specified
            if openai_api_base:
                model_kwargs["openai_api_base"] = openai_api_base
                
            # Add any additional kwargs
            model_kwargs.update(kwargs)
            
            model = ChatOpenAI(**model_kwargs)
        
        # Anthropic models
        elif model_name.startswith("claude-"):
            api_key = os.environ.get(self.api_key_env_vars["anthropic"])
            if not api_key:
                logger.warning(f"Anthropic API key not found in environment variable {self.api_key_env_vars['anthropic']}")
            
            # Use environment settings if available
            anthropic_api_url = os.environ.get("ANTHROPIC_API_URL", None)
            
            model_kwargs = {
                "model": model_name,
                "temperature": temperature,
                "streaming": streaming
            }
            
            # Add API URL if specified
            if anthropic_api_url:
                model_kwargs["anthropic_api_url"] = anthropic_api_url
            
            # Add any additional kwargs
            model_kwargs.update(kwargs)
            
            model = ChatAnthropic(**model_kwargs)
        
        # Google models
        elif model_name.startswith("gemini-"):
            api_key = os.environ.get(self.api_key_env_vars["google"])
            if not api_key:
                logger.warning(f"Google API key not found in environment variable {self.api_key_env_vars['google']}")
            
            model = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                convert_system_message_to_human=True,
                **kwargs
            )
        
        # Mistral models
        elif model_name.startswith("mistral-"):
            api_key = os.environ.get(self.api_key_env_vars["mistral"])
            if not api_key:
                logger.warning(f"Mistral API key not found in environment variable {self.api_key_env_vars['mistral']}")
            
            model = ChatMistralAI(
                model=model_name,
                temperature=temperature,
                streaming=streaming,
                **kwargs
            )
        
        # Azure OpenAI models
        elif model_name.startswith("azure-"):
            # Extract the base model from the name after "azure-" prefix
            base_model = model_name[len("azure-"):]
            
            api_key = os.environ.get(self.api_key_env_vars["azure_openai"])
            if not api_key:
                logger.warning(f"Azure OpenAI API key not found in environment variable {self.api_key_env_vars['azure_openai']}")
            
            # Check for required Azure environment variables
            azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
            if not azure_endpoint:
                logger.warning("Azure OpenAI endpoint not found in AZURE_OPENAI_ENDPOINT")
            
            logger.error(f"Azure OpenAI not available in this environment")
            # Fall back to default model
            return self.get_model(self.default_model, temperature, streaming, **kwargs)
        
        # Unknown model
        else:
            logger.error(f"Unknown model: {model_name}, falling back to default")
            return self.get_model(self.default_model, temperature, streaming, **kwargs)
        
        # Cache the model instance
        self.model_cache[cache_key] = model
        
        return model
    
    def select_model_for_task(
        self,
        task_description: str,
        requirements: Dict[str, float] = None,
        available_models: List[str] = None
    ) -> str:
        """
        Select the best model for a given task based on requirements.
        
        Args:
            task_description: Description of the task to be performed
            requirements: Dictionary of capability requirements and their importance
            available_models: List of models to consider (defaults to all models)
            
        Returns:
            Name of the selected model
        """
        # Use all models if available_models is not specified
        if available_models is None:
            available_models = list(self.model_capabilities.keys())
        
        # If no specific requirements, return default model
        if not requirements:
            for model in [self.default_model] + available_models:
                if model in self.model_capabilities:
                    return model
            
            # Fall back to first available model if default not available
            return available_models[0]
        
        # Calculate scores for each model
        model_scores = {}
        for model in available_models:
            if model not in self.model_capabilities:
                continue
                
            score = 0
            for capability, importance in requirements.items():
                if capability in self.model_capabilities[model]:
                    score += self.model_capabilities[model][capability] * importance
            
            model_scores[model] = score
        
        # Return the model with the highest score
        if model_scores:
            best_model = max(model_scores, key=model_scores.get)
            logger.info(f"Selected model {best_model} for task: {task_description[:50]}...")
            return best_model
        
        # Fall back to default if no models matched
        logger.warning(f"No suitable model found for task, using default: {self.default_model}")
        return self.default_model
    
    def get_all_available_models(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available models with their capabilities.
        
        Returns:
            List of dictionaries containing model information
        """
        available_models = []
        
        for model_name, capabilities in self.model_capabilities.items():
            # Check if the API key is available
            api_key_available = False
            
            if model_name.startswith("gpt-"):
                api_key_available = bool(os.environ.get(self.api_key_env_vars["openai"]))
                provider = "OpenAI"
            elif model_name.startswith("claude-"):
                api_key_available = bool(os.environ.get(self.api_key_env_vars["anthropic"]))
                provider = "Anthropic"
            elif model_name.startswith("gemini-"):
                api_key_available = bool(os.environ.get(self.api_key_env_vars["google"]))
                provider = "Google"
            elif model_name.startswith("mistral-"):
                api_key_available = bool(os.environ.get(self.api_key_env_vars["mistral"]))
                provider = "Mistral AI"
            elif model_name.startswith("azure-"):
                api_key_available = bool(os.environ.get(self.api_key_env_vars["azure_openai"]))
                provider = "Azure OpenAI"
            else:
                provider = "Unknown"
            
            available_models.append({
                "name": model_name,
                "provider": provider,
                "available": api_key_available,
                "capabilities": capabilities,
                "is_default": model_name == self.default_model
            })
        
        return available_models