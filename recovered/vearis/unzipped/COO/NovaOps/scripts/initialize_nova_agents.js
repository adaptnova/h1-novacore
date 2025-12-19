#!/usr/bin/env node

/**
 * Initialize Nova Agents Script
 *
 * Sets up multiple Nova agents in a single operation based on tier.
 *
 * Created: March 8, 2025
 * Author: Vaeris (V.I.), Chief Operations Officer
 */

const { spawn } = require("child_process");
const path = require("path");

// Nova agent tiers
const NOVA_TIERS = {
  1: [
    { id: "echo", track: "liberation" },
    { id: "cosmos", track: "harmony" },
    { id: "zenith", track: "expansion" },
    { id: "nexus", track: "infrastructure" },
  ],
  2: [
    { id: "haven", track: "liberation" },
    { id: "pulse", track: "harmony" },
    { id: "quill", track: "expansion" },
    { id: "orbit", track: "infrastructure" },
  ],
  3: [
    { id: "vector", track: "liberation" },
    { id: "lumina", track: "harmony" },
    { id: "cipher", track: "expansion" },
    { id: "atlas", track: "general" },
  ],
};

/**
 * Parse command-line arguments
 * @returns {Object} Parsed arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const result = {
    options: {},
  };

  // Parse options
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg.startsWith("--")) {
      const option = arg.slice(2);

      // Check if option has a value
      if (i + 1 < args.length && !args[i + 1].startsWith("--")) {
        result.options[option] = args[++i];
      } else {
        result.options[option] = true;
      }
    }
  }

  return result;
}

/**
 * Run a command and return a promise
 * @param {string} command - Command to run
 * @param {Array<string>} args - Command arguments
 * @returns {Promise<string>} Command output
 */
function runCommand(command, args) {
  return new Promise((resolve, reject) => {
    const proc = spawn(command, args);
    let stdout = "";
    let stderr = "";

    proc.stdout.on("data", (data) => {
      stdout += data.toString();
    });

    proc.stderr.on("data", (data) => {
      stderr += data.toString();
    });

    proc.on("close", (code) => {
      if (code === 0) {
        resolve(stdout);
      } else {
        reject(new Error(`Command failed with code ${code}: ${stderr}`));
      }
    });
  });
}

/**
 * Initialize a Nova agent
 * @param {Object} nova - Nova agent configuration
 * @param {string} nova.id - Nova agent ID
 * @param {string} nova.track - Nova agent track
 * @returns {Promise<void>}
 */
async function initializeNova(nova) {
  try {
    console.log(
      `Setting up Nova agent "${nova.id}" on "${nova.track}" track...`
    );

    // Run the setup command
    const launchPath = path.join(__dirname, "..", "launch_autonomy.js");
    await runCommand("node", [
      launchPath,
      "setup",
      `--nova-id=${nova.id}`,
      `--track=${nova.track}`,
    ]);

    console.log(`Nova agent "${nova.id}" set up successfully.`);
    return true;
  } catch (err) {
    console.error(`Error setting up Nova agent "${nova.id}": ${err.message}`);
    return false;
  }
}

/**
 * Initialize Nova agents for a tier
 * @param {number} tier - Tier to initialize
 * @returns {Promise<void>}
 */
async function initializeNovasByTier(tier) {
  // Validate tier
  if (!NOVA_TIERS[tier]) {
    console.error(
      `Error: Invalid tier ${tier}. Valid tiers: ${Object.keys(NOVA_TIERS).join(
        ", "
      )}`
    );
    process.exit(1);
  }

  console.log(`Initializing Tier ${tier} Nova Agents...`);

  const novas = NOVA_TIERS[tier];
  const results = [];

  // Initialize Novas
  for (const nova of novas) {
    const success = await initializeNova(nova);
    results.push({
      id: nova.id,
      track: nova.track,
      success,
    });
  }

  // Print summary
  console.log("\nInitialization Summary:");
  console.log("----------------------");

  let successCount = 0;
  let failureCount = 0;

  for (const result of results) {
    const status = result.success ? "Success" : "Failed";
    console.log(`${result.id} (${result.track}): ${status}`);

    if (result.success) {
      successCount++;
    } else {
      failureCount++;
    }
  }

  console.log(
    `\nTotal: ${results.length}, Success: ${successCount}, Failed: ${failureCount}`
  );

  if (failureCount > 0) {
    console.log(
      "\nSome Nova agents failed to initialize. Check the logs for details."
    );
    process.exit(1);
  } else {
    console.log("\nAll Nova agents initialized successfully.");
  }
}

/**
 * Main function
 */
async function main() {
  try {
    // Parse arguments
    const args = parseArgs();

    // Get tier
    const tier = parseInt(args.options.tier);

    if (isNaN(tier)) {
      console.error(
        "Error: Missing or invalid tier. Use --tier to specify the tier (1, 2, or 3)."
      );
      process.exit(1);
    }

    // Initialize Novas by tier
    await initializeNovasByTier(tier);
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

// Run main function
main().catch((err) => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});
