# xaue-mcp

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![MCP](https://img.shields.io/badge/protocol-MCP-green)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

XAUE on-chain query MCP server — 让 AI 助手直接读取以太坊上的 XAUE 实时数据（供应量、NAV、APY、储备金）。

## Quick Start

> 前提条件：安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)（Python 包管理器）

**无需 clone，一行命令即可运行：**

```bash
uvx --from git+https://github.com/AntalphaDevs/xaue-mcp xaue-mcp
```

## 在 AI 客户端中使用

### Cursor

编辑 `~/.cursor/mcp.json`：

```json
{
  "mcpServers": {
    "xaue-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/AntalphaDevs/xaue-mcp", "xaue-mcp"]
    }
  }
}
```

### Claude Desktop

编辑配置文件（macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "xaue-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/AntalphaDevs/xaue-mcp", "xaue-mcp"]
    }
  }
}
```

### 自定义 RPC 节点（可选）

默认使用公共节点，如需指定私有 RPC，添加 `env` 字段：

```json
{
  "mcpServers": {
    "xaue-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/AntalphaDevs/xaue-mcp", "xaue-mcp"],
      "env": {
        "ETH_RPC_URL": "https://your-rpc-endpoint.com"
      }
    }
  }
}
```

## 提供的工具

配置完成后，AI 助手可以自动调用以下工具：

| 工具 | 说明 |
|------|------|
| `xaue_get_supply` | 查询 XAUE 流通供应量（totalSupply + decimals） |
| `xaue_get_nav` | 查询 NAV 净值，获取 XAUt ↔ XAUE 换算率 |
| `xaue_get_apy` | 查询当前年化收益率（来自 Oracle） |
| `xaue_get_reserves` | 查询储备地址的 XAUt 余额 |
| `xaue_get_backing` | （开发中）查询 XAUt 总储备支撑 |

### 使用示例

在 Cursor 或 Claude Desktop 中直接向 AI 提问：

- "XAUE 当前的流通量是多少？"
- "1 XAUt 可以兑换多少 XAUE？"
- "XAUE 现在的年化收益率是多少？"
- "查一下储备地址的 XAUt 余额"

AI 会自动调用对应的 MCP 工具并返回实时链上数据。

## 合约地址

| 合约 | 地址 | 网络 |
|------|------|------|
| XAUE | [`0xd5D6840ed95F58FAf537865DcA15D5f99195F87a`](https://etherscan.io/address/0xd5D6840ed95F58FAf537865DcA15D5f99195F87a) | Ethereum |
| Oracle Proxy | [`0x0618BD112C396060d2b37B537b3d92e757644169`](https://etherscan.io/address/0x0618BD112C396060d2b37B537b3d92e757644169) | Ethereum |
| XAUt | [`0x68749665FF8D2d112Fa859AA293F07A622782F38`](https://etherscan.io/address/0x68749665FF8D2d112Fa859AA293F07A622782F38) | Ethereum |

## 技术说明

- XAUE 合约为 EIP-1967 代理合约
- NAV 和 APY 数据从 Oracle Proxy 合约读取
- 储备查询当前使用 3 个固定的 mock 地址，通过 ERC-20 `balanceOf` 查询 XAUt 余额
- 服务器使用 stdio 传输协议，与 MCP 客户端通信

## License

MIT
