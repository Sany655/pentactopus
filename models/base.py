"""Abstract base class for LLM Agent model providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class BaseModelProvider(ABC):
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key

    @abstractmethod
    def predict_action(
        self,
        goal: str,
        screen_state_text: str,
        screenshot_bytes: Optional[bytes] = None,
        history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Given goal and current screen state, predict next structured action."""
        pass
