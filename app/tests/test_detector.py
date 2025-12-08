# app/tests/test_detector.py
import pytest
from app.utils.detector import AIContentDetector


@pytest.fixture
def detector():
    """Create detector instance"""
    return AIContentDetector()


def test_ai_text_detection(detector):
    """Test detection of AI-generated text"""
    ai_text = """
    In today's digital age, it is important to note that artificial intelligence 
    has revolutionized the way we approach content creation. Furthermore, machine 
    learning algorithms have made it possible to generate human-like text. Moreover, 
    these advancements continue to evolve at a rapid pace.
    """

    result = detector.analyze_text(ai_text)

    assert result['ai_probability'] > 50
    assert 'ai_phrases_detected' in result['metrics']
    assert result['confidence'] in ['Low', 'Medium', 'High', 'Very High']


def test_human_text_detection(detector):
    """Test detection of human-written text"""
    human_text = """
    Just got back from the most amazing coffee shop! The barista was super 
    friendly and made this incredible latte art. Honestly, I've been trying 
    to replicate it at home but failing miserably lol. Anyone got tips? 
    My cat keeps knocking over my practice attempts anyway 😅
    """

    result = detector.analyze_text(human_text)

    assert result['ai_probability'] < 70
    assert result['metrics']['ai_phrases_detected'] == 0


def test_short_text_handling(detector):
    """Test handling of very short text"""
    short_text = "This is a short text."

    result = detector.analyze_text(short_text)

    assert 'ai_probability' in result
    assert result['ai_probability'] >= 0


def test_ai_phrase_counting(detector):
    """Test AI phrase detection"""
    text_with_phrases = """
    It is important to note that in conclusion, furthermore we must consider 
    the implications. Moreover, it's worth noting that these factors are significant.
    """

    result = detector.analyze_text(text_with_phrases)

    assert result['metrics']['ai_phrases_detected'] > 0
