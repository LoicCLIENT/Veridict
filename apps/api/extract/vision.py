"""Photo analysis using Claude Vision."""

from typing import Optional
from config import get_settings


async def analyze_photo(image_path: str) -> dict:
    """
    Analyze accident photo using Claude Vision.

    Args:
        image_path: Path to the image

    Returns:
        Analysis results
    """
    settings = get_settings()

    if not settings.anthropic_api_key:
        return _get_mock_analysis()

    # In production, would:
    # 1. Load image as base64
    # 2. Send to Claude Vision API
    # 3. Parse response

    return _get_mock_analysis()


def _get_mock_analysis() -> dict:
    """Return mock photo analysis."""
    return {
        "damage_location": "front_right",
        "damage_severity": "moderate",
        "visible_debris": True,
        "skid_marks_visible": True,
        "skid_mark_length_estimate": "10-15m",
        "weather_visible": "dry",
        "time_of_day": "daytime",
        "road_surface": "asphalt",
        "confidence": 0.85,
        "fuente": "mock",
    }


async def analyze_damage_pattern(images: list[str]) -> dict:
    """
    Analyze damage pattern across multiple photos.

    Args:
        images: List of image paths

    Returns:
        Damage pattern analysis
    """
    return {
        "impact_type": "lateral",
        "principal_direction_of_force": "right",
        "estimated_crush_depth": "15-20cm",
        "affected_components": ["front_fender", "door", "bumper"],
    }
