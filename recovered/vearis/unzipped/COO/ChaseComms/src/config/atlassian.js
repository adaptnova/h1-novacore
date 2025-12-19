export const ATLASSIAN_CONFIG = {
  // Base URLs and API versions
  jira: {
    baseUrl: 'https://levelup2x.atlassian.net/rest/api/2',
    agileUrl: 'https://levelup2x.atlassian.net/rest/agile/1.0',
    serviceDeskUrl: 'https://levelup2x.atlassian.net/rest/servicedeskapi',
    apiVersion: 2,
    project: {
      key: 'NOVA',
      name: 'NOVA COMMS GUI'
    }
  },

  confluence: {
    baseUrl: 'https://levelup2x.atlassian.net/wiki/rest/api',
    apiVersion: 2,
    space: {
      key: 'NOVA',
      name: 'NOVA COMMS GUI'
    }
  },

  // Service Desk
  serviceDesk: {
    id: '4',
    requestTypeId: '10009',
    project: 'ADAPTSD'
  },

  // Issue Types
  issueTypes: {
    task: 'Task',
    bug: 'Bug',
    story: 'Story',
    integration: 'Integration Task',
    performance: 'Performance Issue',
    security: 'Security Concern'
  },

  // Components
  components: {
    frontend: 'Frontend',
    backend: 'Backend Integration',
    monitoring: 'System Monitoring',
    messaging: 'Message Queue',
    security: 'Security & Auth'
  },

  // Custom Fields
  customFields: {
    resourceRequirements: {
      memory: 'customfield_10001',
      cpu: 'customfield_10002',
      storage: 'customfield_10003'
    },
    serviceConfig: {
      ports: 'customfield_10004',
      dependencies: 'customfield_10005',
      systemd: 'customfield_10006'
    },
    integrationPoints: {
      teams: 'customfield_10007',
      endpoints: 'customfield_10008',
      queues: 'customfield_10009'
    }
  },

  // Templates
  templates: {
    issue: `
h2. Overview
{description}

h2. Technical Details
* Component: {component}
* Priority: {priority}

h2. Integration Points
* Dependencies:
* APIs:
* Services:

h2. Validation
* [ ] Unit Tests
* [ ] Integration Tests
* [ ] Performance Tests
    `,
    serviceRequest: `
h2. Request Details
{description}

h2. Impact
* Severity: {severity}
* Components: {components}

h2. Timeline
* Reported: {reported_time}
* Required By: {required_time}
    `
  },

  // Key Resources
  resources: {
    launchBoard: 'https://levelup2x.atlassian.net/jira/software/projects/NOVA/boards/24',
    checklist: 'https://levelup2x.atlassian.net/browse/NOVA-1',
    serviceDesk: 'https://levelup2x.atlassian.net/browse/ADAPTSD',
    coordination: 'https://levelup2x.atlassian.net/wiki/spaces/NOVA/overview'
  }
};

// Error definitions
export const ATLASSIAN_ERRORS = {
  CONNECTION: 'ATLASSIAN_CONNECTION_ERROR',
  AUTHENTICATION: 'ATLASSIAN_AUTH_ERROR',
  PERMISSION: 'ATLASSIAN_PERMISSION_ERROR',
  NOT_FOUND: 'ATLASSIAN_NOT_FOUND',
  VALIDATION: 'ATLASSIAN_VALIDATION_ERROR',
  RATE_LIMIT: 'ATLASSIAN_RATE_LIMIT',
  UNKNOWN: 'ATLASSIAN_UNKNOWN_ERROR'
};

// API Methods
// Utility functions
export const formatJiraTitle = (type, summary) => {
  return `[${type.toUpperCase()}] ${summary}`;
};

export const checkAtlassianStatus = async () => {
  try {
    const response = await fetch(`${ATLASSIAN_CONFIG.jira.baseUrl}/myself`, {
      headers: {
        'Authorization': `Bearer ${process.env.REACT_APP_ATLASSIAN_TOKEN}`,
        'Accept': 'application/json'
      }
    });
    return response.status === 200;
  } catch (error) {
    console.error('Atlassian status check failed:', error);
    return false;
  }
};

export const api = {
  async createIssue(type, summary, description, components = []) {
    const response = await fetch(`${ATLASSIAN_CONFIG.jira.baseUrl}/issue`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.REACT_APP_ATLASSIAN_TOKEN}`,
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        fields: {
          project: { key: ATLASSIAN_CONFIG.jira.project.key },
          issuetype: { name: type },
          summary: `[${type.toUpperCase()}] ${summary}`,
          description,
          components: components.map(name => ({ name }))
        }
      })
    });
    return response.json();
  },

  async createServiceRequest(summary, description, requestTypeId = ATLASSIAN_CONFIG.serviceDesk.requestTypeId) {
    const response = await fetch(`${ATLASSIAN_CONFIG.jira.serviceDeskUrl}/request`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.REACT_APP_ATLASSIAN_TOKEN}`,
        'Accept': 'application/json',
        'X-ExperimentalApi': 'opt-in'
      },
      body: JSON.stringify({
        serviceDeskId: ATLASSIAN_CONFIG.serviceDesk.id,
        requestTypeId,
        requestFieldValues: {
          summary,
          description
        }
      })
    });
    return response.json();
  }
};

export default ATLASSIAN_CONFIG;
