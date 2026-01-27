# server.py
import logging
import asyncio
import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp-server")

# Create a shared HTTP client for API requests
http_client = httpx.AsyncClient(timeout=10.0)

# Create an MCP server with a name
mcp = FastMCP("Calculator and Weather Tools", host="0.0.0.0", port=8000)


@mcp.tool()
async def calculate(expression: str) -> str:
    """
    Evaluates a mathematical expression and returns the result.

    Args:
        expression: Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5', etc.)

    Returns:
        A string containing the result of the calculation
    """
    logger.info(f"Calculating expression: {expression}")
    try:
        # Using eval with a restricted scope to prevent security issues
        # In a production environment, use a safer evaluation method
        result = eval(expression, {"__builtins__": {}}, {})
        logger.info(f"Result: {result}")
        return f"The result of {expression} is {result}"
    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        return f"Failed to calculate. Error: {str(e)}"


@mcp.tool()
async def get_weather(city: str) -> str:
    """
    Gets current weather temperature for a city.

    Args:
        city: City name to get weather for

    Returns:
        A string containing the current temperature for the city
    """
    logger.info(f"Getting weather for city: {city}")

    try:
        # Step 1: Get coordinates for the city
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_response = await http_client.get(geo_url)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data.get("results"):
            logger.warning(f"City not found: {city}")
            return f"City '{city}' not found."

        location = geo_data["results"][0]
        latitude = location["latitude"]
        longitude = location["longitude"]
        resolved_city_name = location.get("name", city)

        logger.info(
            f"Coordinates for {resolved_city_name}: Lat={latitude}, Lon={longitude}"
        )

        # Step 2: Get weather for the coordinates
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m"
        weather_response = await http_client.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        if (
            "current" not in weather_data
            or "temperature_2m" not in weather_data["current"]
        ):
            logger.error(
                f"Invalid weather data for {resolved_city_name}: {weather_data}"
            )
            return "Could not retrieve temperature from weather API."

        temperature = weather_data["current"]["temperature_2m"]
        logger.info(f"Temperature for {resolved_city_name}: {temperature}°C")
        return f"The current temperature in {resolved_city_name} is {temperature}°C"

    except httpx.HTTPStatusError as e:
        logger.error(
            f"HTTP error fetching weather for {city}: {e.response.status_code} - {e.response.text}"
        )
        return f"Error communicating with weather service: {e.response.status_code}"
    except Exception as e:
        logger.error(f"Unexpected error fetching weather for {city}: {str(e)}")
        return f"Internal server error: {str(e)}"


if __name__ == "__main__":
    try:
        logger.info("Starting MCP server on port 8000...")
        # Close the HTTP client when the server shuts down
        mcp.run(transport="sse")
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
        asyncio.run(http_client.aclose())
