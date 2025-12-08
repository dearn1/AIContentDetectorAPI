# app/utils/detector.py
import re
from typing import Dict, List


class AIContentDetector:
    """
    AI Content Detection Engine
    Analyzes text for AI-generated characteristics
    """

    def __init__(self):
        # Common AI writing patterns
        self.ai_patterns = {
            'repetitive_phrases': [
                r'it is important to note',
                r'in conclusion',
                r'furthermore',
                r'moreover',
                r'it\'s worth noting',
                r'delve into',
                r'dive deep',
                r'in today\'s digital age',
                r'it goes without saying',
                r'needless to say',
                r'at the end of the day',
                r'in summary',
                r'to summarize',
                r'in essence',
                r'fundamentally'
            ],
            'perfect_grammar_ratio': 0.98,
            'sentence_uniformity': 0.85,
        }

    def analyze_text(self, text: str) -> Dict:
        """
        Analyze text for AI-generated characteristics

        Args:
            text: The text to analyze

        Returns:
            Dictionary containing analysis results
        """
        # Calculate various metrics
        ai_phrase_count = self._count_ai_phrases(text)
        sentence_uniformity = self._calculate_sentence_uniformity(text)
        repetition_score = self._calculate_repetition(text)

        # Calculate overall AI probability (0-100)
        ai_probability = self._calculate_probability(
            ai_phrase_count,
            sentence_uniformity,
            repetition_score
        )

        return {
            'ai_probability': round(ai_probability, 2),
            'is_likely_ai': ai_probability > 70,
            'confidence': self._get_confidence_level(ai_probability),
            'metrics': {
                'ai_phrases_detected': ai_phrase_count,
                'sentence_uniformity_score': round(sentence_uniformity, 2),
                'repetition_score': round(repetition_score, 2)
            }
        }

    def _count_ai_phrases(self, text: str) -> int:
        """Count common AI writing phrases"""
        count = 0
        text_lower = text.lower()
        for pattern in self.ai_patterns['repetitive_phrases']:
            count += len(re.findall(pattern, text_lower))
        return count

    def _calculate_sentence_uniformity(self, text: str) -> float:
        """
        Calculate how uniform sentence lengths are
        AI tends to produce more uniform sentences
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return 0

        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)

        # Calculate variance
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)

        # Lower variance = higher uniformity (more AI-like)
        uniformity = max(0, 100 - variance)
        return min(100, uniformity)

    def _calculate_repetition(self, text: str) -> float:
        """Calculate word repetition patterns"""
        words = text.lower().split()
        if len(words) < 10:
            return 0

        unique_words = len(set(words))
        total_words = len(words)

        # AI tends to have less vocabulary diversity
        diversity = (unique_words / total_words) * 100
        repetition = 100 - diversity

        return repetition

    def _calculate_probability(self, ai_phrases: int, uniformity: float, repetition: float) -> float:
        """Calculate overall AI probability"""
        # Weighted scoring
        phrase_score = min(ai_phrases * 15, 40)  # Max 40 points
        uniformity_score = uniformity * 0.3  # Max 30 points
        repetition_score = repetition * 0.3  # Max 30 points

        total = phrase_score + uniformity_score + repetition_score
        return min(100, total)

    def _get_confidence_level(self, probability: float) -> str:
        """Return confidence level based on probability"""
        if probability >= 80:
            return "Very High"
        elif probability >= 60:
            return "High"
        elif probability >= 40:
            return "Medium"
        else:
            return "Low"
