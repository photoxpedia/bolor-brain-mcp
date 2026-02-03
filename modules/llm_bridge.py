"""
LLM Bridge for Bolor Brain MCP.

Provides optional LLM integration that works WITH or WITHOUT an LLM:
- When disabled: Uses template-based formatting (pure symbolic)
- When enabled: Uses LLM for synthesis, creativity, and ambiguity resolution
- Supports OpenAI, Anthropic, Ollama, and custom providers
- Lazy-loads LLM client on first use
- Falls back to symbolic formatting when LLM fails (configurable)

Three use cases:
1. synthesis - Convert structured reasoning results to natural language
2. creative - Enhance symbolic ideas with LLM creativity
3. ambiguous - Resolve uncertain/ambiguous reasoning results
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .config import Config

logger = logging.getLogger(__name__)


class LLMBridgeError(Exception):
    """Exception raised when LLM bridge operations fail."""
    pass


@dataclass
class LLMResponse:
    """
    Response from an LLM bridge operation.

    Attributes:
        success: Whether the operation succeeded
        content: The generated text content
        used_llm: Whether the LLM was actually used (False if fallback)
        fallback_reason: Why fallback was used (if any)
        ideas: Optional list of ideas (for creativity enhancement)
        metadata: Optional additional metadata
    """
    success: bool
    content: str
    used_llm: bool
    fallback_reason: Optional[str] = None
    ideas: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMBridge:
    """
    Bridge for optional LLM integration.

    Handles LLM calls with lazy loading, fallback, and use-case filtering.
    Works in two modes:
    - Disabled: All methods return template-formatted results
    - Enabled: Uses LLM for configured use cases, with optional fallback

    Example:
        >>> from modules.config import Config
        >>> config = Config(llm_enabled=False)
        >>> bridge = LLMBridge(config)
        >>> response = await bridge.synthesize({"conclusion": "X"}, "brief")
        >>> print(response.used_llm)  # False - LLM disabled
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize the LLM bridge.

        Args:
            config: Configuration object with LLM settings
        """
        self.config = config
        self.enabled = config.llm_enabled
        self._client: Optional[Any] = None  # Lazy-loaded

    @property
    def client(self) -> Any:
        """
        Get the LLM client, initializing if needed.

        Returns:
            The initialized LLM client

        Raises:
            LLMBridgeError: If client initialization fails
        """
        if self._client is None:
            self._client = self._init_client()
        return self._client

    def _init_client(self) -> Any:
        """
        Initialize the LLM client based on provider.

        Returns:
            Initialized client for the configured provider

        Raises:
            LLMBridgeError: If initialization fails or provider is unsupported
        """
        provider = self.config.llm_provider

        try:
            if provider == "openai":
                return self._init_openai_client()
            elif provider == "anthropic":
                return self._init_anthropic_client()
            elif provider == "ollama":
                return self._init_ollama_client()
            elif provider == "custom":
                return self._init_custom_client()
            else:
                raise LLMBridgeError(f"Unsupported provider: {provider}")
        except ImportError as e:
            raise LLMBridgeError(
                f"Failed to import {provider} client library. "
                f"Please install the required package: {e}"
            )
        except Exception as e:
            raise LLMBridgeError(f"Failed to initialize {provider} client: {e}")

    def _init_openai_client(self) -> Any:
        """Initialize OpenAI client."""
        try:
            from openai import AsyncOpenAI
            return AsyncOpenAI(api_key=self.config.llm_api_key)
        except ImportError:
            # Return a mock client for testing if openai not installed
            logger.warning("OpenAI library not installed, using mock client")
            return _MockOpenAIClient(self.config.llm_api_key)

    def _init_anthropic_client(self) -> Any:
        """Initialize Anthropic client."""
        try:
            from anthropic import AsyncAnthropic
            return AsyncAnthropic(api_key=self.config.llm_api_key)
        except ImportError:
            logger.warning("Anthropic library not installed, using mock client")
            return _MockAnthropicClient(self.config.llm_api_key)

    def _init_ollama_client(self) -> Any:
        """Initialize Ollama client."""
        try:
            import httpx
            base_url = self.config.llm_base_url or "http://localhost:11434"
            return _OllamaClient(base_url, self.config.llm_model)
        except ImportError:
            logger.warning("httpx library not installed, using mock client")
            return _MockOllamaClient(
                self.config.llm_base_url or "http://localhost:11434",
                self.config.llm_model
            )

    def _init_custom_client(self) -> Any:
        """Initialize custom API client."""
        if not self.config.llm_base_url:
            raise LLMBridgeError("Custom provider requires llm_base_url")
        return _CustomClient(
            self.config.llm_base_url,
            self.config.llm_api_key,
            self.config.llm_model
        )

    async def _call_llm(self, prompt: str, system: Optional[str] = None) -> str:
        """
        Make an API call to the LLM.

        Args:
            prompt: The user prompt
            system: Optional system prompt

        Returns:
            The LLM's response text

        Raises:
            Exception: If the API call fails
        """
        provider = self.config.llm_provider
        model = self.config.llm_model

        if provider == "openai":
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content

        elif provider == "anthropic":
            response = await self.client.messages.create(
                model=model,
                max_tokens=4096,
                system=system or "",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text

        elif provider == "ollama":
            return await self.client.generate(prompt, system)

        elif provider == "custom":
            return await self.client.generate(prompt, system)

        else:
            raise LLMBridgeError(f"Unsupported provider: {provider}")

    def _sanitize_error(self, error: Exception) -> str:
        """
        Sanitize error message to remove sensitive information like API keys.

        Args:
            error: The exception to sanitize

        Returns:
            Sanitized error message string
        """
        error_msg = str(error)
        if self.config.llm_api_key and self.config.llm_api_key in error_msg:
            error_msg = error_msg.replace(self.config.llm_api_key, "***API_KEY***")
        return error_msg

    def _should_use_llm(self, use_case: str) -> bool:
        """
        Check if LLM should be used for a given use case.

        Args:
            use_case: The use case (synthesis, creative, ambiguous)

        Returns:
            True if LLM should be used, False otherwise
        """
        return self.enabled and use_case in self.config.llm_use_for

    async def synthesize(
        self,
        structured_result: Dict[str, Any],
        output_style: str = "detailed"
    ) -> LLMResponse:
        """
        Convert structured reasoning result to natural language.

        Args:
            structured_result: The structured reasoning output
            output_style: Output style (brief, detailed, technical)

        Returns:
            LLMResponse with synthesized text
        """
        # Check if we should use LLM
        if not self._should_use_llm("synthesis"):
            reason = "llm_disabled" if not self.enabled else "use_case_not_enabled"
            return LLMResponse(
                success=True,
                content=self._format_without_llm(structured_result, output_style),
                used_llm=False,
                fallback_reason=reason
            )

        # Try LLM call
        try:
            system_prompt = self._get_synthesis_system_prompt(output_style)
            prompt = self._format_synthesis_prompt(structured_result)

            content = await self._call_llm(prompt, system_prompt)

            return LLMResponse(
                success=True,
                content=content,
                used_llm=True
            )

        except Exception as e:
            error_msg = self._sanitize_error(e)
            logger.error(f"LLM synthesis failed: {error_msg}")

            # Check if fallback is enabled
            if self.config.llm_fallback_to_symbolic:
                return LLMResponse(
                    success=True,
                    content=self._format_without_llm(structured_result, output_style),
                    used_llm=False,
                    fallback_reason="llm_error",
                    metadata={
                        "error": error_msg,
                        "provider": self.config.llm_provider,
                        "model": self.config.llm_model,
                        "timestamp": time.time()
                    }
                )
            else:
                raise LLMBridgeError(f"LLM call failed and fallback is disabled: {error_msg}")

    async def enhance_creativity(
        self,
        base_ideas: List[str],
        challenge: str,
        constraints: Optional[List[str]] = None
    ) -> LLMResponse:
        """
        Enhance base ideas with LLM creativity.

        Args:
            base_ideas: Symbolically generated base ideas
            challenge: The challenge/problem being addressed
            constraints: Optional constraints to consider

        Returns:
            LLMResponse with enhanced ideas
        """
        constraints = constraints or []

        # Check if we should use LLM
        if not self._should_use_llm("creative"):
            # Return formatted base ideas
            formatted_content = self._format_ideas_without_llm(
                base_ideas, challenge, constraints
            )
            return LLMResponse(
                success=True,
                content=formatted_content,
                used_llm=False,
                fallback_reason="llm_disabled" if not self.enabled else "use_case_not_enabled",
                ideas=base_ideas
            )

        # Try LLM call
        try:
            system_prompt = (
                "You are a creative thinking assistant. Enhance and expand upon "
                "the given ideas while respecting any constraints. Generate novel "
                "variations and combinations."
            )

            prompt = self._format_creativity_prompt(base_ideas, challenge, constraints)

            content = await self._call_llm(prompt, system_prompt)

            # Parse enhanced ideas from response
            enhanced_ideas = self._parse_ideas_from_response(content, base_ideas)

            return LLMResponse(
                success=True,
                content=content,
                used_llm=True,
                ideas=enhanced_ideas
            )

        except Exception as e:
            error_msg = self._sanitize_error(e)
            logger.error(f"LLM creativity enhancement failed: {error_msg}")

            if self.config.llm_fallback_to_symbolic:
                formatted_content = self._format_ideas_without_llm(
                    base_ideas, challenge, constraints
                )
                return LLMResponse(
                    success=True,
                    content=formatted_content,
                    used_llm=False,
                    fallback_reason="llm_error",
                    ideas=base_ideas,
                    metadata={
                        "error": error_msg,
                        "provider": self.config.llm_provider,
                        "model": self.config.llm_model,
                        "timestamp": time.time()
                    }
                )
            else:
                raise LLMBridgeError(f"LLM call failed and fallback is disabled: {error_msg}")

    async def resolve_ambiguity(
        self,
        symbolic_result: Dict[str, Any],
        confidence: float
    ) -> LLMResponse:
        """
        Resolve ambiguous reasoning results using LLM.

        Args:
            symbolic_result: Ambiguous symbolic reasoning output
            confidence: Overall confidence in the result (0.0-1.0)

        Returns:
            LLMResponse with resolved interpretation
        """
        # Check if we should use LLM
        if not self._should_use_llm("ambiguous"):
            content = self._format_ambiguity_without_llm(symbolic_result, confidence)
            return LLMResponse(
                success=True,
                content=content,
                used_llm=False,
                fallback_reason="llm_disabled" if not self.enabled else "use_case_not_enabled"
            )

        # Try LLM call
        try:
            system_prompt = (
                "You are an expert at interpreting ambiguous information. "
                "Analyze the given interpretations and provide a clear resolution "
                "with reasoning for your choice."
            )

            prompt = self._format_ambiguity_prompt(symbolic_result, confidence)

            content = await self._call_llm(prompt, system_prompt)

            return LLMResponse(
                success=True,
                content=content,
                used_llm=True
            )

        except Exception as e:
            error_msg = self._sanitize_error(e)
            logger.error(f"LLM ambiguity resolution failed: {error_msg}")

            if self.config.llm_fallback_to_symbolic:
                content = self._format_ambiguity_without_llm(symbolic_result, confidence)
                return LLMResponse(
                    success=True,
                    content=content,
                    used_llm=False,
                    fallback_reason="llm_error",
                    metadata={
                        "error": error_msg,
                        "provider": self.config.llm_provider,
                        "model": self.config.llm_model,
                        "timestamp": time.time()
                    }
                )
            else:
                raise LLMBridgeError(f"LLM call failed and fallback is disabled: {error_msg}")

    # ==================== Template Formatting (No LLM) ====================

    def _format_without_llm(
        self,
        result: Dict[str, Any],
        style: str = "detailed"
    ) -> str:
        """
        Format structured result as text without LLM.

        Args:
            result: The structured result
            style: Output style (brief, detailed, technical)

        Returns:
            Formatted text string
        """
        if style == "brief":
            return self._format_brief(result)
        elif style == "technical":
            return self._format_technical(result)
        else:  # detailed
            return self._format_detailed(result)

    def _format_brief(self, result: Dict[str, Any]) -> str:
        """Format as brief summary."""
        lines = []

        if "conclusion" in result:
            lines.append(f"Conclusion: {result['conclusion']}")

        if "confidence" in result:
            lines.append(f"Confidence: {result['confidence']:.0%}")

        if not lines:
            # Fallback: just stringify the result
            return str(result)

        return " | ".join(lines)

    def _format_detailed(self, result: Dict[str, Any]) -> str:
        """Format as detailed explanation."""
        lines = []

        if "conclusion" in result:
            lines.append(f"**Conclusion**: {result['conclusion']}")

        if "confidence" in result:
            lines.append(f"**Confidence**: {result['confidence']:.0%}")

        if "reasoning_steps" in result:
            lines.append("\n**Reasoning Steps**:")
            for i, step in enumerate(result["reasoning_steps"], 1):
                lines.append(f"  {i}. {step}")

        if "evidence" in result:
            lines.append("\n**Supporting Evidence**:")
            for evidence in result["evidence"]:
                lines.append(f"  - {evidence}")

        if not lines:
            # Fallback: pretty-print JSON
            return json.dumps(result, indent=2)

        return "\n".join(lines)

    def _format_technical(self, result: Dict[str, Any]) -> str:
        """Format as technical output (JSON-like)."""
        return json.dumps(result, indent=2, default=str)

    def _format_ideas_without_llm(
        self,
        ideas: List[str],
        challenge: str,
        constraints: List[str]
    ) -> str:
        """Format ideas list without LLM enhancement."""
        lines = [f"**Challenge**: {challenge}"]

        if constraints:
            lines.append(f"**Constraints**: {', '.join(constraints)}")

        lines.append("\n**Ideas**:")
        for i, idea in enumerate(ideas, 1):
            lines.append(f"  {i}. {idea}")

        return "\n".join(lines)

    def _format_ambiguity_without_llm(
        self,
        result: Dict[str, Any],
        confidence: float
    ) -> str:
        """Format ambiguous result without LLM resolution."""
        lines = [f"**Ambiguity Detected** (confidence: {confidence:.0%})"]

        # Find highest-scoring interpretation
        best_key = None
        best_score = -1

        for key, value in result.items():
            if isinstance(value, dict) and "score" in value:
                if value["score"] > best_score:
                    best_score = value["score"]
                    best_key = key

        if best_key:
            best_value = result[best_key]
            lines.append(f"\n**Most Likely Interpretation**: {best_key}")
            if "meaning" in best_value:
                lines.append(f"  Meaning: {best_value['meaning']}")
            lines.append(f"  Score: {best_score:.2f}")

            lines.append("\n**Alternative Interpretations**:")
            for key, value in result.items():
                if key != best_key and isinstance(value, dict):
                    meaning = value.get("meaning", "unknown")
                    score = value.get("score", 0)
                    lines.append(f"  - {key}: {meaning} (score: {score:.2f})")
        else:
            lines.append("\n" + json.dumps(result, indent=2))

        return "\n".join(lines)

    # ==================== Prompt Formatting ====================

    def _get_synthesis_system_prompt(self, style: str) -> str:
        """Get system prompt for synthesis based on style."""
        base = (
            "You are an expert at explaining reasoning results in clear, "
            "natural language. Convert the structured reasoning output into "
            "a coherent explanation."
        )

        if style == "brief":
            return base + " Keep your response concise (1-2 sentences)."
        elif style == "technical":
            return base + " Use precise technical language and include all details."
        else:
            return base + " Provide a thorough but accessible explanation."

    def _format_synthesis_prompt(self, result: Dict[str, Any]) -> str:
        """Format prompt for synthesis."""
        return (
            "Please synthesize the following reasoning result into natural language:\n\n"
            f"{json.dumps(result, indent=2, default=str)}"
        )

    def _format_creativity_prompt(
        self,
        ideas: List[str],
        challenge: str,
        constraints: List[str]
    ) -> str:
        """Format prompt for creativity enhancement."""
        prompt_parts = [
            f"Challenge: {challenge}",
            "",
            "Base Ideas:",
        ]

        for i, idea in enumerate(ideas, 1):
            prompt_parts.append(f"{i}. {idea}")

        if constraints:
            prompt_parts.append("")
            prompt_parts.append(f"Constraints: {', '.join(constraints)}")

        prompt_parts.append("")
        prompt_parts.append(
            "Please enhance these ideas with creative variations, "
            "novel combinations, and new perspectives while respecting the constraints."
        )

        return "\n".join(prompt_parts)

    def _format_ambiguity_prompt(
        self,
        result: Dict[str, Any],
        confidence: float
    ) -> str:
        """Format prompt for ambiguity resolution."""
        return (
            f"The following reasoning result has low confidence ({confidence:.0%}) "
            "and multiple possible interpretations:\n\n"
            f"{json.dumps(result, indent=2, default=str)}\n\n"
            "Please analyze these interpretations and provide:\n"
            "1. The most likely correct interpretation\n"
            "2. Your reasoning for this choice\n"
            "3. Any caveats or conditions"
        )

    def _parse_ideas_from_response(
        self,
        response: str,
        base_ideas: List[str]
    ) -> List[str]:
        """
        Parse enhanced ideas from LLM response.

        Args:
            response: LLM response text
            base_ideas: Original base ideas

        Returns:
            List of ideas (enhanced or original if parsing fails)
        """
        # Simple parsing: look for numbered items
        ideas = []
        lines = response.split("\n")

        for line in lines:
            line = line.strip()
            # Check for numbered items (1., 2., etc.)
            if line and len(line) > 2 and line[0].isdigit() and line[1] == ".":
                idea = line[2:].strip()
                if idea:
                    ideas.append(idea)
            # Check for bullet points
            elif line.startswith("- ") or line.startswith("* "):
                idea = line[2:].strip()
                if idea:
                    ideas.append(idea)

        # Return parsed ideas, original base ideas, or fallback message
        if ideas:
            return ideas
        elif base_ideas:
            return base_ideas
        else:
            logger.warning("No ideas could be parsed and no base ideas provided")
            return ["No ideas generated - please try again"]


# ==================== Client Implementations ====================

class _OllamaClient:
    """Async Ollama client."""

    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """
        Generate response from Ollama.

        Args:
            prompt: The user prompt
            system: Optional system prompt

        Returns:
            The generated response text

        Raises:
            LLMBridgeError: If connection fails or response is invalid
        """
        import httpx

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=120.0)
                response.raise_for_status()
                data = response.json()
                if "response" not in data:
                    raise LLMBridgeError(f"Invalid Ollama response format: missing 'response' key in {list(data.keys())}")
                return data["response"]
        except httpx.ConnectError:
            raise LLMBridgeError(f"Cannot connect to Ollama at {self.base_url}. Is it running?")
        except httpx.TimeoutException:
            raise LLMBridgeError(f"Ollama request timed out after 120 seconds")
        except httpx.HTTPStatusError as e:
            raise LLMBridgeError(f"Ollama HTTP error: {e.response.status_code} - {e.response.text}")
        except KeyError as e:
            raise LLMBridgeError(f"Invalid Ollama response structure: missing {e}")


class _CustomClient:
    """Custom API client for OpenAI-compatible endpoints."""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str],
        model: str
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """Generate response from custom endpoint."""
        import httpx

        url = f"{self.base_url}/v1/chat/completions"

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages
        }

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers=headers,
                timeout=120.0
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]


# ==================== Mock Clients (for testing without dependencies) ====================

class _MockOpenAIClient:
    """Mock OpenAI client for testing."""

    def __init__(self, api_key: Optional[str]) -> None:
        self.api_key = api_key

    @property
    def chat(self) -> "_MockChat":
        return _MockChat()


class _MockChat:
    @property
    def completions(self) -> "_MockCompletions":
        return _MockCompletions()


class _MockCompletions:
    async def create(self, model: str, messages: List[Dict]) -> Any:
        # Return a mock response
        class MockChoice:
            class MockMessage:
                content = "Mock LLM response"
            message = MockMessage()

        class MockResponse:
            choices = [MockChoice()]

        return MockResponse()


class _MockAnthropicClient:
    """Mock Anthropic client for testing."""

    def __init__(self, api_key: Optional[str]) -> None:
        self.api_key = api_key

    @property
    def messages(self) -> "_MockMessages":
        return _MockMessages()


class _MockMessages:
    async def create(
        self,
        model: str,
        max_tokens: int,
        system: str,
        messages: List[Dict]
    ) -> Any:
        class MockContent:
            text = "Mock Anthropic response"

        class MockResponse:
            content = [MockContent()]

        return MockResponse()


class _MockOllamaClient:
    """Mock Ollama client for testing."""

    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url
        self.model = model

    async def generate(self, prompt: str, system: Optional[str] = None) -> str:
        return "Mock Ollama response"
