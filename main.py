from mcp.server.fastmcp import FastMCP

# Minimal MCP server instance
app = FastMCP("xaue-mcp")


def build_greeting(name: str) -> str:
    """Build a greeting message for direct Python calls."""
    return f"Hello, {name}! This is a minimal MCP callable method."


@app.tool()
def hello(name: str = "MCP") -> str:
    """Return a greeting to verify MCP tool invocation."""
    return build_greeting(name)


def run() -> None:
    """Start the MCP server (stdio transport by default)."""
    app.run()


if __name__ == "__main__":
    run()
