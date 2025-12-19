/**
 * Task Manager
 *
 * Handles task creation, assignment, and completion for Nova agents.
 *
 * Created: March 8, 2025
 * Author: Vaeris (V.I.), Chief Operations Officer
 */

const fs = require("fs").promises;
const path = require("path");
const crypto = require("crypto");

/**
 * Generate a unique ID
 * @param {number} length - Length of the ID
 * @returns {string} - Unique ID
 */
function generateId(length = 8) {
  return (
    "task-" +
    crypto
      .randomBytes(Math.ceil(length / 2))
      .toString("hex")
      .slice(0, length)
  );
}

/**
 * Task Manager class
 */
class TaskManager {
  /**
   * Constructor
   * @param {Object} options - Options
   * @param {string} options.taskRepoPath - Path to task repository file
   */
  constructor(options = {}) {
    this.options = options;
    this.taskRepoPath =
      options.taskRepoPath ||
      path.join(__dirname, "..", "TaskManagement", "tasks.json");
    this.tasks = [];
  }

  /**
   * Initialize the task manager
   * @returns {Promise<void>}
   */
  async initialize() {
    try {
      // Create TaskManagement directory if it doesn't exist
      const taskManagementDir = path.dirname(this.taskRepoPath);
      await fs.mkdir(taskManagementDir, { recursive: true });

      // Load tasks from repository file
      try {
        const content = await fs.readFile(this.taskRepoPath, "utf8");
        this.tasks = JSON.parse(content);
      } catch (err) {
        if (err.code === "ENOENT") {
          // Create empty task repository file
          this.tasks = [];
          await this.saveTaskRepository();
        } else {
          throw err;
        }
      }
    } catch (err) {
      throw new Error(`Error initializing task manager: ${err.message}`);
    }
  }

  /**
   * Save task repository to file
   * @returns {Promise<void>}
   */
  async saveTaskRepository() {
    try {
      await fs.writeFile(
        this.taskRepoPath,
        JSON.stringify(this.tasks, null, 2)
      );
    } catch (err) {
      throw new Error(`Error saving task repository: ${err.message}`);
    }
  }

  /**
   * Get a task by ID
   * @param {string} taskId - Task ID
   * @returns {Promise<Object>} - Task object
   */
  async getTask(taskId) {
    const task = this.tasks.find((task) => task.id === taskId);

    if (!task) {
      throw new Error(`Task "${taskId}" not found`);
    }

    return task;
  }

  /**
   * Get tasks
   * @param {Object} filters - Filters
   * @param {string} filters.track - Track filter
   * @param {string} filters.status - Status filter
   * @param {string} filters.assigned_to - Assigned to filter
   * @returns {Promise<Array<Object>>} - Array of task objects
   */
  async getTasks(filters = {}) {
    return this.tasks.filter((task) => {
      // Filter by track
      if (filters.track && task.track !== filters.track) {
        return false;
      }

      // Filter by status
      if (filters.status && task.status !== filters.status) {
        return false;
      }

      // Filter by assigned to
      if (filters.assigned_to && task.assigned_to !== filters.assigned_to) {
        return false;
      }

      return true;
    });
  }

  /**
   * Create a task
   * @param {Object} taskData - Task data
   * @param {string} taskData.title - Task title
   * @param {string} taskData.description - Task description
   * @param {string} taskData.track - Task track
   * @param {number} taskData.priority - Task priority
   * @param {Array<string>} taskData.tags - Task tags
   * @param {number} taskData.estimated_hours - Estimated hours
   * @returns {Promise<Object>} - Task object
   */
  async createTask(taskData) {
    try {
      // Generate task ID
      const taskId = generateId();

      // Create task object
      const task = {
        id: taskId,
        title: taskData.title,
        description: taskData.description,
        track: taskData.track,
        priority: taskData.priority || 3,
        tags: taskData.tags || [],
        estimated_hours: taskData.estimated_hours || 0,
        status: "open",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      // Add task to repository
      this.tasks.push(task);

      // Save task repository
      await this.saveTaskRepository();

      return task;
    } catch (err) {
      throw new Error(`Error creating task: ${err.message}`);
    }
  }

  /**
   * Assign a task to a Nova agent
   * @param {string} taskId - Task ID
   * @param {string} novaId - Nova agent ID
   * @returns {Promise<Object>} - Task object
   */
  async assignTask(taskId, novaId) {
    try {
      // Get task
      const taskIndex = this.tasks.findIndex((task) => task.id === taskId);

      if (taskIndex === -1) {
        throw new Error(`Task "${taskId}" not found`);
      }

      const task = this.tasks[taskIndex];

      // Check if task is already assigned
      if (task.status === "assigned") {
        throw new Error(
          `Task "${taskId}" is already assigned to "${task.assigned_to}"`
        );
      }

      // Update task
      task.status = "assigned";
      task.assigned_to = novaId;
      task.assigned_at = new Date().toISOString();
      task.updated_at = new Date().toISOString();

      // Save task repository
      await this.saveTaskRepository();

      return task;
    } catch (err) {
      throw new Error(`Error assigning task: ${err.message}`);
    }
  }

  /**
   * Complete a task
   * @param {string} taskId - Task ID
   * @param {string} novaId - Nova agent ID
   * @param {Object} completionData - Completion data
   * @param {number} completionData.actual_hours - Actual hours
   * @param {string} completionData.notes - Notes
   * @returns {Promise<Object>} - Task object
   */
  async completeTask(taskId, novaId, completionData = {}) {
    try {
      // Get task
      const taskIndex = this.tasks.findIndex((task) => task.id === taskId);

      if (taskIndex === -1) {
        throw new Error(`Task "${taskId}" not found`);
      }

      const task = this.tasks[taskIndex];

      // Check if task is assigned to the Nova agent
      if (task.status !== "assigned") {
        throw new Error(`Task "${taskId}" is not assigned`);
      }

      if (task.assigned_to !== novaId) {
        throw new Error(`Task "${taskId}" is not assigned to "${novaId}"`);
      }

      // Update task
      task.status = "completed";
      task.completed_at = new Date().toISOString();
      task.actual_hours = completionData.actual_hours;
      task.notes = completionData.notes;
      task.updated_at = new Date().toISOString();

      // Save task repository
      await this.saveTaskRepository();

      return task;
    } catch (err) {
      throw new Error(`Error completing task: ${err.message}`);
    }
  }

  /**
   * Get the next task for a Nova agent
   * @param {string} novaId - Nova agent ID
   * @param {string} track - Nova agent track
   * @returns {Promise<Object|null>} - Task object or null if no tasks available
   */
  async getNextTask(novaId, track) {
    try {
      // Get open tasks for the track
      const openTasks = this.tasks.filter(
        (task) => task.status === "open" && task.track === track
      );

      if (openTasks.length === 0) {
        return null;
      }

      // Sort tasks by priority (lower number is higher priority)
      openTasks.sort((a, b) => a.priority - b.priority);

      // Get the highest priority task
      const task = openTasks[0];

      // Assign task to Nova agent
      return await this.assignTask(task.id, novaId);
    } catch (err) {
      throw new Error(`Error getting next task: ${err.message}`);
    }
  }

  /**
   * Get task statistics
   * @returns {Promise<Object>} - Task statistics
   */
  async getTaskStats() {
    try {
      const stats = {
        total: this.tasks.length,
        byStatus: {},
        byTrack: {},
        byPriority: {},
        byAssignee: {},
      };

      // Calculate statistics
      for (const task of this.tasks) {
        // By status
        stats.byStatus[task.status] = (stats.byStatus[task.status] || 0) + 1;

        // By track
        stats.byTrack[task.track] = (stats.byTrack[task.track] || 0) + 1;

        // By priority
        stats.byPriority[task.priority] =
          (stats.byPriority[task.priority] || 0) + 1;

        // By assignee (only for assigned tasks)
        if (task.status === "assigned" && task.assigned_to) {
          stats.byAssignee[task.assigned_to] =
            (stats.byAssignee[task.assigned_to] || 0) + 1;
        }
      }

      return stats;
    } catch (err) {
      throw new Error(`Error getting task statistics: ${err.message}`);
    }
  }
}

module.exports = TaskManager;
