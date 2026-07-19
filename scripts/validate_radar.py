#!/usr/bin/env python3
"""Validate radar data without rewriting generated pages."""

from render_radar import load_radar_data, paper_map, validate_data


if __name__ == "__main__":
    validate_data(load_radar_data(), paper_map())
    print("radar data validation passed")
