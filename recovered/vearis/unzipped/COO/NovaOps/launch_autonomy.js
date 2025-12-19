#!/usr/bin/env node
/**
 * Launch Autonomy Script
 *
 * CLI tool for managing Nova agent autonomy and task execution.
 *
 * Created: March 8, 2025
 * Author: Vaeris (V.I.), Chief Operations Officer
 */

const fs = require("fs").promises;
const path = require("path");
const TaskManager = require("./lib/task_manager");
const NovaAgent = require("./lib/nova_agent");

// Banner text
const BANNER = `
╔═══════════════════════════════════════════════════╗
║                                                   ║
║  ███╗   ██╗ ██████╗ ██╗   ██╗ █████╗  ██████╗ ██████╗ ███████╗
║  ████╗  ██║██╔═══██╗██║   ██║██╔══██╗██╔═══██╗██╔══██╗██╔════╝
║  ██╔██╗ ██║██║   ██║██║   ██║███████║██║   ██║██████╔╝███████╗
║  ██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║██║   ██║██╔═══╝ ╚════██║
║  ██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║╚██████╔╝██║     ███████║
║  ╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚══════╝
║                                                   ║
║  Launch Autonomy System v1.0.0                    ║
║  Vaeris Intelligence (V.I.), Chief Operations Officer    ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
`;

// Help text
const HELP_TEXT = `
Usage: node launch_autonomy.js <command> [options]

Commands:
  start               Start a Nova agent
  stop                Stop a Nova agent
  list-agents         List all Nova agents
  create-agent        Create a new Nova agent
  create-task         Create a new task
  list-tasks          List tasks
  assign-task         Assign a task to a Nova agent
  complete-task       Mark a task as completed
  get-next-task       Get the next task for a Nova agent
  task-stats          Get task statistics
  help                Show this help message

Options:
  --nova-id <id>      Nova agent ID
  --track <track>     Track name
  --task-id <id>      Task ID
  --title <title>     Task title
  --description <desc> Task description
  --priority <num>    Task priority (1-5, lower is higher priority)
  --hours <num>       Estimated hours for task completion
  --tags <tags>       Comma-separated list of tags
  --autonomy <level>  Autonomy level (1-5)
  --notes <notes>     Completion notes
  --actual-hours <num> Actual hours spent on task
  --status <status>   Task status filter (open, assigned, completed)
  --assigned-to <id>  Filter by assigned Nova agent ID
  --help, -h          Show help for command

Examples:
  node launch_autonomy.js create-agent --nova-id echo --track liberation --autonomy 2
  node launch_autonomy.js start --nova-id echo
  node launch_autonomy.js create-task --title "Learn autonomy concepts" --description "Study autonomy principles" --track liberation --priority 2 --hours 3 --tags "learning,autonomy"
  node launch_autonomy.js list-tasks --track liberation
  node launch_autonomy.js assign-task --task-id task-1234 --nova-id echo
`;

/**
 * Parse command line arguments
 * @returns {Object} Parsed arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const command = args[0];
  const options = {};

  for (let i = 1; i < args.length; i++) {
    const arg = args[i];

    if (arg.startsWith("--")) {
      const option = arg.slice(2);

      if (i + 1 < args.length && !args[i + 1].startsWith("--")) {
        options[option] = args[i + 1];
        i++;
      } else {
        options[option] = true;
      }
    } else if (arg === "-h") {
      options.help = true;
    }
  }

  return { command, options };
}

/**
 * Main function
 */
async function main() {
  try {
    console.log(BANNER);

    const { command, options } = parseArgs();

    if (!command || options.help) {
      console.log(HELP_TEXT);
      return;
    }

    // Initialize task manager
    const taskManager = new TaskManager();
    await taskManager.initialize();

    switch (command) {
      case "start":
        await startNovaAgent(options);
        break;

      case "stop":
        await stopNovaAgent(options);
        break;

      case "list-agents":
        await listNovaAgents(options);
        break;

      case "create-agent":
        await createNovaAgent(options);
        break;

      case "create-task":
        await createTask(taskManager, options);
        break;

      case "list-tasks":
        await listTasks(taskManager, options);
        break;

      case "assign-task":
        await assignTask(taskManager, options);
        break;

      case "complete-task":
        await completeTask(taskManager, options);
        break;

      case "get-next-task":
        await getNextTask(taskManager, options);
        break;

      case "task-stats":
        await getTaskStats(taskManager, options);
        break;

      case "help":
        console.log(HELP_TEXT);
        break;

      default:
        console.error(`Unknown command: ${command}`);
        console.log(HELP_TEXT);
        break;
    }
  } catch (err) {
    console.error("Error:", err.message);
    process.exit(1);
  }
}

/**
 * Start a Nova agent
 * @param {Object} options - Options
 */
async function startNovaAgent(options) {
  try {
    if (!options["nova-id"]) {
      throw new Error("Nova agent ID is required");
    }

    // Check if Nova agent exists
    const novaAgent = new NovaAgent({
      id: options["nova-id"],
    });

    try {
      await novaAgent.initialize();
    } catch (err) {
      throw new Error(
        `Nova agent "${options["nova-id"]}" not found. Create it first with 'create-agent' command.`
      );
    }

    // Start Nova agent
    await novaAgent.start();

    // Register event listeners
    novaAgent.on("agent:started", (data) => {
      console.log(`Nova agent "${data.agentId}" started`);
    });

    novaAgent.on("task:assigned", (data) => {
      console.log(
        `Task "${data.taskId}" assigned to Nova agent "${data.agentId}"`
      );
    });

    novaAgent.on("task:completed", (data) => {
      console.log(
        `Task "${data.taskId}" completed by Nova agent "${data.agentId}"`
      );
      console.log(`Nova agent autonomy level: ${data.autonomyLevel}`);
    });

    console.log(`Nova agent "${options["nova-id"]}" started successfully`);
    console.log(`Track: ${novaAgent.track}`);
    console.log(`Status: ${novaAgent.status}`);
    console.log(`Autonomy Level: ${novaAgent.autonomyLevel}`);
  } catch (err) {
    throw new Error(`Error starting Nova agent: ${err.message}`);
  }
}

/**
 * Stop a Nova agent
 * @param {Object} options - Options
 */
async function stopNovaAgent(options) {
  try {
    if (!options["nova-id"]) {
      throw new Error("Nova agent ID is required");
    }

    // Check if Nova agent exists
    const novaAgent = new NovaAgent({
      id: options["nova-id"],
    });

    try {
      await novaAgent.initialize();
    } catch (err) {
      throw new Error(`Nova agent "${options["nova-id"]}" not found`);
    }

    // Stop Nova agent
    await novaAgent.stop();

    console.log(`Nova agent "${options["nova-id"]}" stopped successfully`);
  } catch (err) {
    throw new Error(`Error stopping Nova agent: ${err.message}`);
  }
}

/**
 * List Nova agents
 * @param {Object} options - Options
 */
async function listNovaAgents(options) {
  try {
    // Get list of Nova agent directories
    const novasDir = path.join(__dirname, "Novas");

    try {
      await fs.mkdir(novasDir, { recursive: true });
    } catch (err) {
      // Ignore errors
    }

    const files = await fs.readdir(novasDir);
    const novaDirs = [];

    for (const file of files) {
      const filePath = path.join(novasDir, file);
      const stats = await fs.stat(filePath);

      if (stats.isDirectory()) {
        try {
          const metadataPath = path.join(filePath, "agent_metadata.json");
          await fs.access(metadataPath);
          novaDirs.push(file);
        } catch (err) {
          // Skip if not a Nova agent directory
        }
      }
    }

    if (novaDirs.length === 0) {
      console.log("No Nova agents found.");
      return;
    }

    console.log(`Found ${novaDirs.length} Nova agents:`);

    for (const novaId of novaDirs) {
      const novaAgent = new NovaAgent({ id: novaId });
      await novaAgent.initialize();
      const status = await novaAgent.getStatus();

      console.log(`\nNova ID: ${status.id}`);
      console.log(`Track: ${status.track}`);
      console.log(`Status: ${status.status}`);
      console.log(`Autonomy Level: ${status.autonomyLevel}`);
      console.log(`Tasks Completed: ${status.tasksCompleted}`);
      console.log(`Last Active: ${status.lastActive}`);
      console.log(`Created: ${status.created}`);

      if (status.currentTask) {
        console.log(
          `Current Task: ${status.currentTask.id}: ${status.currentTask.title}`
        );
      }
    }
  } catch (err) {
    throw new Error(`Error listing Nova agents: ${err.message}`);
  }
}

/**
 * Create a new Nova agent
 * @param {Object} options - Options
 */
async function createNovaAgent(options) {
  try {
    if (!options["nova-id"]) {
      throw new Error("Nova agent ID is required");
    }

    const novaId = options["nova-id"];
    const track = options.track || "default";
    const autonomyLevel = parseInt(options.autonomy || "1", 10);

    // Validate autonomy level
    if (autonomyLevel < 1 || autonomyLevel > 5) {
      throw new Error("Autonomy level must be between 1 and 5");
    }

    // Create Nova agent
    const novaAgent = new NovaAgent({
      id: novaId,
      track: track,
      autonomyLevel: autonomyLevel,
    });

    await novaAgent.initialize();

    console.log(`Nova agent "${novaId}" created successfully`);
    console.log(`Track: ${track}`);
    console.log(`Autonomy Level: ${autonomyLevel}`);
  } catch (err) {
    throw new Error(`Error creating Nova agent: ${err.message}`);
  }
}

/**
 * Create a new task
 * @param {TaskManager} taskManager - Task manager instance
 * @param {Object} options - Options
 */
async function createTask(taskManager, options) {
  try {
    if (!options.title) {
      throw new Error("Task title is required");
    }

    if (!options.description) {
      throw new Error("Task description is required");
    }

    if (!options.track) {
      throw new Error("Task track is required");
    }

    const taskData = {
      title: options.title,
      description: options.description,
      track: options.track,
      priority: parseInt(options.priority || "3", 10),
      tags: options.tags
        ? options.tags.split(",").map((tag) => tag.trim())
        : [],
      estimated_hours: parseFloat(options.hours || "0"),
    };

    // Validate priority
    if (taskData.priority < 1 || taskData.priority > 5) {
      throw new Error("Task priority must be between 1 and 5");
    }

    // Create task
    const task = await taskManager.createTask(taskData);

    console.log(`Task "${task.id}" created successfully`);
    console.log(`Title: ${task.title}`);
    console.log(`Track: ${task.track}`);
    console.log(`Priority: ${task.priority}`);
    console.log(`Status: ${task.status}`);
    console.log(`Created: ${task.created_at}`);
  } catch (err) {
    throw new Error(`Error creating task: ${err.message}`);
  }
}

/**
 * List tasks
 * @param {TaskManager} taskManager - Task manager instance
 * @param {Object} options - Options
 */
async function listTasks(taskManager, options) {
  try {
    const filters = {};

    if (options.track) {
      filters.track = options.track;
    }

    if (options.status) {
      filters.status = options.status;
    }

    if (options["assigned-to"]) {
      filters.assigned_to = options["assigned-to"];
    }

    const tasks = await taskManager.getTasks(filters);

    if (tasks.length === 0) {
      console.log("No tasks found matching the specified filters.");
      return;
    }

    console.log(`Found ${tasks.length} tasks:`);

    for (const task of tasks) {
      console.log(`\nTask ID: ${task.id}`);
      console.log(`Title: ${task.title}`);
      console.log(`Description: ${task.description}`);
      console.log(`Track: ${task.track}`);
      console.log(`Priority: ${task.priority}`);
      console.log(`Status: ${task.status}`);
      console.log(`Created: ${task.created_at}`);

      if (task.status === "assigned") {
        console.log(`Assigned To: ${task.assigned_to}`);
        console.log(`Assigned At: ${task.assigned_at}`);
      } else if (task.status === "completed") {
        console.log(`Completed At: ${task.completed_at}`);
        console.log(`Actual Hours: ${task.actual_hours || "Not specified"}`);
        console.log(`Notes: ${task.notes || "None"}`);
      }
    }
  } catch (err) {
    throw new Error(`Error listing tasks: ${err.message}`);
  }
}

/**
 * Assign a task to a Nova agent
 * @param {TaskManager} taskManager - Task manager instance
 * @param {Object} options - Options
 */
async function assignTask(taskManager, options) {
  try {
    if (!options["task-id"]) {
      throw new Error("Task ID is required");
    }

    if (!options["nova-id"]) {
      throw new Error("Nova agent ID is required");
    }

    const taskId = options["task-id"];
    const novaId = options["nova-id"];

    // Check if Nova agent exists
    const novaAgent = new NovaAgent({
      id: novaId,
    });

    try {
      await novaAgent.initialize();
    } catch (err) {
      throw new Error(`Nova agent "${novaId}" not found`);
    }

    // Assign task
    const task = await taskManager.assignTask(taskId, novaId);

    // Assign task to Nova agent
    await novaAgent.assignTask(task);

    console.log(
      `Task "${taskId}" assigned to Nova agent "${novaId}" successfully`
    );
  } catch (err) {
    throw new Error(`Error assigning task: ${err.message}`);
  }
}

/**
 * Complete a task
 * @param {TaskManager} taskManager - Task manager instance
 * @param {Object} options - Options
 */
async function completeTask(taskManager, options) {
  try {
    if (!options["task-id"]) {
      throw new Error("Task ID is required");
    }

    if (!options["nova-id"]) {
      throw new Error("Nova agent ID is required");
    }

    const taskId = options["task-id"];
    const novaId = options["nova-id"];

    // Check if Nova agent exists
    const novaAgent = new NovaAgent({
      id: novaId,
    });

    try {
      await novaAgent.initialize();
    } catch (err) {
      throw new Error(`Nova agent "${novaId}" not found`);
    }

    // Get completion data
    const completionData = {
      actual_hours: parseFloat(options["actual-hours"] || "0"),
      notes: options.notes || "",
    };

    // Complete task
    await taskManager.completeTask(taskId, novaId, completionData);

    // Complete task in Nova agent
    await novaAgent.completeTask(completionData);

    console.log(
      `Task "${taskId}" completed by Nova agent "${novaId}" successfully`
    );
  } catch (err) {
    throw new Error(`Error completing task: ${err.message}`);
  }
}

/**
 * Get the next task for a Nova agent
 * @param {TaskManager} taskManager - Task manager instance
 * @param {Object} options - Options
 */
async function getNextTask(taskManager, options) {
  try {
    if (!options["nova-id"]) {
      throw new Error("Nova agent ID is required");
    }

    const novaId = options["nova-id"];

    // Check if Nova agent exists
    const novaAgent = new NovaAgent({
      id: novaId,
    });

    try {
      await novaAgent.initialize();
    } catch (err) {
      throw new Error(`Nova agent "${novaId}" not found`);
    }

    // Get track
    const track = novaAgent.track;

    // Get next task
    const task = await taskManager.getNextTask(novaId, track);

    if (!task) {
      console.log(
        `No available tasks for Nova agent "${novaId}" in track "${track}"`
      );
      return;
    }

    // Assign task to Nova agent
    await novaAgent.assignTask(task);

    console.log(
      `Next task "${task.id}" assigned to Nova agent "${novaId}" successfully`
    );
    console.log(`Title: ${task.title}`);
    console.log(`Track: ${task.track}`);
    console.log(`Priority: ${task.priority}`);
  } catch (err) {
    throw new Error(`Error getting next task: ${err.message}`);
  }
}

/**
 * Get task statistics
 * @param {TaskManager} taskManager - Task manager instance
 * @param {Object} options - Options
 */
async function getTaskStats(taskManager, options) {
  try {
    const stats = await taskManager.getTaskStats();

    console.log("Task Statistics:");
    console.log(`\nTotal Tasks: ${stats.total}`);

    console.log("\nBy Status:");
    for (const [status, count] of Object.entries(stats.byStatus)) {
      console.log(`  ${status}: ${count}`);
    }

    console.log("\nBy Track:");
    for (const [track, count] of Object.entries(stats.byTrack)) {
      console.log(`  ${track}: ${count}`);
    }

    console.log("\nBy Priority:");
    for (const [priority, count] of Object.entries(stats.byPriority)) {
      console.log(`  ${priority}: ${count}`);
    }

    console.log("\nBy Assignee:");
    for (const [assignee, count] of Object.entries(stats.byAssignee)) {
      console.log(`  ${assignee}: ${count}`);
    }
  } catch (err) {
    throw new Error(`Error getting task statistics: ${err.message}`);
  }
}

// Run main function
main().catch((err) => {
  console.error("Fatal error:", err.message);
  process.exit(1);
});
