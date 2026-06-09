"""Dagster Definitions — entry point for the warehouse project."""

from dagster import Definitions, load_assets_from_modules

from . import assets
from .sensors import result_file_sensor

all_assets = load_assets_from_modules([assets])

defs = Definitions(
    assets=all_assets,
    sensors=[result_file_sensor],
)
