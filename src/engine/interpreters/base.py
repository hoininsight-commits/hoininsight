from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseInterpreter(ABC):
    """
    Standard interface for all HoinInsight Interpreters.
    Interpreters take raw engine context and produce stylized artifacts.
    """
    
    @abstractmethod
    def run(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Run the interpretation logic.
        Returns a list of artifacts: [{'path': '...', 'payload': {...}}]
        """
        pass
