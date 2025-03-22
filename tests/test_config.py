"""Tests for the configuration module."""

import os
import tempfile
from pathlib import Path

import pytest

from src.hydrograph_seatek_analysis.core.config import Config, NavdConstants, ChartSettings


def test_config_default_initialization():
    """Test that Config can be initialized with default values."""
    config = Config()
    
    assert config.base_dir is not None
    assert config.data_dir == config.base_dir / "data"
    assert config.raw_data_dir == config.data_dir / "raw"
    assert config.processed_dir == config.data_dir / "processed"
    assert config.output_dir == config.base_dir / "output/charts"


def test_config_custom_base_dir():
    """Test that Config can be initialized with a custom base directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = Config(base_dir=temp_path)
        
        assert config.base_dir == temp_path
        assert config.data_dir == temp_path / "data"
        assert config.raw_data_dir == temp_path / "data/raw"
        assert config.processed_dir == temp_path / "data/processed"
        assert config.output_dir == temp_path / "output/charts"


def test_navd_constants():
    """Test that NavdConstants can be initialized with default and custom values."""
    # Default values
    constants = NavdConstants()
    assert constants.offset_a == 1.9
    assert constants.offset_b == 0.32
    assert constants.scale_factor == 400 / 30.48
    
    # Custom values
    custom_constants = NavdConstants(offset_a=2.0, offset_b=0.4, scale_factor=15.0)
    assert custom_constants.offset_a == 2.0
    assert custom_constants.offset_b == 0.4
    assert custom_constants.scale_factor == 15.0


def test_chart_settings():
    """Test that ChartSettings can be initialized with default and custom values."""
    # Default values
    settings = ChartSettings()
    assert settings.dpi == 300
    assert settings.figure_size == (12, 8)
    assert settings.font_family == 'Arial'
    assert settings.font_size == 11
    
    # Custom values
    custom_settings = ChartSettings(dpi=200, figure_size=(10, 6), font_family='Times', font_size=12)
    assert custom_settings.dpi == 200
    assert custom_settings.figure_size == (10, 6)
    assert custom_settings.font_family == 'Times'
    assert custom_settings.font_size == 12


def test_config_from_dict():
    """Test that Config can be created from a dictionary."""
    config_dict = {
        'base_dir': '/tmp/test',
        'navd88_constants': {
            'offset_a': 2.0,
            'offset_b': 0.4,
            'scale_factor': 15.0
        },
        'chart_settings': {
            'dpi': 200,
            'figure_size': (10, 6),
            'font_family': 'Times',
            'font_size': 12
        }
    }
    
    config = Config.from_dict(config_dict)
    
    assert config.base_dir == Path('/tmp/test')
    assert config.navd88_constants.offset_a == 2.0
    assert config.navd88_constants.offset_b == 0.4
    assert config.navd88_constants.scale_factor == 15.0
    assert config.chart_settings.dpi == 200
    assert config.chart_settings.figure_size == (10, 6)
    assert config.chart_settings.font_family == 'Times'
    assert config.chart_settings.font_size == 12