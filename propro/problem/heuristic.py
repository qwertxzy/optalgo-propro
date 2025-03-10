from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class AbstractHeuristic(ABC):
    '''
    Represents the score of a solution.
    '''

    @abstractmethod
    def is_valid(self) -> bool:
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def __lt__(self, other: 'AbstractHeuristic'):
        pass

    @abstractmethod
    def __eq__(self, other: 'AbstractHeuristic'):
        pass

    @abstractmethod
    def __le__(self, other: 'AbstractHeuristic'):
        pass


  
