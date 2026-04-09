# xaue-mcp

A Python MCP server for XAUE on-chain query tools.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run Server

```bash
python main.py
```

or:

```bash
xaue-mcp
```

## RPC Configuration

Set Ethereum RPC (optional). Default is `https://ethereum.publicnode.com`.

```bash
export ETH_RPC_URL="https://ethereum.publicnode.com"
```

## MCP Tools

- `xaue_get_nav()`
- `xaue_get_apy()`
- `xaue_get_supply()`
- `xaue_get_backing(reserve_addresses: list[str] | None = None)`
- `xaue_get_reserves(reserve_addresses: list[str] | None = None)`

## Notes

- Contract address: `0xd5D6840ed95F58FAf537865DcA15D5f99195F87a`
- Oracle proxy (NAV/APY): `0x0618BD112C396060d2b37B537b3d92e757644169`
- The contract is an EIP-1967 proxy.
- `xaue_get_nav` and `xaue_get_apy` are read from the oracle proxy.
- `xaue_get_reserves` currently uses 3 fixed mock reserve addresses and queries XAUt via `balanceOf`.
