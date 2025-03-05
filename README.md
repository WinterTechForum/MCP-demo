# MCP Client

A client implementation for MCP with Anthropic integration.

## Requirements

- Python 3.13 or higher
- pip or uv package manager

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd mcp-client
   ```

2. Create and activate a virtual environment:
   ```bash
   uv venv  # Recommended
   source .venv/bin/activate  # On Unix-like systems
   # Or on Windows:
   # .venv\Scripts\activate

   # Alternatively with Python's venv module:
   # python -m venv .venv
   # source .venv/bin/activate  # On Unix-like systems
   # .venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   uv sync  # Recommended
   # Or alternatively with pip:
   # pip install .
   ```

4. Configure environment variables:
   - Create a `.env` file in the project root with the following content:
     ```
     ANTHROPIC_API_KEY=your_api_key_here
     ```
   - Replace `your_api_key_here` with your actual Anthropic API key

5. Running:
   `python client.py weather/weather.py`

   If you have a separate tools server, replace `weather/weather.py` with the location of your server

## Dependencies

- anthropic (>=0.49.0): Anthropic API client
- httpx (>=0.28.1): HTTP client
- mcp[cli] (>=1.3.0): MCP CLI tools
- python-dotenv (>=1.0.1): Environment variable management

## Environment Variables

The following environment variables are required:

- `ANTHROPIC_API_KEY`: Your Anthropic API key for authentication

## Note

Make sure to keep your `.env` file secure and never commit it to version control. The repository includes a `.gitignore` file that should already exclude the `.env` file.
