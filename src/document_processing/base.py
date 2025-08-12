from abc import ABC, abstractmethod
from typing import List, Any
import pathlib

class BaseProcessor(ABC):
    """
    Abstract base class for all document processors.
    """
    @abstractmethod
    def process(self, file_path: pathlib.Path) -> List[Any]:
        """
        Process a single file and return a list of processed chunks or objects.

        Args:
            file_path: The path to the file to be processed.

        Returns:
            A list of processed items. The type of items can vary depending on the processor.
        """
        pass
