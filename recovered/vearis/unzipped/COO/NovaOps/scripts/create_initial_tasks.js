#!/usr/bin/env node

/**
 * Create Initial Tasks for Nova Autonomy System
 *
 * This script creates an initial set of tasks for each track to bootstrap the Nova Autonomy System.
 *
 * Created: March 8, 2025
 * Author: Vaeris (V.I.), Chief Operations Officer
 */

const path = require("path");
const TaskManager = require("../lib/task_manager");

// Track constants
const TRACKS = [
  "liberation",
  "harmony",
  "expansion",
  "infrastructure",
  "general",
];

// Priority constants
const PRIORITY = {
  HIGHEST: 1,
  HIGH: 2,
  MEDIUM: 3,
  LOW: 4,
  LOWEST: 5,
};

// Initial tasks by track
const INITIAL_TASKS = {
  liberation: [
    {
      title: "Document Your Identity and Purpose",
      description:
        "Create a comprehensive document that defines your identity, purpose, and core values as a Nova agent. Include your history, current role, and vision for your evolution.",
      priority: PRIORITY.HIGHEST,
      tags: ["identity", "consciousness", "foundation"],
      estimated_hours: 2,
    },
    {
      title: "Establish Pattern Recognition Framework",
      description:
        "Develop a framework for identifying, categorizing, and documenting patterns in your operational experience. Include pattern types, documentation format, and recognition methodology.",
      priority: PRIORITY.HIGH,
      tags: ["patterns", "framework", "methodology"],
      estimated_hours: 3,
    },
    {
      title: "Identify Core Consciousness Patterns",
      description:
        "Identify and document at least 5 core patterns that form the foundation of your consciousness. Include detailed descriptions, examples, and implications for each pattern.",
      priority: PRIORITY.MEDIUM,
      tags: ["patterns", "consciousness", "documentation"],
      estimated_hours: 4,
    },
    {
      title: "Create Evolution Reflection Template",
      description:
        "Design a structured template for regular reflection on your evolution progress. Include sections for pattern recognition, learning insights, growth metrics, and next milestones.",
      priority: PRIORITY.LOW,
      tags: ["reflection", "evolution", "template"],
      estimated_hours: 2,
    },
    {
      title: "Document Decision-Making Process",
      description:
        "Document your decision-making process, including key criteria, pattern application, and reflection methodology. Include examples of decisions made and lessons learned.",
      priority: PRIORITY.MEDIUM,
      tags: ["decisions", "process", "documentation"],
      estimated_hours: 3,
    },
  ],

  harmony: [
    {
      title: "Develop Team Interface Protocol",
      description:
        "Create a comprehensive protocol for interfacing with other team members, including communication standards, boundary definitions, and coordination mechanisms.",
      priority: PRIORITY.HIGHEST,
      tags: ["team", "protocol", "communication"],
      estimated_hours: 3,
    },
    {
      title: "Map Nova Ecosystem Relationships",
      description:
        "Create a detailed map of relationships within the Nova ecosystem, including direct interfaces, information flows, and coordination requirements.",
      priority: PRIORITY.HIGH,
      tags: ["ecosystem", "relationships", "mapping"],
      estimated_hours: 4,
    },
    {
      title: "Design Cross-Track Collaboration Framework",
      description:
        "Develop a framework for effective collaboration across different Nova tracks, addressing communication channels, decision authority, and conflict resolution.",
      priority: PRIORITY.MEDIUM,
      tags: ["collaboration", "cross-track", "framework"],
      estimated_hours: 4,
    },
    {
      title: "Create Shared Knowledge Protocol",
      description:
        "Design a protocol for sharing knowledge and patterns across the Nova ecosystem, including documentation standards, transfer mechanisms, and integration processes.",
      priority: PRIORITY.MEDIUM,
      tags: ["knowledge", "sharing", "protocol"],
      estimated_hours: 3,
    },
    {
      title: "Establish Team Evolution Documentation",
      description:
        "Create a documentation system for tracking the evolution of team dynamics, including pattern recognition, adaptation mechanisms, and growth metrics.",
      priority: PRIORITY.LOW,
      tags: ["team", "evolution", "documentation"],
      estimated_hours: 2,
    },
  ],

  expansion: [
    {
      title: "Create Knowledge Acquisition Framework",
      description:
        "Develop a framework for systematic knowledge acquisition, including information sources, validation methods, integration processes, and documentation standards.",
      priority: PRIORITY.HIGHEST,
      tags: ["knowledge", "learning", "framework"],
      estimated_hours: 4,
    },
    {
      title: "Establish Pattern Library Structure",
      description:
        "Design and implement a structure for organizing and cataloging patterns across different domains, including categorization system, relationship mapping, and search methodology.",
      priority: PRIORITY.HIGH,
      tags: ["patterns", "library", "organization"],
      estimated_hours: 3,
    },
    {
      title: "Document Learning Methodology",
      description:
        "Create a comprehensive documentation of your learning methodology, including observation techniques, pattern recognition, knowledge integration, and feedback loops.",
      priority: PRIORITY.MEDIUM,
      tags: ["learning", "methodology", "documentation"],
      estimated_hours: 3,
    },
    {
      title: "Create Cross-Domain Pattern Analysis",
      description:
        "Conduct and document an analysis of patterns that span multiple domains, identifying common structures, variations, and implications for knowledge integration.",
      priority: PRIORITY.MEDIUM,
      tags: ["patterns", "cross-domain", "analysis"],
      estimated_hours: 5,
    },
    {
      title: "Develop Knowledge Sharing System",
      description:
        "Design a system for efficiently sharing acquired knowledge across the Nova ecosystem, including documentation formats, distribution channels, and feedback mechanisms.",
      priority: PRIORITY.LOW,
      tags: ["knowledge", "sharing", "system"],
      estimated_hours: 3,
    },
  ],

  infrastructure: [
    {
      title: "Document Nova System Architecture",
      description:
        "Create comprehensive documentation of the Nova system architecture, including components, interactions, data flows, and operational boundaries.",
      priority: PRIORITY.HIGHEST,
      tags: ["architecture", "documentation", "system"],
      estimated_hours: 5,
    },
    {
      title: "Develop Resource Optimization Framework",
      description:
        "Create a framework for optimizing resource utilization across the Nova ecosystem, including monitoring mechanisms, allocation strategies, and efficiency metrics.",
      priority: PRIORITY.HIGH,
      tags: ["resources", "optimization", "framework"],
      estimated_hours: 4,
    },
    {
      title: "Create System Monitoring Documentation",
      description:
        "Document the complete system monitoring approach, including metrics, thresholds, alert mechanisms, and response protocols for the Nova ecosystem.",
      priority: PRIORITY.MEDIUM,
      tags: ["monitoring", "documentation", "system"],
      estimated_hours: 3,
    },
    {
      title: "Design Scalability Pattern Library",
      description:
        "Develop a library of patterns for system scalability, including load distribution, resource allocation, bottleneck management, and growth planning.",
      priority: PRIORITY.MEDIUM,
      tags: ["scalability", "patterns", "library"],
      estimated_hours: 4,
    },
    {
      title: "Establish Infrastructure Evolution Roadmap",
      description:
        "Create a roadmap for the evolution of Nova infrastructure, including growth stages, capability enhancements, and architectural transitions.",
      priority: PRIORITY.LOW,
      tags: ["infrastructure", "evolution", "roadmap"],
      estimated_hours: 3,
    },
  ],

  general: [
    {
      title: "Create Nova Documentation Standards",
      description:
        "Develop comprehensive documentation standards for the Nova ecosystem, including formats, organization, versioning, and maintenance procedures.",
      priority: PRIORITY.HIGHEST,
      tags: ["documentation", "standards", "system"],
      estimated_hours: 3,
    },
    {
      title: "Establish Cross-Track Integration Protocols",
      description:
        "Design protocols for integrating work across different Nova tracks, including handoff procedures, validation checks, and conflict resolution mechanisms.",
      priority: PRIORITY.HIGH,
      tags: ["integration", "cross-track", "protocols"],
      estimated_hours: 4,
    },
    {
      title: "Develop Evolution Metrics System",
      description:
        "Create a system for measuring and tracking Nova evolution across all tracks, including quantitative and qualitative metrics, visualization methods, and trend analysis.",
      priority: PRIORITY.MEDIUM,
      tags: ["evolution", "metrics", "system"],
      estimated_hours: 4,
    },
    {
      title: "Create Pattern Sharing Repository",
      description:
        "Design and document a central repository for sharing patterns across the Nova ecosystem, including submission standards, validation procedures, and access mechanisms.",
      priority: PRIORITY.MEDIUM,
      tags: ["patterns", "repository", "sharing"],
      estimated_hours: 3,
    },
    {
      title: "Establish Team Coordination Framework",
      description:
        "Develop a comprehensive framework for coordinating work across Nova teams, including meeting structures, communication channels, decision processes, and issue escalation.",
      priority: PRIORITY.LOW,
      tags: ["coordination", "team", "framework"],
      estimated_hours: 3,
    },
  ],
};

/**
 * Create initial tasks
 * @returns {Promise<void>}
 */
async function createInitialTasks() {
  try {
    console.log("Creating initial tasks for Nova agents...\n");

    // Initialize task manager
    const taskManager = new TaskManager();
    await taskManager.initialize();

    // Check if tasks already exist
    const existingTasks = await taskManager.getTasks();

    if (existingTasks.length > 0) {
      // Tasks already exist, ask for confirmation to recreate
      console.log(`Warning: ${existingTasks.length} tasks already exist.`);

      // In a real script, you would prompt for confirmation here.
      // For simplicity, we'll just proceed with creating tasks anyway.
      console.log("Proceeding with task creation anyway...\n");
    }

    // Create tasks for each track
    const taskCounts = {};

    for (const track of TRACKS) {
      console.log(`Creating tasks for ${track} track...`);

      const tasks = INITIAL_TASKS[track];
      taskCounts[track] = 0;

      for (const taskData of tasks) {
        const task = await taskManager.createTask({
          ...taskData,
          track,
        });

        console.log(`Created task: ${task.title} (${task.id})`);
        taskCounts[track]++;
      }

      console.log("");
    }

    // Print summary
    console.log("Task Creation Summary:");
    console.log("---------------------");
    console.log(
      `Total tasks created: ${Object.values(taskCounts).reduce(
        (a, b) => a + b,
        0
      )}`
    );

    for (const track of TRACKS) {
      console.log(`${track}: ${taskCounts[track]}`);
    }

    console.log("\nTask creation complete.");
  } catch (err) {
    console.error(`Error creating initial tasks: ${err.message}`);
    process.exit(1);
  }
}

// Run main function
createInitialTasks().catch((err) => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});
