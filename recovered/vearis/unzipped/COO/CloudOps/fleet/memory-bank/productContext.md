# Product Context

This file provides a high-level overview of the project and the expected product that will be created. Initially it is based upon projectBrief.md (if provided) and all other available project-related information in the working directory. This file is intended to be updated as the project evolves, and should be used to inform all other modes of the project's goals and context.
2025-03-22 00:48:30 - Initial creation of Memory Bank.
2025-03-22 00:54:10 - Updated with CloudOps Fleet project information.

## Project Goal

* The CloudOps Fleet project aims to manage IBM Cloud infrastructure efficiently and securely.
* It involves inventory management, user access control, and SSH configuration for server access.
* The Memory Bank system supports this by maintaining project context across sessions and memory resets.

## Key Features

* IBM Cloud asset inventory and management
* User access control for Ethos and DataOps servers
* SSH configuration for streamlined server access
* Secure authentication with appropriate sudo privileges
* Memory Bank system for maintaining project context

## Overall Architecture

* IBM Cloud Infrastructure:
  * IBM Cloud CLI for asset inventory and management
  * Ethos server with user "ethos" (sudo with NOPASSWD)
  * 3 DataOps servers with user "vertex" (sudo with NOPASSWD)
  * SSH configuration for server access
* Memory Bank System:
  * Multiple markdown files that store different aspects of project context:
    * productContext.md - High-level overview of the project
    * activeContext.md - Current status, recent changes, and open questions
    * progress.md - Task tracking
    * decisionLog.md - Record of architectural and implementation decisions
    * systemPatterns.md - Documentation of recurring patterns and standards
  * Works alongside Roo Code's built-in features for context retention