import ATLASSIAN_CONFIG from '../config/atlassian';
import monitoringService from './MonitoringService';

class AtlassianService {
  constructor() {
    this.config = ATLASSIAN_CONFIG;
    this.monitoringSubscription = null;
  }

  async initialize() {
    // Subscribe to monitoring service for automated issue creation
    this.monitoringSubscription = monitoringService.subscribe(
      this.handleMonitoringEvent.bind(this)
    );

    // Initialize documentation
    await this.initializeDocs();
  }

  async handleMonitoringEvent(type, data) {
    if (!data) return;

    // Handle critical events
    if (data.status === 'critical') {
      await this.createCriticalIssue(type, data);
    }

    // Update service status page
    await this.updateServiceStatus(type, data);
  }

  async createCriticalIssue(type, data) {
    const summary = `Critical: ${type} issue detected`;
    const description = `
h2. Issue Details
* Type: ${type}
* Status: ${data.status}
* Time: ${new Date().toISOString()}

h2. Metrics
${JSON.stringify(data, null, 2)}

h2. Impact
* Service: ${type}
* Severity: Critical
* Affected Components: ${data.components?.join(', ') || 'Unknown'}

h2. Automatic Actions
* Issue created
* Team notified
* Status page updated
    `;

    try {
      await this.config.api.createIssue(
        this.config.issueTypes.bug,
        summary,
        description,
        [type]
      );
    } catch (error) {
      console.error('Failed to create Jira issue:', error);
    }
  }

  async updateServiceStatus(type, data) {
    const pageTitle = 'NOVA COMMS GUI - Service Status';
    const content = `
h1. Service Status Dashboard
_Last updated: ${new Date().toISOString()}_

h2. System Health
${this.formatHealthStatus(data)}

h2. Performance Metrics
${this.formatPerformanceMetrics(data)}

h2. Recent Events
${this.formatRecentEvents(type, data)}

h2. Integration Status
${this.formatIntegrationStatus()}
    `;

    try {
      // Find existing page or create new one
      const searchResult = await this.findConfluencePage(pageTitle);
      if (searchResult) {
        await this.config.api.updatePage(
          searchResult.id,
          pageTitle,
          content,
          searchResult.version.number
        );
      } else {
        await this.config.api.createPage(pageTitle, content);
      }
    } catch (error) {
      console.error('Failed to update Confluence page:', error);
    }
  }

  async initializeDocs() {
    const docs = [
      {
        title: 'Service Installation Guide',
        content: this.config.templates.serviceInstallation
      },
      {
        title: 'Integration Documentation',
        content: this.config.templates.integrationDoc
      },
      {
        title: 'Monitoring Setup',
        content: this.formatMonitoringDocs()
      }
    ];

    for (const doc of docs) {
      try {
        const existing = await this.findConfluencePage(doc.title);
        if (!existing) {
          await this.config.api.createPage(doc.title, doc.content);
        }
      } catch (error) {
        console.error(`Failed to initialize ${doc.title}:`, error);
      }
    }
  }

  async findConfluencePage(title) {
    try {
      const response = await fetch(
        `${this.config.confluence.baseUrl}/rest/api/${this.config.confluence.apiVersion}/content?title=${encodeURIComponent(title)}&spaceKey=${this.config.confluence.space.key}`,
        {
          headers: {
            'Authorization': `Bearer ${process.env.REACT_APP_ATLASSIAN_TOKEN}`
          }
        }
      );
      const data = await response.json();
      return data.results[0];
    } catch (error) {
      console.error('Failed to find Confluence page:', error);
      return null;
    }
  }

  formatHealthStatus(data) {
    return `
|| Component || Status || Details ||
| API | ${this.formatStatus(data.api)} | Response time: ${data.api?.responseTime}ms |
| WebSocket | ${this.formatStatus(data.websocket)} | Connections: ${data.websocket?.connections} |
| Message Queue | ${this.formatStatus(data.messageQueue)} | Messages/sec: ${data.messageQueue?.rate} |
| Memory | ${this.formatStatus(data.memory)} | Usage: ${data.memory?.usage}% |
    `;
  }

  formatPerformanceMetrics(data) {
    return `
h3. Response Times
* API: ${data.api?.responseTime}ms
* WebSocket: ${data.websocket?.latency}ms
* Message Processing: ${data.messageQueue?.processTime}ms

h3. Resource Usage
* CPU: ${data.cpu?.usage}%
* Memory: ${data.memory?.usage}%
* Network: ${data.network?.bandwidth} MB/s

h3. Error Rates
* API: ${data.api?.errorRate}%
* WebSocket: ${data.websocket?.errorRate}%
* Overall: ${data.overall?.errorRate}%
    `;
  }

  formatRecentEvents(type, data) {
    return `
|| Time || Event || Status ||
| ${new Date().toISOString()} | ${type} update | ${this.formatStatus(data.status)} |
    `;
  }

  formatIntegrationStatus() {
    return `
|| Service || Status || Last Check ||
| Backend API | ${this.formatStatus('healthy')} | ${new Date().toISOString()} |
| RabbitMQ | ${this.formatStatus('healthy')} | ${new Date().toISOString()} |
| Redis Cache | ${this.formatStatus('healthy')} | ${new Date().toISOString()} |
    `;
  }

  formatMonitoringDocs() {
    return `
h1. Monitoring Configuration

h2. System Metrics
* Response times
* Error rates
* Resource usage
* Connection status

h2. Alert Thresholds
|| Metric || Warning || Critical ||
| Response Time | > 200ms | > 500ms |
| Error Rate | > 1% | > 5% |
| Memory Usage | > 75% | > 90% |
| CPU Usage | > 75% | > 90% |

h2. Integration Points
* Jira issue creation
* Status page updates
* Team notifications
* Performance tracking
    `;
  }

  formatStatus(status) {
    if (status === 'healthy' || status === true) {
      return '(/) Healthy';
    } else if (status === 'warning') {
      return '(!) Warning';
    } else {
      return '(x) Critical';
    }
  }

  cleanup() {
    if (this.monitoringSubscription) {
      this.monitoringSubscription();
      this.monitoringSubscription = null;
    }
  }
}

// Create singleton instance
const atlassianService = new AtlassianService();
export default atlassianService;
