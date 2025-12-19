#!/usr/bin/env node

const fetch = require('node-fetch');
const colors = require('colors/safe');

// Configuration
const config = {
  jira: {
    baseUrl: process.env.REACT_APP_ATLASSIAN_URL,
    project: 'NOVACOMM'
  },
  confluence: {
    baseUrl: `${process.env.REACT_APP_ATLASSIAN_URL}/wiki`,
    space: 'NOVACOMM'
  },
  auth: {
    token: process.env.REACT_APP_ATLASSIAN_TOKEN
  }
};

// Utility functions
const log = {
  info: (msg) => console.log(colors.blue('INFO: ') + msg),
  success: (msg) => console.log(colors.green('SUCCESS: ') + msg),
  error: (msg) => console.log(colors.red('ERROR: ') + msg),
  warning: (msg) => console.log(colors.yellow('WARNING: ') + msg)
};

const formatResponse = (response) => {
  return `Status: ${response.status}\nBody: ${JSON.stringify(response.data, null, 2)}`;
};

// Verification functions
async function verifyJiraConnection() {
  log.info('Verifying Jira connection...');
  
  try {
    const response = await fetch(`${config.jira.baseUrl}/rest/api/3/project/${config.jira.project}`, {
      headers: {
        'Authorization': `Bearer ${config.auth.token}`,
        'Accept': 'application/json'
      }
    });

    const data = await response.json();
    
    if (response.ok) {
      log.success('Jira connection verified');
      return { status: response.status, data };
    } else {
      throw new Error(`Failed to connect to Jira: ${data.message}`);
    }
  } catch (error) {
    log.error(`Jira connection failed: ${error.message}`);
    throw error;
  }
}

async function verifyConfluenceConnection() {
  log.info('Verifying Confluence connection...');
  
  try {
    const response = await fetch(`${config.confluence.baseUrl}/rest/api/space/${config.confluence.space}`, {
      headers: {
        'Authorization': `Bearer ${config.auth.token}`,
        'Accept': 'application/json'
      }
    });

    const data = await response.json();
    
    if (response.ok) {
      log.success('Confluence connection verified');
      return { status: response.status, data };
    } else {
      throw new Error(`Failed to connect to Confluence: ${data.message}`);
    }
  } catch (error) {
    log.error(`Confluence connection failed: ${error.message}`);
    throw error;
  }
}

async function verifyIssueCreation() {
  log.info('Testing issue creation...');
  
  try {
    const response = await fetch(`${config.jira.baseUrl}/rest/api/3/issue`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${config.auth.token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        fields: {
          project: { key: config.jira.project },
          summary: 'Test Issue - Verify Integration',
          description: 'This is a test issue created by the verification script.',
          issuetype: { name: 'Task' }
        }
      })
    });

    const data = await response.json();
    
    if (response.ok) {
      log.success(`Test issue created: ${data.key}`);
      return { status: response.status, data };
    } else {
      throw new Error(`Failed to create test issue: ${data.message}`);
    }
  } catch (error) {
    log.error(`Issue creation failed: ${error.message}`);
    throw error;
  }
}

async function verifyConfluencePageCreation() {
  log.info('Testing Confluence page creation...');
  
  try {
    const response = await fetch(`${config.confluence.baseUrl}/rest/api/content`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${config.auth.token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        type: 'page',
        title: 'Test Page - Verify Integration',
        space: { key: config.confluence.space },
        body: {
          storage: {
            value: 'This is a test page created by the verification script.',
            representation: 'storage'
          }
        }
      })
    });

    const data = await response.json();
    
    if (response.ok) {
      log.success(`Test page created: ${data.id}`);
      return { status: response.status, data };
    } else {
      throw new Error(`Failed to create test page: ${data.message}`);
    }
  } catch (error) {
    log.error(`Page creation failed: ${error.message}`);
    throw error;
  }
}

// Main verification
async function verifyAtlassianIntegration() {
  log.info('Starting Atlassian integration verification...');
  console.log('----------------------------------------');

  try {
    // Verify connections
    const jiraConn = await verifyJiraConnection();
    console.log('\nJira Connection:', formatResponse(jiraConn));

    const confluenceConn = await verifyConfluenceConnection();
    console.log('\nConfluence Connection:', formatResponse(confluenceConn));

    // Test functionality
    const issue = await verifyIssueCreation();
    console.log('\nIssue Creation:', formatResponse(issue));

    const page = await verifyConfluencePageCreation();
    console.log('\nPage Creation:', formatResponse(page));

    log.success('\nAll verifications completed successfully!');
    process.exit(0);
  } catch (error) {
    log.error('\nVerification failed!');
    console.error(error);
    process.exit(1);
  }
}

// Run verification
verifyAtlassianIntegration();
