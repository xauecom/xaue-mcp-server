#!/usr/bin/env node

const { spawn, execFileSync } = require("child_process");

function findCommand(cmd) {
  try {
    execFileSync(process.platform === "win32" ? "where" : "which", [cmd], {
      stdio: "ignore",
    });
    return true;
  } catch {
    return false;
  }
}

const GITHUB_SRC = "git+https://github.com/xauecom/xaue-mcp-server";

function startServer() {
  if (findCommand("uvx")) {
    return spawn("uvx", ["--from", GITHUB_SRC, "xaue-mcp-server"], {
      stdio: "inherit",
      shell: process.platform === "win32",
    });
  }

  if (findCommand("pipx")) {
    return spawn("pipx", ["run", "--spec", GITHUB_SRC, "xaue-mcp-server"], {
      stdio: "inherit",
      shell: process.platform === "win32",
    });
  }

  console.error(
    "Error: Neither 'uvx' nor 'pipx' found.\n\n" +
      "Please install one of the following:\n" +
      "  • uv (recommended): https://docs.astral.sh/uv/getting-started/installation/\n" +
      "  • pipx: https://pipx.pypa.io/stable/installation/\n"
  );
  process.exit(1);
}

const child = startServer();

child.on("error", (err) => {
  console.error("Failed to start xaue-mcp-server:", err.message);
  process.exit(1);
});

child.on("exit", (code) => process.exit(code ?? 0));
