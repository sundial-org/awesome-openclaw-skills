"""
Signal generation components

Handles trading signal generation and recommendations
"""

from .generator import SignalGenerator
from .recommender import RecommendationEngine

__all__ = ['SignalGenerator', 'RecommendationEngine']
