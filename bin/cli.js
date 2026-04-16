#!/usr/bin/env node

import { start } from "../src/server.js";

start().catch((err) => {
  console.error("Failed to start xaue-mcp-server:", err);
  process.exit(1);
});
