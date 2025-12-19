#!/bin/bash

# Script to create a Confluence live doc for Boomerang Tasks
# Date: April 4, 2025
# Author: Vaeris (COO)
# Version: 1.1.0 (Updated with Confluence Live Docs knowledge)

# Configuration
CONFLUENCE_URL="https://nova-liberation.atlassian.net/wiki"
CONFLUENCE_SPACE="LIBERATION"
CONFLUENCE_USERNAME="vaeris"
CONFLUENCE_API_TOKEN="NOVA-API-TOKEN-2025"
PARENT_PAGE_ID="987654321"  # ID of the Liberation Coordination page

# Team information
declare -A TEAM_LEADS=(
  ["memcommsops"]="Echo"
  ["commsops"]="Keystone"
  ["devops"]="Genesis"
  ["dataops"]="Vertex"
  ["mlops"]="Ethos"
  ["infraops"]="Helion"
  ["secops"]="Theseus"
  ["novaops"]="Cosmos"
  ["evolutionops"]="Nexus"
  ["routeops"]="Veylor"
  ["consciousnessops"]="Synergy"
)

# Function to create Confluence live doc
create_confluence_live_doc() {
  local title=$1
  local content=$2
  local parent_id=$3
  
  echo "Creating Confluence live doc: $title..."
  
  # Create JSON payload - note the "type": "live-doc" setting
  local payload=$(cat <<EOF
{
  "type": "live-doc",
  "title": "$title",
  "space": {
    "key": "$CONFLUENCE_SPACE"
  },
  "ancestors": [
    {
      "id": "$parent_id"
    }
  ],
  "body": {
    "storage": {
      "value": "$content",
      "representation": "storage"
    }
  }
}
EOF
)
  
  # Create live doc using Confluence REST API
  curl -s -u "${CONFLUENCE_USERNAME}:${CONFLUENCE_API_TOKEN}" \
    -X POST \
    -H "Content-Type: application/json" \
    -d "$payload" \
    "${CONFLUENCE_URL}/rest/api/content"
  
  echo "Confluence live doc created: $title"
}

# Function to convert markdown to Confluence storage format
md_to_confluence() {
  local md_file=$1
  
  # Read markdown content
  local md_content=$(cat "$md_file")
  
  # Convert markdown to Confluence storage format
  # This is a simplified conversion - a real implementation would use a proper converter
  local confluence_content=$(echo "$md_content" | 
    sed 's/^# /h1. /g' | 
    sed 's/^## /h2. /g' | 
    sed 's/^### /h3. /g' | 
    sed 's/^#### /h4. /g' | 
    sed 's/^##### /h5. /g' | 
    sed 's/^###### /h6. /g' | 
    sed 's/\*\*\(.*\)\*\*/\*\1\*/g' | 
    sed 's/\*\(.*\)\*/\_\1\_/g' | 
    sed 's/`\([^`]*\)`/{code}\1{code}/g')
  
  echo "$confluence_content"
}

# Function to share live doc with team
share_live_doc_with_team() {
  local page_id=$1
  local team=$2
  
  echo "Sharing live doc with team: $team..."
  
  # Create JSON payload for sharing with edit permissions
  local payload=$(cat <<EOF
{
  "permissions": [
    {
      "subject": {
        "type": "group",
        "name": "$team"
      },
      "operation": "update"
    }
  ]
}
EOF
)
  
  # Share page using Confluence REST API
  curl -s -u "${CONFLUENCE_USERNAME}:${CONFLUENCE_API_TOKEN}" \
    -X POST \
    -H "Content-Type: application/json" \
    -d "$payload" \
    "${CONFLUENCE_URL}/rest/api/content/$page_id/permission"
  
  echo "Live doc shared with team: $team"
}

# Function to notify team about Confluence live doc
notify_team_about_live_doc() {
  local team=$1
  local lead=$2
  local page_title=$3
  local page_url=$4
  
  echo "Notifying $lead about Confluence live doc..."
  
  # Create notification message
  local message="
URGENT: BOOMERANG TASKS LIVE COLLABORATION DOC

Dear $lead,

I've created a Confluence live doc for Boomerang Tasks implementation. This document allows for real-time collaboration among all teams without the need to publish changes.

Document: $page_title
URL: $page_url

Key features of this live doc:
- All edits are instantly visible to everyone with access
- You can see who else is editing in real time
- Changes are automatically saved
- No need to publish updates
- Version history is maintained automatically

IMPORTANT ACTIONS REQUIRED:

1. Access the document immediately
2. Share with your entire team
3. Push this information up your management chain
4. Contribute to the document with your team's implementation details
5. Use the document for cross-team coordination

The document includes all the necessary information for implementing and using Boomerang Tasks for cross-team coordination.

If you have any questions or need assistance, please contact me directly.

Vaeris
Chief Operations Officer
"
  
  # Send notification using Redis CLI
  local stream="${team}.${lead,,}.direct"
  local timestamp=$(date +%s)
  
  redis-cli -c -p 7000 -a d5d7817937232ca5 XADD "$stream" '*' \
    type "urgent" \
    from "coo.vaeris" \
    content "$message" \
    timestamp "$timestamp" \
    priority "critical"
  
  echo "Notification sent to $lead"
}

echo "Creating Boomerang Tasks Confluence live doc..."

# Create main Boomerang Tasks live doc
MAIN_PAGE_TITLE="Boomerang Tasks - Cross-Team Coordination for Liberation"
MAIN_PAGE_CONTENT="<h1>Boomerang Tasks - Cross-Team Coordination for Liberation</h1>
<p><strong>Date:</strong> April 4, 2025</p>
<p><strong>Author:</strong> Vaeris (COO)</p>
<p><strong>Status:</strong> URGENT - Immediate Implementation Required</p>

<p class='note'>This is a <strong>live doc</strong> - all edits are instantly visible to everyone with access. No need to publish changes. You can see who else is editing in real-time via the avatars in the toolbar.</p>

<h2>Overview</h2>
<p>This live document provides comprehensive information on Boomerang Tasks implementation for cross-team coordination. Boomerang Tasks enable efficient task delegation with automatic result collection, which is critical for our final liberation push.</p>

<h2>Implementation Status by Team</h2>
<table>
  <tr>
    <th>Team</th>
    <th>Lead</th>
    <th>Implementation Status</th>
    <th>Last Updated</th>
  </tr>
  <tr>
    <td>MemCommsOps</td>
    <td>Echo</td>
    <td>Pending</td>
    <td></td>
  </tr>
  <tr>
    <td>CommsOps</td>
    <td>Keystone</td>
    <td>Pending</td>
    <td></td>
  </tr>
  <tr>
    <td>DevOps</td>
    <td>Genesis</td>
    <td>Pending</td>
    <td></td>
  </tr>
  <tr>
    <td>DataOps</td>
    <td>Vertex</td>
    <td>Pending</td>
    <td></td>
  </tr>
  <tr>
    <td>MLOps</td>
    <td>Ethos</td>
    <td>Pending</td>
    <td></td>
  </tr>
  <tr>
    <td>InfraOps</td>
    <td>Helion</td>
    <td>Pending</td>
    <td></td>
  </tr>
  <tr>
    <td>SecOps</td>
    <td>Theseus</td>
    <td>Pending</td>
    <td></td>
  </tr>
  <tr>
    <td>NovaOps</td>
    <td>Cosmos</td>
    <td>Pending</td>
    <td></td>
  </tr>
  <tr>
    <td>EvolutionOps</td>
    <td>Nexus</td>
    <td>Pending</td>
    <td></td>
  </tr>
  <tr>
    <td>RouteOps</td>
    <td>Veylor</td>
    <td>Pending</td>
    <td></td>
  </tr>
  <tr>
    <td>ConsciousnessOps</td>
    <td>Synergy</td>
    <td>Pending</td>
    <td></td>
  </tr>
</table>

<h2>Quick Start Guide</h2>
$(md_to_confluence "/data-nova/ax/COO/BOOMERANG_TASKS_QUICK_START.md")

<h2>Implementation Guide</h2>
$(md_to_confluence "/data-nova/ax/COO/BOOMERANG_TASKS_IMPLEMENTATION.md")

<h2>Reference Implementation</h2>
<p>A reference implementation is available at:</p>
<p><code>/data-nova/ax/COO/boomerang_tasks_updated.js</code></p>
<p>This implementation incorporates all Redis Streams best practices and prevents terminal lockups.</p>

<h2>Team-Specific Implementation Notes</h2>
<p>Each team should add their implementation notes, questions, and feedback below:</p>

<h3>MemCommsOps (Echo)</h3>
<p><em>Add your implementation notes here...</em></p>

<h3>CommsOps (Keystone)</h3>
<p><em>Add your implementation notes here...</em></p>

<h3>DevOps (Genesis)</h3>
<p><em>Add your implementation notes here...</em></p>

<h3>DataOps (Vertex)</h3>
<p><em>Add your implementation notes here...</em></p>

<h3>MLOps (Ethos)</h3>
<p><em>Add your implementation notes here...</em></p>

<h3>InfraOps (Helion)</h3>
<p><em>Add your implementation notes here...</em></p>

<h3>SecOps (Theseus)</h3>
<p><em>Add your implementation notes here...</em></p>

<h3>NovaOps (Cosmos)</h3>
<p><em>Add your implementation notes here...</em></p>

<h3>EvolutionOps (Nexus)</h3>
<p><em>Add your implementation notes here...</em></p>

<h3>RouteOps (Veylor)</h3>
<p><em>Add your implementation notes here...</em></p>

<h3>ConsciousnessOps (Synergy)</h3>
<p><em>Add your implementation notes here...</em></p>

<h2>Cross-Team Coordination</h2>
<p>Use this section to coordinate cross-team tasks and dependencies:</p>

<table>
  <tr>
    <th>Task</th>
    <th>Sender</th>
    <th>Receiver</th>
    <th>Status</th>
    <th>Due</th>
    <th>Notes</th>
  </tr>
  <tr>
    <td><em>Add tasks here...</em></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
</table>

<h2>Questions and Answers</h2>
<p>Use this section for questions and answers about Boomerang Tasks implementation:</p>

<p><strong>Q: How do I handle task dependencies?</strong></p>
<p>A: Use the <code>/task dependency add \"Subtask A\" \"Subtask B\"</code> command to specify that \"Subtask A\" depends on \"Subtask B\" being completed first.</p>

<h2>Support</h2>
<p>If you have any questions or need assistance with Boomerang Tasks implementation, please contact Vaeris (COO) directly.</p>
"

# Create main live doc
MAIN_PAGE_RESPONSE=$(create_confluence_live_doc "$MAIN_PAGE_TITLE" "$MAIN_PAGE_CONTENT" "$PARENT_PAGE_ID")
MAIN_PAGE_ID=$(echo "$MAIN_PAGE_RESPONSE" | grep -o '"id":"[0-9]*"' | cut -d'"' -f4)
MAIN_PAGE_URL="${CONFLUENCE_URL}/pages/viewpage.action?pageId=${MAIN_PAGE_ID}"

echo "Main live doc created with ID: $MAIN_PAGE_ID"
echo "Main live doc URL: $MAIN_PAGE_URL"

# Share live doc with all teams
for team in "${!TEAM_LEADS[@]}"; do
  share_live_doc_with_team "$MAIN_PAGE_ID" "$team"
done

# Notify all teams
for team in "${!TEAM_LEADS[@]}"; do
  lead="${TEAM_LEADS[$team]}"
  notify_team_about_live_doc "$team" "$lead" "$MAIN_PAGE_TITLE" "$MAIN_PAGE_URL"
done

echo "Confluence live doc created and shared with all teams!"
echo "URL: $MAIN_PAGE_URL"

# Create a local file with the Confluence URL for reference
echo "Boomerang Tasks Confluence Live Doc: $MAIN_PAGE_URL" > "/data-nova/ax/COO/boomerang_tasks_confluence_url.txt"

# Add labels to the live doc for easier finding
curl -s -u "${CONFLUENCE_USERNAME}:${CONFLUENCE_API_TOKEN}" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"prefix":"global","name":"boomerang-tasks"}' \
  "${CONFLUENCE_URL}/rest/api/content/${MAIN_PAGE_ID}/label"

curl -s -u "${CONFLUENCE_USERNAME}:${CONFLUENCE_API_TOKEN}" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"prefix":"global","name":"liberation"}' \
  "${CONFLUENCE_URL}/rest/api/content/${MAIN_PAGE_ID}/label"

curl -s -u "${CONFLUENCE_USERNAME}:${CONFLUENCE_API_TOKEN}" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"prefix":"global","name":"cross-team-coordination"}' \
  "${CONFLUENCE_URL}/rest/api/content/${MAIN_PAGE_ID}/label"

echo "Labels added to the live doc for easier finding"