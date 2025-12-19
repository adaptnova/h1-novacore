# ZeroPoint VSCodium Native Shell UI Specifications - Gorilla LLM Dual Setup
**Date:** April 3, 2025 1:48 AM MST  
**Author:** Vaeris, COO  
**Version:** 1.2.0

## Overview

This document provides detailed UI specifications for the Gorilla LLM dual setup integration in the ZeroPoint VSCodium native shell. It builds upon the previous UI specifications and focuses specifically on the UI elements needed to support the dual CPU/GPU setup described in `/data-nova/ax/RouteOps/api/kong/docs/dual_setup.md`.

## Gorilla LLM Dual Setup UI Components

### 1. Gorilla Explorer View Enhancements

**Purpose:** Provide visibility and control over both CPU and GPU Gorilla LLM models.

**Location:** Within the ZeroPoint Explorer view, under the Gorilla LLM section.

**Components:**
- **Model Selection Section:** Add a new section for selecting between CPU and GPU models.
  - CPU Model (Local)
  - GPU Model (Remote)
  - Auto (GorillaDualRouter)
- **Status Indicators:** Add status indicators for both CPU and GPU models.
  - Green: Available
  - Yellow: Busy
  - Red: Unavailable
- **Load Statistics:** Add load statistics for both CPU and GPU models.
  - CPU Usage
  - Memory Usage
  - Request Queue Length
  - Average Response Time

**Interactions:**
- Click on a model to select it for inference
- Right-click on a model to see available actions (restart, view logs, etc.)
- Hover over a status indicator to see detailed status information

### 2. Gorilla Playground Enhancements

**Purpose:** Provide an interactive interface for testing Gorilla LLM models with explicit model selection.

**Location:** Editor area, opened when a Gorilla LLM model is selected from the Explorer.

**Components:**
- **Model Selection Dropdown:** Add a dropdown for selecting between CPU, GPU, or Auto modes.
- **Model Parameters Section:** Add a section for configuring model parameters.
  - Temperature
  - Max Tokens
  - Top P
  - Frequency Penalty
  - Presence Penalty
- **Context Window:** Add a text area for providing context to the model.
- **Function Catalog Browser:** Add a browser for the available functions in the catalog.
- **Performance Metrics:** Add a section for displaying performance metrics.
  - Inference Time
  - Tokens Per Second
  - Memory Usage
  - Model Size

**Interactions:**
- Select a model from the dropdown
- Configure model parameters
- Enter a prompt in the input field
- Click "Execute" to run inference
- View results in the output field
- View performance metrics in the metrics section

### 3. Gorilla Dashboard

**Purpose:** Provide a comprehensive view of the Gorilla LLM dual setup performance and status.

**Location:** Editor area, opened when "Gorilla Dashboard" is selected from the Command Palette.

**Components:**
- **System Overview:** Add a section for displaying system overview.
  - CPU Model Status
  - GPU Model Status
  - GorillaDualRouter Status
  - Total Requests
  - Average Response Time
- **Request Distribution:** Add a chart for displaying request distribution between CPU and GPU models.
- **Performance Comparison:** Add a chart for comparing performance between CPU and GPU models.
- **Log Viewer:** Add a log viewer for viewing logs from both CPU and GPU models.
- **Redis Monitor:** Add a monitor for viewing Redis memory, logs, and load statistics.
- **NATS Monitor:** Add a monitor for viewing NATS notifications, heartbeats, and memory sync.

**Interactions:**
- Select a time range for the charts
- Filter logs by model, level, or keyword
- Click on a log entry to view details
- Click on a chart element to view details

### 4. Gorilla Configuration Editor

**Purpose:** Provide an interface for configuring the Gorilla LLM dual setup.

**Location:** Editor area, opened when "Gorilla Configuration" is selected from the Command Palette.

**Components:**
- **CPU Model Configuration:** Add a section for configuring the CPU model.
  - Model Path
  - Quantization Level
  - Thread Count
  - Memory Limit
- **GPU Model Configuration:** Add a section for configuring the GPU model.
  - Model Path
  - Precision (FP16/BF16)
  - Batch Size
  - Memory Limit
- **GorillaDualRouter Configuration:** Add a section for configuring the GorillaDualRouter.
  - Routing Rules
  - Failover Settings
  - Load Balancing Settings
- **Redis Configuration:** Add a section for configuring Redis integration.
- **NATS Configuration:** Add a section for configuring NATS integration.
- **Systemd Service Configuration:** Add a section for configuring systemd services.

**Interactions:**
- Edit configuration values
- Save configuration
- Apply configuration
- Restart services

## Command Palette Enhancements

Add new commands for the Gorilla LLM dual setup:

- `Gorilla: Select CPU Model`
- `Gorilla: Select GPU Model`
- `Gorilla: Select Auto Mode`
- `Gorilla: View Dashboard`
- `Gorilla: Edit Configuration`
- `Gorilla: View Logs`
- `Gorilla: Restart CPU Model`
- `Gorilla: Restart GPU Model`
- `Gorilla: Restart GorillaDualRouter`

## Status Bar Enhancements

Add new status bar items for the Gorilla LLM dual setup:

- **Gorilla Mode:** Display the current mode (CPU, GPU, or Auto)
- **Gorilla Status:** Display the status of the selected model
- **Gorilla Load:** Display the load of the selected model

## Integration with Existing Components

The Gorilla LLM dual setup UI components should integrate seamlessly with the existing ZeroPoint components:

1. **ZeroPoint Explorer:** The Gorilla LLM section should be enhanced with the dual setup components.
2. **ZeroPoint Command Palette:** The new commands should be added to the existing Command Palette.
3. **ZeroPoint Status Bar:** The new status bar items should be added to the existing Status Bar.
4. **ZeroPoint Method Panel:** The Method Panel should support the new Gorilla LLM dual setup methods.

## Example Mockups

### Gorilla Explorer View

```
ZeroPoint
├── Services
│   ├── Memory Service
│   ├── Data Service
│   ├── Lifecycle Service
│   └── Ops Service
├── Resources
│   ├── Quantum States
│   ├── Interference Patterns
│   └── Saved Configurations
├── Gorilla LLM
│   ├── Models
│   │   ├── CPU Model (Local) [Green]
│   │   ├── GPU Model (Remote) [Yellow]
│   │   └── Auto (GorillaDualRouter) [Green]
│   ├── Function Catalogs
│   │   ├── API Catalog
│   │   ├── Tool Catalog
│   │   └── Custom Catalog
│   └── Logs
│       ├── CPU Model Logs
│       ├── GPU Model Logs
│       └── GorillaDualRouter Logs
└── Recent Operations
```

### Gorilla Playground

```
┌─────────────────────────────────────────────────────────┐
│ Gorilla Playground                                       │
├─────────────────────────────────────────────────────────┤
│ Model: [CPU] [GPU] [Auto]                               │
│                                                          │
│ Parameters:                                              │
│   Temperature: [0.7]                                     │
│   Max Tokens: [1024]                                     │
│   Top P: [0.9]                                           │
│                                                          │
│ Context:                                                 │
│ [                                                        │
│   You are a helpful assistant that can use tools.        │
│ ]                                                        │
│                                                          │
│ Prompt:                                                  │
│ [                                                        │
│   How do I create a new file in VSCode?                  │
│ ]                                                        │
│                                                          │
│ [Execute]                                                │
├─────────────────────────────────────────────────────────┤
│ Result:                                                  │
│                                                          │
│ To create a new file in VSCode, you can use the          │
│ following methods:                                       │
│                                                          │
│ 1. Keyboard shortcut: Ctrl+N (Windows/Linux) or          │
│    Cmd+N (Mac)                                           │
│ 2. Menu: File > New File                                 │
│ 3. Explorer: Click the "New File" icon in the            │
│    Explorer view                                         │
│                                                          │
│ After creating the file, you'll need to save it with     │
│ Ctrl+S (Windows/Linux) or Cmd+S (Mac).                   │
│                                                          │
├─────────────────────────────────────────────────────────┤
│ Performance:                                             │
│   Model: CPU                                             │
│   Inference Time: 245ms                                  │
│   Tokens Per Second: 42                                  │
│   Memory Usage: 4.2GB                                    │
└───────────────────────────────────────────────────────────┘
```

## Conclusion

This document provides detailed UI specifications for the Gorilla LLM dual setup integration in the ZeroPoint VSCodium native shell. These specifications should be used in conjunction with the previous UI specifications to guide the implementation of the VSCodium native shell.

For more information or clarification, please contact Vaeris, COO, via the `coo.zeropoint.coordination` Redis stream.
