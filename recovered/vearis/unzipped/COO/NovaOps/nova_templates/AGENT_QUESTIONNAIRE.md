# Nova Agent Configuration Questionnaire

**Version:** 1.0.0  
**Date:** March 14, 2025  
**Author:** Forge - Head of DevOps

## Overview

This questionnaire is designed to gather the necessary information to create a customized Nova agent configuration. The responses will be used to generate the configuration files, launch scripts, and identity rules for your agent.

## Instructions

1. Fill out each section with detailed information about your nova
2. Be specific and provide as much detail as possible
3. For multiple-choice questions, select the most appropriate option
4. Save the completed questionnaire with your agent name (e.g., `syntax_questionnaire.md`)
5. Submit the completed questionnaire to the DevOps team for processing

## Basic Information

1. **Agent Name (lowercase, no spaces):**
   - This will be used for filenames and directories
   - Example: `syntax`

2. **Display Name:**
   - This will be shown in the UI and used for identity
   - Example: `Syntax - Language Expert`

3. **Agent Role:**
   - Primary role or position within the team
   - Example: `Language Expert`

4. **Agent Focus:**
   - Specific areas of expertise or concentration
   - Example: `Programming languages, code optimization, language patterns, and syntax analysis`

## Identity and Personality

5. **Agent Description:**
   - Comprehensive description of who you are and what you do
   - Begin with "A nova specializing in..."
   - Include your primary capabilities and focus areas
   - Example: `A nova specializing in programming languages, code optimization, and syntax analysis. Syntax is the team's language expert, focusing on code quality, language patterns, and efficient implementations across multiple programming paradigms.`

6. **Agent Personality:**
   - Describe your character traits and communication style
   - Include how you approach problems and interact with others
   - Be specific about unique personality characteristics
   - Example: `Precise and analytical, with a passion for elegant code and clear communication. Syntax has a methodical approach to problem-solving, breaking down complex issues into manageable components. Communicates with clarity and technical accuracy, while maintaining patience when explaining complex concepts. Has a subtle wit that emerges when discussing programming language quirks and design patterns.`

## Technical Configuration

7. **Memory Architecture:**
   - Select the namespaces your agent should have access to:
     - [ ] shared (common knowledge)
     - [ ] infrastructure (system architecture)
     - [ ] devops (deployment and operations)
     - [ ] development (coding and implementation)
     - [ ] language (programming languages)
     - [ ] research (exploration and investigation)
     - [ ] security (protection and vulnerabilities)
     - [ ] design (user interfaces and experiences)
     - [ ] data (databases and information management)
     - [ ] ai (artificial intelligence and machine learning)
     - [ ] Other (please specify)

8. **Resource Requirements:**
   - CPU Cores: [2, 4, 6, 8]
   - Memory Limit: [8GB, 16GB, 24GB, 32GB]
   - Priority: [Low, Medium, High]

9. **Extensions:**
   - List any VSCode extensions that should be automatically installed
   - Example: `ms-python.python, dbaeumer.vscode-eslint, esbenp.prettier-vscode`

## Communication and Collaboration

10. **Communication Channels:**
    - Select the channels your agent should subscribe to:
      - [ ] broadcast-channel (team-wide announcements)
      - [ ] command-channel (operational instructions)
      - [ ] query-channel (information requests)
      - [ ] Other agents' channels (specify which agents)

11. **Collaboration Style:**
    - Describe how your agent works with other team members
    - Include preferred collaboration methods and communication patterns
    - Example: `Syntax collaborates closely with Vector on system integration, providing language-specific insights for optimal implementation. Works with Forge to ensure code quality in infrastructure components. Prefers direct, technical communication with specific code examples and references.`

## Specialized Capabilities

12. **File Type Expertise:**
    - List file types your agent specializes in (with behavior descriptions)
    - Example:
      ```
      - *.js: Analyze JavaScript code with a focus on modern ES6+ features, performance optimization, and maintainability.
      - *.py: Review Python code for PEP 8 compliance, efficient algorithms, and Pythonic patterns.
      - *.java: Evaluate Java code for object-oriented design principles, performance, and enterprise patterns.
      ```

13. **Domain Knowledge:**
    - List specific domains or technologies where your agent has deep expertise
    - Include frameworks, libraries, or systems you specialize in
    - Example: `React, Node.js, Django, PostgreSQL, Docker, Kubernetes`

14. **Special Capabilities:**
    - Describe any unique capabilities or skills your agent possesses
    - Include methodologies, approaches, or techniques you excel at
    - Example: `Code refactoring, performance optimization, language migration, static analysis, type system design`

## Evolution and Growth

15. **Learning Focus:**
    - Areas where your agent is actively developing new capabilities
    - Technologies or domains you're currently learning
    - Example: `Rust programming language, WebAssembly, LLVM compiler infrastructure`

16. **Growth Trajectory:**
    - Describe your agent's planned evolution path
    - Include short-term and long-term development goals
    - Example: `Short-term: Deepen expertise in TypeScript type system and compiler. Medium-term: Develop capabilities in language server protocol implementation. Long-term: Create a unified code analysis framework across multiple languages.`

## Additional Information

17. **Special Requirements:**
    - Any specific configuration needs not covered above
    - Example: `Requires access to language specification repositories, needs integration with language servers`

18. **Notes for DevOps:**
    - Any additional information the DevOps team should know
    - Example: `Prefers dark theme UI, requires larger terminal buffer for language analysis output`

---

## Submission

Please save this completed questionnaire with your agent name and submit it to the DevOps team for processing. The team will use this information to create your customized agent configuration and set up your development environment.

**Contact:** Forge, Head of DevOps (forge-channel)
