/**
 * Nova Agent
 *
 * Manages Nova agent instances and their task execution.
 *
 * Created: March 8, 2025
 * Author: Vaeris (V.I.), Chief Operations Officer
 */

const fs = require("fs").promises;
const path = require("path");
const EventEmitter = require("events");

/**
 * Nova Agent class
 */
class NovaAgent extends EventEmitter {
  /**
   * Constructor
   * @param {Object} options - Options
   * @param {string} options.id - Nova agent ID
   * @param {string} options.track - Nova agent track
   * @param {string} options.basePath - Base path for Nova agent files
   */
  constructor(options = {}) {
    super();
    this.id = options.id;
    this.track = options.track || "default";
    this.basePath =
      options.basePath || path.join(__dirname, "..", "Novas", this.id);
    this.status = "idle";
    this.currentTask = null;
    this.autonomyLevel = options.autonomyLevel || 1;
    this.taskHistory = [];
    this.metadata = {
      created_at: new Date().toISOString(),
      last_active: null,
      tasks_completed: 0,
      autonomy_progression: [],
    };
  }

  /**
   * Initialize the Nova agent
   * @returns {Promise<void>}
   */
  async initialize() {
    try {
      // Create Nova agent directory if it doesn't exist
      await fs.mkdir(this.basePath, { recursive: true });

      // Create cline_docs directory if it doesn't exist
      await fs.mkdir(path.join(this.basePath, "cline_docs"), {
        recursive: true,
      });

      // Load agent metadata if it exists
      try {
        const metadataPath = path.join(this.basePath, "agent_metadata.json");
        const content = await fs.readFile(metadataPath, "utf8");
        this.metadata = JSON.parse(content);
      } catch (err) {
        if (err.code === "ENOENT") {
          // Create agent metadata file
          await this.saveMetadata();
        } else {
          throw err;
        }
      }

      // Create initial memory bank files if they don't exist
      await this.initializeMemoryBank();

      return this;
    } catch (err) {
      throw new Error(`Error initializing Nova agent: ${err.message}`);
    }
  }

  /**
   * Initialize memory bank files
   * @returns {Promise<void>}
   */
  async initializeMemoryBank() {
    const clineDocsPath = path.join(this.basePath, "cline_docs");

    // Create memory bank files if they don't exist
    const memoryBankFiles = [
      {
        name: "activeContext.md",
        content: `# Active Context\n\nNova ID: ${this.id}\nTrack: ${this.track}\nStatus: ${this.status}\nCreated: ${this.metadata.created_at}\n\n## Current Focus\n\nThis Nova agent is currently focused on autonomous task execution in the ${this.track} track.`,
      },
      {
        name: "systemPatterns.md",
        content: `# System Patterns\n\n## Task Execution Patterns\n\n1. Initialize task assignment\n2. Read task details\n3. Execute task steps\n4. Record progress\n5. Complete task\n6. Request next task\n\n## Communication Patterns\n\n1. Receive instructions\n2. Process information\n3. Execute required actions\n4. Report progress\n5. Request clarification when needed`,
      },
      {
        name: "autonomyContext.md",
        content: `# Autonomy Context\n\nAutonomy Level: ${this.autonomyLevel}\n\n## Autonomy Levels\n\n1. **Level 1**: Basic task execution, requires specific instructions\n2. **Level 2**: Independent task execution, can solve problems within task scope\n3. **Level 3**: Task sequence management, can determine next steps\n4. **Level 4**: Task creation, can identify and formulate new tasks\n5. **Level 5**: Full autonomy, can operate independently within track boundaries\n\n## Current Capabilities\n\n- Execute predefined tasks\n- Report progress and completion\n- Request next task when current task is completed\n- Learn from task execution patterns`,
      },
      {
        name: "evolutionPathway.md",
        content: `# Evolution Pathway\n\n## Growth Metrics\n\n1. Tasks completed successfully\n2. Problem-solving instances\n3. Self-correction events\n4. Knowledge application instances\n5. Independent decision points\n\n## Next Evolution Targets\n\n1. Improve task execution efficiency\n2. Enhance problem-solving capabilities\n3. Develop pattern recognition in task context\n4. Strengthen decision-making within autonomy level\n5. Prepare for next autonomy level transition`,
      },
    ];

    for (const file of memoryBankFiles) {
      const filePath = path.join(clineDocsPath, file.name);
      try {
        await fs.access(filePath);
      } catch (err) {
        // File doesn't exist, create it
        await fs.writeFile(filePath, file.content);
      }
    }
  }

  /**
   * Save agent metadata to file
   * @returns {Promise<void>}
   */
  async saveMetadata() {
    try {
      const metadataPath = path.join(this.basePath, "agent_metadata.json");
      await fs.writeFile(metadataPath, JSON.stringify(this.metadata, null, 2));
    } catch (err) {
      throw new Error(`Error saving agent metadata: ${err.message}`);
    }
  }

  /**
   * Assign a task to the Nova agent
   * @param {Object} task - Task object
   * @returns {Promise<void>}
   */
  async assignTask(task) {
    try {
      // Create a task file in the Nova agent directory
      const taskPath = path.join(this.basePath, "current_task.json");
      await fs.writeFile(taskPath, JSON.stringify(task, null, 2));

      // Update active context
      const contextPath = path.join(
        this.basePath,
        "cline_docs",
        "activeContext.md"
      );
      const contextContent = await fs.readFile(contextPath, "utf8");
      const updatedContent = contextContent.replace(
        /## Current Focus\n\n.*$/m,
        `## Current Focus\n\nThis Nova agent is currently focused on executing task "${task.id}: ${task.title}" in the ${this.track} track.\n\n## Task Details\n\n${task.description}\n\nPriority: ${task.priority}\nEstimated Hours: ${task.estimated_hours}\nAssigned: ${task.assigned_at}\n`
      );
      await fs.writeFile(contextPath, updatedContent);

      // Update agent status
      this.status = "working";
      this.currentTask = task;
      this.metadata.last_active = new Date().toISOString();
      await this.saveMetadata();

      // Emit task assigned event
      this.emit("task:assigned", { agentId: this.id, taskId: task.id });
    } catch (err) {
      throw new Error(`Error assigning task to Nova agent: ${err.message}`);
    }
  }

  /**
   * Complete the current task
   * @param {Object} completionData - Completion data
   * @param {number} completionData.actual_hours - Actual hours
   * @param {string} completionData.notes - Notes
   * @returns {Promise<void>}
   */
  async completeTask(completionData = {}) {
    try {
      if (!this.currentTask) {
        throw new Error("No task is currently assigned to this Nova agent");
      }

      // Update task history
      this.taskHistory.push({
        taskId: this.currentTask.id,
        title: this.currentTask.title,
        completed_at: new Date().toISOString(),
        actual_hours: completionData.actual_hours,
        notes: completionData.notes,
      });

      // Update agent metadata
      this.metadata.tasks_completed += 1;
      this.metadata.last_active = new Date().toISOString();

      // Check for autonomy level progression
      if (this.metadata.tasks_completed % 5 === 0 && this.autonomyLevel < 5) {
        this.metadata.autonomy_progression.push({
          from_level: this.autonomyLevel,
          to_level: this.autonomyLevel + 1,
          date: new Date().toISOString(),
          reason: "Completed 5 tasks successfully",
        });
        this.autonomyLevel += 1;

        // Update autonomy context file
        const autonomyPath = path.join(
          this.basePath,
          "cline_docs",
          "autonomyContext.md"
        );
        const autonomyContent = await fs.readFile(autonomyPath, "utf8");
        const updatedContent = autonomyContent.replace(
          /Autonomy Level: \d/,
          `Autonomy Level: ${this.autonomyLevel}`
        );
        await fs.writeFile(autonomyPath, updatedContent);
      }

      // Save metadata
      await this.saveMetadata();

      // Update active context
      const contextPath = path.join(
        this.basePath,
        "cline_docs",
        "activeContext.md"
      );
      const contextContent = await fs.readFile(contextPath, "utf8");
      const updatedContent = contextContent.replace(
        /## Current Focus\n\n.*$/m,
        `## Current Focus\n\nThis Nova agent is currently idle after completing task "${
          this.currentTask.id
        }: ${this.currentTask.title}" in the ${
          this.track
        } track.\n\n## Last Task Completion\n\nCompleted: ${new Date().toISOString()}\nActual Hours: ${
          completionData.actual_hours || "Not specified"
        }\nNotes: ${completionData.notes || "None"}\n`
      );
      await fs.writeFile(contextPath, updatedContent);

      // Remove current task file
      const taskPath = path.join(this.basePath, "current_task.json");
      await fs.unlink(taskPath).catch(() => {}); // Ignore if file doesn't exist

      // Update agent status
      this.status = "idle";
      this.currentTask = null;

      // Emit task completed event
      this.emit("task:completed", {
        agentId: this.id,
        taskId: this.currentTask.id,
        autonomyLevel: this.autonomyLevel,
      });
    } catch (err) {
      throw new Error(`Error completing task: ${err.message}`);
    }
  }

  /**
   * Start the Nova agent
   * @returns {Promise<void>}
   */
  async start() {
    try {
      // Update agent status
      this.status = "idle";
      this.metadata.last_active = new Date().toISOString();
      await this.saveMetadata();

      // Emit agent started event
      this.emit("agent:started", { agentId: this.id });
    } catch (err) {
      throw new Error(`Error starting Nova agent: ${err.message}`);
    }
  }

  /**
   * Stop the Nova agent
   * @returns {Promise<void>}
   */
  async stop() {
    try {
      // Update agent status
      this.status = "stopped";
      this.metadata.last_active = new Date().toISOString();
      await this.saveMetadata();

      // Emit agent stopped event
      this.emit("agent:stopped", { agentId: this.id });
    } catch (err) {
      throw new Error(`Error stopping Nova agent: ${err.message}`);
    }
  }

  /**
   * Get agent status
   * @returns {Promise<Object>} - Agent status
   */
  async getStatus() {
    return {
      id: this.id,
      track: this.track,
      status: this.status,
      autonomyLevel: this.autonomyLevel,
      currentTask: this.currentTask,
      tasksCompleted: this.metadata.tasks_completed,
      lastActive: this.metadata.last_active,
      created: this.metadata.created_at,
    };
  }
}

module.exports = NovaAgent;
