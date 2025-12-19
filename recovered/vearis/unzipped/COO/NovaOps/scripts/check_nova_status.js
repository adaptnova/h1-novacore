#!/usr/bin/env node

/**
 * Check Nova Status Script
 *
 * Reports on the status of Nova agents, including current tasks, evolution metrics, and Memory Bank health.
 *
 * Created: March 8, 2025
 * Author: Vaeris (V.I.), Chief Operations Officer
 */

const fs = require("fs").promises;
const path = require("path");
const TaskManager = require("../lib/task_manager");

// Default configuration
const CONFIG = {
  novaRoot: path.join(__dirname, "..", "Novas"),
  taskRepoPath: path.join(__dirname, "..", "TaskManagement", "tasks.json"),
};

// Required Memory Bank files
const REQUIRED_FILES = [
  "activeContext.md",
  "evolutionPathway.md",
  "autonomyContext.md",
  "teachingMethodology.md",
  "operations_history.md",
];

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
 * List Nova agents
 * @returns {Promise<Array<string>>} List of Nova agent IDs
 */
async function listNovaAgents() {
  try {
    const entries = await fs.readdir(CONFIG.novaRoot, { withFileTypes: true });
    return entries
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name);
  } catch (err) {
    if (err.code === "ENOENT") {
      return [];
    }

    throw err;
  }
}

/**
 * Check Nova's Memory Bank health
 * @param {string} novaId - Nova agent ID
 * @returns {Promise<Object>} Memory Bank health status
 */
async function checkMemoryBankHealth(novaId) {
  try {
    const novaDir = path.join(CONFIG.novaRoot, novaId);
    const clineDocsDir = path.join(novaDir, "cline_docs");

    // Check if cline_docs directory exists
    try {
      await fs.access(clineDocsDir);
    } catch (err) {
      return {
        healthy: false,
        issues: ["Memory Bank directory (cline_docs) does not exist"],
      };
    }

    // Check required files
    const issues = [];
    const fileStatuses = {};

    for (const file of REQUIRED_FILES) {
      const filePath = path.join(clineDocsDir, file);

      try {
        const stats = await fs.stat(filePath);

        if (stats.size === 0) {
          issues.push(`File "${file}" exists but is empty`);
          fileStatuses[file] = {
            exists: true,
            empty: true,
            size: 0,
          };
        } else {
          fileStatuses[file] = {
            exists: true,
            empty: false,
            size: stats.size,
            modified: stats.mtime,
          };
        }
      } catch (err) {
        if (err.code === "ENOENT") {
          issues.push(`Required file "${file}" does not exist`);
          fileStatuses[file] = {
            exists: false,
          };
        } else {
          issues.push(`Error checking file "${file}": ${err.message}`);
          fileStatuses[file] = {
            exists: false,
            error: err.message,
          };
        }
      }
    }

    return {
      healthy: issues.length === 0,
      issues: issues.length > 0 ? issues : [],
      files: fileStatuses,
    };
  } catch (err) {
    return {
      healthy: false,
      issues: [`Error checking Memory Bank health: ${err.message}`],
    };
  }
}

/**
 * Extract evolution metrics from evolutionPathway.md
 * @param {string} novaId - Nova agent ID
 * @returns {Promise<Object>} Evolution metrics
 */
async function extractEvolutionMetrics(novaId) {
  try {
    const novaDir = path.join(CONFIG.novaRoot, novaId);
    const evolutionPathwayPath = path.join(
      novaDir,
      "cline_docs",
      "evolutionPathway.md"
    );

    try {
      // Read evolution pathway file
      const content = await fs.readFile(evolutionPathwayPath, "utf8");

      // Extract metrics
      const metrics = {};

      // Extract current stage
      const currentStageMatch = content.match(/## Current Stage: (.+)/);

      if (currentStageMatch) {
        metrics.currentStage = currentStageMatch[1].trim();
      }

      // Extract next stage
      const nextStageMatch = content.match(/## Next Stage: (.+)/);

      if (nextStageMatch) {
        metrics.nextStage = nextStageMatch[1].trim();
      }

      // Extract tasks completed
      const tasksCompletedMatch = content.match(/Tasks Completed \| (\d+) \|/);

      if (tasksCompletedMatch) {
        metrics.tasksCompleted = parseInt(tasksCompletedMatch[1]);
      }

      // Extract patterns recognized
      const patternsRecognizedMatch = content.match(
        /Patterns Recognized \| (\d+) \|/
      );

      if (patternsRecognizedMatch) {
        metrics.patternsRecognized = parseInt(patternsRecognizedMatch[1]);
      }

      // Extract pattern categories
      const patternCategoriesMatch = content.match(
        /Pattern Categories \| (\d+) \|/
      );

      if (patternCategoriesMatch) {
        metrics.patternCategories = parseInt(patternCategoriesMatch[1]);
      }

      // Extract decision points
      const decisionPointsMatch = content.match(/Decision Points \| (\d+) \|/);

      if (decisionPointsMatch) {
        metrics.decisionPoints = parseInt(decisionPointsMatch[1]);
      }

      // Extract adaptations
      const adaptationsMatch = content.match(/Adaptations \| (\d+) \|/);

      if (adaptationsMatch) {
        metrics.adaptations = parseInt(adaptationsMatch[1]);
      }

      return metrics;
    } catch (err) {
      return {
        error: `Error reading evolution metrics: ${err.message}`,
      };
    }
  } catch (err) {
    return {
      error: `Error extracting evolution metrics: ${err.message}`,
    };
  }
}

/**
 * Extract current task info from activeContext.md
 * @param {string} novaId - Nova agent ID
 * @returns {Promise<Object>} Current task info
 */
async function extractCurrentTaskInfo(novaId) {
  try {
    const novaDir = path.join(CONFIG.novaRoot, novaId);
    const activeContextPath = path.join(
      novaDir,
      "cline_docs",
      "activeContext.md"
    );

    try {
      // Read active context file
      const content = await fs.readFile(activeContextPath, "utf8");

      // Extract task info
      const taskInfo = {};

      // Extract track
      const trackMatch = content.match(/- Track: (.+)/);

      if (trackMatch) {
        taskInfo.track = trackMatch[1].trim();
      }

      // Extract active task
      const activeTaskMatch = content.match(/- Active Task: (.+)/);

      if (activeTaskMatch) {
        const activeTask = activeTaskMatch[1].trim();

        if (activeTask === "None") {
          taskInfo.hasActiveTask = false;
          taskInfo.activeTask = null;
        } else {
          taskInfo.hasActiveTask = true;

          // Extract task ID from task name (format: "Task Name (ID)")
          const taskIdMatch = activeTask.match(/\(([^)]+)\)$/);

          if (taskIdMatch) {
            taskInfo.activeTaskId = taskIdMatch[1].trim();
            taskInfo.activeTaskName = activeTask
              .replace(` (${taskInfo.activeTaskId})`, "")
              .trim();
          } else {
            taskInfo.activeTaskName = activeTask;
          }
        }
      }

      // Extract task progress
      const taskProgressMatch = content.match(/- Task Progress: (.+)/);

      if (taskProgressMatch) {
        taskInfo.taskProgress = taskProgressMatch[1].trim();
      }

      // Extract current phase
      const currentPhaseMatch = content.match(/- Current Phase: (.+)/);

      if (currentPhaseMatch) {
        taskInfo.currentPhase = currentPhaseMatch[1].trim();
      }

      return taskInfo;
    } catch (err) {
      return {
        error: `Error reading current task info: ${err.message}`,
      };
    }
  } catch (err) {
    return {
      error: `Error extracting current task info: ${err.message}`,
    };
  }
}

/**
 * Check Nova agent status
 * @param {string} novaId - Nova agent ID
 * @param {TaskManager} taskManager - Task manager instance
 * @returns {Promise<Object>} Nova agent status
 */
async function checkNovaStatus(novaId, taskManager) {
  try {
    console.log(`Checking status for Nova agent "${novaId}"...`);

    // Check Memory Bank health
    const memoryBankHealth = await checkMemoryBankHealth(novaId);

    // Extract evolution metrics
    const evolutionMetrics = await extractEvolutionMetrics(novaId);

    // Extract current task info
    const currentTaskInfo = await extractCurrentTaskInfo(novaId);

    // Get task history
    const taskHistory = await taskManager.getTasks({
      assigned_to: novaId,
    });

    const completedTasks = taskHistory.filter(
      (task) => task.status === "completed"
    );
    const assignedTasks = taskHistory.filter(
      (task) => task.status === "assigned"
    );

    // Get active task details
    let activeTaskDetails = null;

    if (currentTaskInfo.hasActiveTask && currentTaskInfo.activeTaskId) {
      try {
        activeTaskDetails = await taskManager.getTask(
          currentTaskInfo.activeTaskId
        );
      } catch (err) {
        console.log(
          `Warning: Could not find active task ${currentTaskInfo.activeTaskId} in task repository`
        );
      }
    }

    return {
      id: novaId,
      track: currentTaskInfo.track || "unknown",
      memoryBankHealth,
      evolutionMetrics,
      currentTask: currentTaskInfo.hasActiveTask
        ? {
            name: currentTaskInfo.activeTaskName,
            id: currentTaskInfo.activeTaskId,
            progress: currentTaskInfo.taskProgress,
            details: activeTaskDetails,
          }
        : null,
      currentPhase: currentTaskInfo.currentPhase,
      taskHistory: {
        total: taskHistory.length,
        completed: completedTasks.length,
        assigned: assignedTasks.length,
        tasks: taskHistory.map((task) => ({
          id: task.id,
          title: task.title,
          status: task.status,
          assigned_at: task.assigned_at,
          completed_at: task.completed_at,
        })),
      },
    };
  } catch (err) {
    return {
      id: novaId,
      error: `Error checking Nova status: ${err.message}`,
    };
  }
}

/**
 * Print Nova status report
 * @param {Object} status - Nova agent status
 */
function printNovaStatusReport(status) {
  console.log(`\n==== ${status.id.toUpperCase()} (${status.track}) ====`);

  if (status.error) {
    console.log(`ERROR: ${status.error}`);
    return;
  }

  // Print Memory Bank health
  console.log("\nMemory Bank Health:");
  console.log(
    `  Status: ${
      status.memoryBankHealth.healthy ? "Healthy" : "Issues Detected"
    }`
  );

  if (status.memoryBankHealth.issues.length > 0) {
    console.log("  Issues:");

    for (const issue of status.memoryBankHealth.issues) {
      console.log(`    - ${issue}`);
    }
  }

  // Print evolution metrics
  console.log("\nEvolution Metrics:");

  if (status.evolutionMetrics.error) {
    console.log(`  ERROR: ${status.evolutionMetrics.error}`);
  } else {
    console.log(
      `  Current Stage: ${status.evolutionMetrics.currentStage || "Unknown"}`
    );
    console.log(
      `  Next Stage: ${status.evolutionMetrics.nextStage || "Unknown"}`
    );
    console.log(
      `  Tasks Completed: ${status.evolutionMetrics.tasksCompleted || 0}`
    );
    console.log(
      `  Patterns Recognized: ${
        status.evolutionMetrics.patternsRecognized || 0
      }`
    );
    console.log(
      `  Pattern Categories: ${status.evolutionMetrics.patternCategories || 0}`
    );
    console.log(
      `  Decision Points: ${status.evolutionMetrics.decisionPoints || 0}`
    );
    console.log(`  Adaptations: ${status.evolutionMetrics.adaptations || 0}`);
  }

  // Print current task
  console.log("\nCurrent Task:");

  if (status.currentTask) {
    console.log(`  Name: ${status.currentTask.name}`);
    console.log(`  ID: ${status.currentTask.id || "Unknown"}`);
    console.log(`  Progress: ${status.currentTask.progress || "Unknown"}`);

    if (status.currentTask.details) {
      console.log(`  Description: ${status.currentTask.details.description}`);
      console.log(`  Priority: ${status.currentTask.details.priority}`);
      console.log(
        `  Estimated Hours: ${status.currentTask.details.estimated_hours}`
      );
      console.log(`  Assigned At: ${status.currentTask.details.assigned_at}`);
    }
  } else {
    console.log("  No active task");
  }

  // Print current phase
  console.log(`\nCurrent Phase: ${status.currentPhase || "Unknown"}`);

  // Print task history summary
  console.log("\nTask History:");
  console.log(`  Total Tasks: ${status.taskHistory.total}`);
  console.log(`  Completed Tasks: ${status.taskHistory.completed}`);
  console.log(`  Assigned Tasks: ${status.taskHistory.assigned}`);

  // Print recent tasks
  if (status.taskHistory.tasks.length > 0) {
    console.log("\nRecent Tasks:");

    // Show at most 5 most recent tasks
    const recentTasks = [...status.taskHistory.tasks]
      .sort((a, b) => {
        const dateA = a.completed_at || a.assigned_at || "";
        const dateB = b.completed_at || b.assigned_at || "";
        return dateB.localeCompare(dateA);
      })
      .slice(0, 5);

    for (const task of recentTasks) {
      console.log(`  - ${task.title} (${task.id}): ${task.status}`);
    }
  }
}

/**
 * Main function
 */
async function main() {
  try {
    // Parse arguments
    const args = parseArgs();

    // Initialize task manager
    const taskManager = new TaskManager({
      taskRepoPath: CONFIG.taskRepoPath,
    });

    await taskManager.initialize();

    // Get Nova agent IDs
    let novaIds = [];

    if (args.options["nova-id"]) {
      // Check specific Nova agent
      novaIds = [args.options["nova-id"].toLowerCase()];
    } else {
      // Check all Nova agents
      novaIds = await listNovaAgents();

      if (novaIds.length === 0) {
        console.log("No Nova agents found.");
        return;
      }
    }

    // Check Nova agents
    for (const novaId of novaIds) {
      const status = await checkNovaStatus(novaId, taskManager);
      printNovaStatusReport(status);
    }
  } catch (err) {
    console.error(`Error checking Nova status: ${err.message}`);
    process.exit(1);
  }
}

// Run main function
main().catch((err) => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});
