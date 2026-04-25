# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **Chart Generation Tool for Agent**: Added a new modular feature `chart_tool.py` that allows the LLM agent to generate and render time-series line charts for given KPIs.
- **Configurable Flag for Chart Tool**: Added `ENABLE_CHART_TOOL` in `app/config/settings.py` (default: `True` through `.env` fallback to `"true"`). This makes the module entirely plug-and-play and isolated from the main logic. If disabled, the tool is not loaded.
- **Dependency**: Added `matplotlib==3.8.4` to `requirements.txt` to support chart generation.

### Changed
- **Agent Initialization (`agent.py`)**: Modified `build_agent` to conditionally inject the `generate_time_series_chart` tool based on the `ENABLE_CHART_TOOL` setting.
- **System Prompt (`system_prompt.py`)**: Instructed the LLM to call the new chart tool when requested by the user and directly embed the Markdown response.

### Fixed
- **Chart Rendering**: Changed the chart generation output from Base64 to saving the PNG file into `app/static/charts/`. This prevents the LLM from corrupting or breaking the long Base64 string during response generation, ensuring the chart is correctly displayed in the frontend.
