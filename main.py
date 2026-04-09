import os
from typing import Any

from mcp.server.fastmcp import FastMCP
from web3 import Web3

app = FastMCP("xaue-mcp")


XAUE_CONTRACT_ADDRESS = "0xd5D6840ed95F58FAf537865DcA15D5f99195F87a"
XAUE_ORACLE_PROXY_ADDRESS = "0x0618BD112C396060d2b37B537b3d92e757644169"
DEFAULT_ETH_RPC_URL = "https://ethereum.publicnode.com"

XAUE_ABI = [
    {
        "inputs": [],
        "name": "asset",
        "outputs": [{"internalType": "contract IERC20", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "vault",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "MANAGER_ROLE",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "role", "type": "bytes32"}],
        "name": "getRoleMembers",
        "outputs": [{"internalType": "address[]", "name": "", "type": "address[]"}],
        "stateMutability": "view",
        "type": "function",
    },
]

ERC20_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "symbol",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
]

ORACLE_ABI = [
    {
        "inputs": [],
        "name": "getLatestPrice",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "currentAPR",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "lastUpdateTimestamp",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]


def _w3() -> Web3:
    rpc_url = os.getenv("ETH_RPC_URL", DEFAULT_ETH_RPC_URL)
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise RuntimeError(f"Cannot connect to Ethereum RPC: {rpc_url}")
    return w3


def _to_checksum(w3: Web3, address: str) -> str:
    return w3.to_checksum_address(address)


def _to_float(raw: int, decimals: int) -> float:
    return raw / (10 ** decimals)


def _xaue_contract(w3: Web3):
    return w3.eth.contract(address=_to_checksum(w3, XAUE_CONTRACT_ADDRESS), abi=XAUE_ABI)


def _erc20_contract(w3: Web3, token_address: str):
    return w3.eth.contract(address=_to_checksum(w3, token_address), abi=ERC20_ABI)


def _oracle_contract(w3: Web3):
    return w3.eth.contract(address=_to_checksum(w3, XAUE_ORACLE_PROXY_ADDRESS), abi=ORACLE_ABI)


def _discover_reserve_addresses(contract, vault_address: str) -> list[str]:
    addresses: list[str] = []
    if vault_address and int(vault_address, 16) != 0:
        addresses.append(vault_address)

    try:
        manager_role = contract.functions.MANAGER_ROLE().call()
        role_members = contract.functions.getRoleMembers(manager_role).call()
        addresses.extend(role_members)
    except Exception:
        pass

    unique: list[str] = []
    for addr in addresses:
        if addr not in unique:
            unique.append(addr)
    return unique


@app.tool()
def xaue_get_supply() -> dict[str, Any]:
    """Get circulating XAUE supply from the XAUE contract."""
    try:
        w3 = _w3()
        contract = _xaue_contract(w3)
        supply_raw = contract.functions.totalSupply().call()
        xaue_decimals = contract.functions.decimals().call()
        return {
            "ok": True,
            "contract": XAUE_CONTRACT_ADDRESS,
            "total_supply_raw": str(supply_raw),
            "decimals": xaue_decimals,
            "circulating_xaue": _to_float(supply_raw, xaue_decimals),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "hint": "Check ETH_RPC_URL and RPC availability."}


@app.tool()
def xaue_get_reserves(reserve_addresses: list[str] | None = None) -> dict[str, Any]:
    """Get per-address XAUt reserve balances (best effort)."""
    try:
        w3 = _w3()
        xaue = _xaue_contract(w3)
        asset_address = xaue.functions.asset().call()
        vault_address = xaue.functions.vault().call()

        token = _erc20_contract(w3, asset_address)
        token_decimals = token.functions.decimals().call()
        token_symbol = token.functions.symbol().call()

        addresses = reserve_addresses or _discover_reserve_addresses(xaue, vault_address)

        balances = []
        for addr in addresses:
            checksum_addr = _to_checksum(w3, addr)
            bal_raw = token.functions.balanceOf(checksum_addr).call()
            balances.append(
                {
                    "address": checksum_addr,
                    "balance_raw": str(bal_raw),
                    "balance": _to_float(bal_raw, token_decimals),
                    "symbol": token_symbol,
                }
            )

        return {
            "ok": True,
            "asset_token": _to_checksum(w3, asset_address),
            "asset_symbol": token_symbol,
            "asset_decimals": token_decimals,
            "vault_address": _to_checksum(w3, vault_address),
            "reserves": balances,
            "notes": [
                "If reserve_addresses is omitted, this call uses vault + MANAGER_ROLE members as best-effort reserve set."
            ],
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "hint": "You can pass reserve_addresses explicitly to reduce discovery failures.",
        }


@app.tool()
def xaue_get_backing(reserve_addresses: list[str] | None = None) -> dict[str, Any]:
    """Get total XAUt backing across reserve addresses (best effort)."""
    reserves_data = xaue_get_reserves(reserve_addresses=reserve_addresses)
    if not reserves_data.get("ok", False):
        return {
            "ok": False,
            "error": reserves_data.get("error", "unknown error"),
            "todo": "Provide reserve_addresses explicitly and retry.",
        }

    total_raw = sum(int(item["balance_raw"]) for item in reserves_data["reserves"])
    decimals = reserves_data["asset_decimals"]
    return {
        "ok": True,
        "asset_token": reserves_data["asset_token"],
        "asset_symbol": reserves_data["asset_symbol"],
        "asset_decimals": decimals,
        "total_backing_raw": str(total_raw),
        "total_backing": _to_float(total_raw, decimals),
        "reserves_count": len(reserves_data["reserves"]),
        "notes": reserves_data["notes"],
    }


@app.tool()
def xaue_get_nav() -> dict[str, Any]:
    """Primary conversion tool: use this for `1 XAUT -> ? XAUE` questions."""
    try:
        w3 = _w3()
        oracle = _oracle_contract(w3)
        nav_raw = oracle.functions.getLatestPrice().call()
        last_update_timestamp = oracle.functions.lastUpdateTimestamp().call()

        xaut_per_xaue = _to_float(nav_raw, 18)
        if xaut_per_xaue <= 0:
            return {
                "ok": False,
                "error": "oracle NAV is zero, cannot invert",
                "oracle_nav_raw": str(nav_raw),
            }

        xaue_per_xaut = 1.0 / xaut_per_xaue
        nav_per_1000_shares = xaut_per_xaue * 1000.0
        rate_1000_xaue_per_xaut = 1000.0 / nav_per_1000_shares

        return {
            "ok": True,
            "definition": "1 XAUt = X XAUE",
            "one_xaut_to_xaue": xaue_per_xaut,
            "nav_xaue_per_xaut": xaue_per_xaut,
            "inverse_xaut_per_xaue": xaut_per_xaue,
            "xaue_nav_per_1000_shares": nav_per_1000_shares,
            "expected_rate_1000_xaue_per_xaut": rate_1000_xaue_per_xaut,
            "oracle_contract": XAUE_ORACLE_PROXY_ADDRESS,
            "oracle_nav_raw_1e18": str(nav_raw),
            "oracle_last_update_timestamp": last_update_timestamp,
            "notes": [
                "For conversion questions, call this tool directly without combining other tools.",
                "Frontend usually shows XAUE NAV as 'per 1000 shares'.",
                "If you need the exact same UI number, ensure the same chain + block timing + rounding mode.",
            ],
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "hint": "Check ETH_RPC_URL and oracle proxy availability.",
        }


@app.tool()
def xaue_get_apy() -> dict[str, Any]:
    """Get APY from oracle proxy (currentAPR in 1e18 precision)."""
    try:
        w3 = _w3()
        oracle = _oracle_contract(w3)
        apr_raw = oracle.functions.currentAPR().call()
        last_update_timestamp = oracle.functions.lastUpdateTimestamp().call()

        apy_percent = _to_float(apr_raw, 16)
        apy_ratio = _to_float(apr_raw, 18)
        return {
            "ok": True,
            "oracle_contract": XAUE_ORACLE_PROXY_ADDRESS,
            "apy_percent": apy_percent,
            "apy_ratio": apy_ratio,
            "apr_raw_1e18": str(apr_raw),
            "oracle_last_update_timestamp": last_update_timestamp,
            "notes": ["APY sourced from oracle currentAPR(). Precision is 1e18."],
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "hint": "Check ETH_RPC_URL and oracle proxy availability.",
        }


def run() -> None:
    """Start the MCP server (stdio transport by default)."""
    app.run()


if __name__ == "__main__":
    run()
