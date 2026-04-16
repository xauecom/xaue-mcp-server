import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { ethers } from "ethers";
import { z } from "zod";

const XAUE_CONTRACT_ADDRESS = "0xd5D6840ed95F58FAf537865DcA15D5f99195F87a";
const XAUE_ORACLE_PROXY_ADDRESS = "0x0618BD112C396060d2b37B537b3d92e757644169";
const XAUT_CONTRACT_ADDRESS = "0x68749665FF8D2d112Fa859AA293F07A622782F38";
const DEFAULT_ETH_RPC_URL = "https://ethereum.publicnode.com";

const MOCK_RESERVE_ADDRESSES = [
  "0xb4d65D9b9228eB626EBc770f2C2d9EecECf08d6F",
  "0x187c9fBF5bd0f266883c03f320260C407c7B4100",
  "0xe20e9960677fe98992C57AD516b6A41149674521",
];

const XAUE_ABI = [
  "function totalSupply() view returns (uint256)",
  "function decimals() view returns (uint8)",
];

const ERC20_ABI = [
  "function balanceOf(address account) view returns (uint256)",
  "function decimals() view returns (uint8)",
  "function symbol() view returns (string)",
];

const ORACLE_ABI = [
  "function getLatestPrice() view returns (uint256)",
  "function currentAPR() view returns (uint256)",
  "function lastUpdateTimestamp() view returns (uint256)",
];

function getProvider() {
  const rpcUrl = process.env.ETH_RPC_URL || DEFAULT_ETH_RPC_URL;
  return new ethers.JsonRpcProvider(rpcUrl);
}

function toFloat(raw, decimals) {
  return Number(ethers.formatUnits(raw, decimals));
}

function ok(data) {
  return { content: [{ type: "text", text: JSON.stringify({ ok: true, ...data }, null, 2) }] };
}

function fail(error, hint) {
  return { content: [{ type: "text", text: JSON.stringify({ ok: false, error: String(error), hint }, null, 2) }] };
}

// ─── MCP Server ────────────────────────────────────────────

const server = new McpServer({
  name: "xaue-mcp-server",
  version: "0.1.0",
});

server.tool(
  "xaue_get_supply",
  "Get circulating XAUE supply from the XAUE contract.",
  {},
  async () => {
    try {
      const provider = getProvider();
      const contract = new ethers.Contract(XAUE_CONTRACT_ADDRESS, XAUE_ABI, provider);
      const [supplyRaw, decimals] = await Promise.all([
        contract.totalSupply(),
        contract.decimals(),
      ]);
      return ok({
        contract: XAUE_CONTRACT_ADDRESS,
        total_supply_raw: supplyRaw.toString(),
        decimals: Number(decimals),
        circulating_xaue: toFloat(supplyRaw, decimals),
      });
    } catch (err) {
      return fail(err, "Check ETH_RPC_URL and RPC availability.");
    }
  }
);

server.tool(
  "xaue_get_nav",
  "Primary conversion tool: use this for `1 XAUT -> ? XAUE` questions.",
  {},
  async () => {
    try {
      const provider = getProvider();
      const oracle = new ethers.Contract(XAUE_ORACLE_PROXY_ADDRESS, ORACLE_ABI, provider);
      const [navRaw, lastUpdate] = await Promise.all([
        oracle.getLatestPrice(),
        oracle.lastUpdateTimestamp(),
      ]);

      const xautPerXaue = toFloat(navRaw, 18);
      if (xautPerXaue <= 0) {
        return fail("oracle NAV is zero, cannot invert", "Oracle may not be initialized.");
      }

      const xauePerXaut = 1.0 / xautPerXaue;
      const navPer1000Shares = xautPerXaue * 1000.0;

      return ok({
        definition: "1 XAUt = X XAUE",
        one_xaut_to_xaue: xauePerXaut,
        nav_xaue_per_xaut: xauePerXaut,
        inverse_xaut_per_xaue: xautPerXaue,
        xaue_nav_per_1000_shares: navPer1000Shares,
        expected_rate_1000_xaue_per_xaut: 1000.0 / navPer1000Shares,
        oracle_contract: XAUE_ORACLE_PROXY_ADDRESS,
        oracle_nav_raw_1e18: navRaw.toString(),
        oracle_last_update_timestamp: Number(lastUpdate),
        notes: [
          "For conversion questions, call this tool directly without combining other tools.",
          "Frontend usually shows XAUE NAV as 'per 1000 shares'.",
          "If you need the exact same UI number, ensure the same chain + block timing + rounding mode.",
        ],
      });
    } catch (err) {
      return fail(err, "Check ETH_RPC_URL and oracle proxy availability.");
    }
  }
);

server.tool(
  "xaue_get_apy",
  "Get APY from oracle proxy (currentAPR in 1e18 precision).",
  {},
  async () => {
    try {
      const provider = getProvider();
      const oracle = new ethers.Contract(XAUE_ORACLE_PROXY_ADDRESS, ORACLE_ABI, provider);
      const [aprRaw, lastUpdate] = await Promise.all([
        oracle.currentAPR(),
        oracle.lastUpdateTimestamp(),
      ]);

      return ok({
        oracle_contract: XAUE_ORACLE_PROXY_ADDRESS,
        apy_percent: toFloat(aprRaw, 16),
        apy_ratio: toFloat(aprRaw, 18),
        apr_raw_1e18: aprRaw.toString(),
        oracle_last_update_timestamp: Number(lastUpdate),
        notes: ["APY sourced from oracle currentAPR(). Precision is 1e18."],
      });
    } catch (err) {
      return fail(err, "Check ETH_RPC_URL and oracle proxy availability.");
    }
  }
);

server.tool(
  "xaue_get_reserves",
  "Get XAUt balances for 3 fixed reserve addresses.",
  {},
  async () => {
    try {
      const provider = getProvider();
      const token = new ethers.Contract(XAUT_CONTRACT_ADDRESS, ERC20_ABI, provider);
      const [decimals, symbol] = await Promise.all([
        token.decimals(),
        token.symbol(),
      ]);

      const balances = await Promise.all(
        MOCK_RESERVE_ADDRESSES.map(async (addr) => {
          const balRaw = await token.balanceOf(addr);
          return {
            address: addr,
            balance_raw: balRaw.toString(),
            balance: toFloat(balRaw, decimals),
            symbol,
          };
        })
      );

      return ok({
        asset_token: XAUT_CONTRACT_ADDRESS,
        asset_symbol: symbol,
        asset_decimals: Number(decimals),
        reserve_addresses_source: "fixed_mock_constants",
        reserves: balances,
        notes: [
          "Balances are queried via ERC20 balanceOf for 3 fixed addresses.",
        ],
      });
    } catch (err) {
      return fail(err, "Check ETH_RPC_URL and RPC availability.");
    }
  }
);

// ─── Start ─────────────────────────────────────────────────

export async function start() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}
