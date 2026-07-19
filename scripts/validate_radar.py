#!/usr/bin/env python3
"""Validate radar data without rewriting generated pages."""

from render_radar import EDITIONS_PATH, load_yaml, paper_map, validate_data


if __name__ == "__main__":
    validate_data(load_yaml(EDITIONS_PATH), paper_map())
    print("radar data validation passed")
