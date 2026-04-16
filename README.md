# xaue-mcp-server

[![Node.js 18+](https://img.shields.io/badge/node-18%2B-blue)](https://nodejs.org)
[![MCP](https://img.shields.io/badge/protocol-MCP-green)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

A Model Context Protocol (MCP) server for querying XAUE on-chain data — enabling AI assistants to read real-time XAUE metrics (supply, NAV, APY, reserves) directly from Ethereum.

## Quick Start

Add the following to your AI client's MCP config file:

```json
{
  "mcpServers": {
    "xaue-mcp-server": {
      "command": "npx",
      "args": ["-y", "github:xauecom/xaue-mcp-server"]
    }
  }
}
```

### Config File Locations

| Client | Config File Path |
|--------|-----------------|
| Cursor | `~/.cursor/mcp.json` |
| Claude Desktop (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |

### Custom RPC Endpoint (Optional)

A public RPC node is used by default. To specify a private RPC, add the `env` field:

```json
{
  "mcpServers": {
    "xaue-mcp-server": {
      "command": "npx",
      "args": ["-y", "github:xauecom/xaue-mcp-server"],
      "env": {
        "ETH_RPC_URL": "https://your-rpc-endpoint.com"
      }
    }
  }
}
```

## Available Tools

Once configured, the AI assistant can automatically invoke the following tools:

| Tool | Description |
|------|-------------|
| `xaue_get_supply` | Query XAUE circulating supply (totalSupply + decimals) |
| `xaue_get_nav` | Query NAV (Net Asset Value) and get XAUt ↔ XAUE conversion rate |
| `xaue_get_apy` | Query the current annual percentage yield (from Oracle) |
| `xaue_get_reserves` | Query XAUt balances of the reserve and vault addresses |

### Example Prompts

Ask the AI directly in Cursor or Claude Desktop:

- "What is the current circulating supply of XAUE?"
- "How many XAUE can 1 XAUt be exchanged for?"
- "What is the current APY for XAUE?"
- "Check the XAUt balance of the reserve addresses"

The AI will automatically call the corresponding MCP tools and return real-time on-chain data.

## Contract Addresses

| Contract | Address | Network |
|----------|---------|---------|
| XAUE | [`0xd5D6840ed95F58FAf537865DcA15D5f99195F87a`](https://etherscan.io/address/0xd5D6840ed95F58FAf537865DcA15D5f99195F87a) | Ethereum |
| Oracle Proxy | [`0x0618BD112C396060d2b37B537b3d92e757644169`](https://etherscan.io/address/0x0618BD112C396060d2b37B537b3d92e757644169) | Ethereum |
| XAUt | [`0x68749665FF8D2d112Fa859AA293F07A622782F38`](https://etherscan.io/address/0x68749665FF8D2d112Fa859AA293F07A622782F38) | Ethereum |
| Reserve | [`0x07cd80c066e13679a70e125c76f76e796c8bc748`](https://etherscan.io/address/0x07cd80c066e13679a70e125c76f76e796c8bc748) | Ethereum |
| Vault | [`0xC86Daf84C01c891B21dEA66f4cA41CD3799f9E6B`](https://etherscan.io/address/0xC86Daf84C01c891B21dEA66f4cA41CD3799f9E6B) | Ethereum |

## Technical Notes

- The XAUE contract is an EIP-1967 proxy contract
- NAV and APY data are read from the Oracle Proxy contract
- Reserve queries use the reserve address (`0x07cd...748`) and vault address (`0xC86D...E6B`), querying XAUt balances via ERC-20 `balanceOf`
- The server uses the stdio transport protocol to communicate with MCP clients

## License

MIT
