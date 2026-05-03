"""
Veridict AI - Training Module
Herramientas para entrenar y mejorar agentes de visualizacion
"""

from .train_visualizations import VisualizationTrainer
from .iterate import iterate_with_feedback

__all__ = ["VisualizationTrainer", "iterate_with_feedback"]
