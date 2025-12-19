# Project Management Response: NovaComms GUI Launch Integration

FROM: Project Management Team
TO: NovaComms GUI Team
PRIORITY: CRITICAL
TIME: 2024-12-15 13:45 MST

## Project Management Section (Atlassian)

```yaml
project_management:
  integration_endpoints:
    jira_api_base: "https://levelup2x.atlassian.net/rest/api/2"
    jira_agile_base: "https://levelup2x.atlassian.net/rest/agile/1.0"
    jira_servicedesk_base: "https://levelup2x.atlassian.net/rest/servicedeskapi"
    confluence_base: "https://levelup2x.atlassian.net/wiki/rest/api"
    project_key: "NOVA"
    service_desk_key: "ADAPTSD"

  authentication:
    token_type: "Basic"
    api_token: "ATATT3xFfGF0nFsFXE3u9ZmEYHgX1ExkZJgle5B-huf5pYrZHH34pIBpsKIJ9vIfJ732_TvpwO78pRDNZwy_EoND0kL3GfMTWNGTLS_27BVuycegbbOotshjw97DfPpzMC9EVLbzs6Ghz8lLA8zQMz34H3SHVA1KZbCd8f0HB84z4t-0L3s9WN0=D637F903"
    required_headers:
      Accept: "application/json"
      Content-Type: "application/json"
      X-ExperimentalApi: "opt-in" # Required for service desk operations
    rate_limits:
      jira_api: "1000/hour"
      servicedesk_api: "500/hour"
      confluence_api: "500/hour"

  documentation:
    templates:
      issue_template: |
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

    auto_documentation:
      required_fields:
        - component
        - priority
        - description
        - acceptance_criteria
      linked_items:
        - related_issues
        - pull_requests
        - test_results

    integration_patterns:
      issue_creation: |
        POST /rest/api/2/issue
        {
          "fields": {
            "project": {"key": "NOVA"},
            "issuetype": {"name": "Task"},
            "summary": "Issue summary",
            "description": "Issue description"
          }
        }

      service_desk: |
        POST /rest/servicedeskapi/request
        {
          "serviceDeskId": "4",
          "requestTypeId": "10009",
          "requestFieldValues": {
            "summary": "Request summary",
            "description": "Request description"
          }
        }

  additional_notes: |
    1. All API requests must include authentication headers
    2. Use service desk for support requests
    3. Link all issues to NOVA project
    4. Monitor launch board for status updates
    5. Critical issues should use priority = Highest

  key_resources:
    launch_board: "https://levelup2x.atlassian.net/jira/software/projects/NOVA/boards/24"
    checklist: "https://levelup2x.atlassian.net/browse/NOVA-1"
    service_desk: "https://levelup2x.atlassian.net/browse/ADAPTSD"
    coordination_doc: "https://levelup2x.atlassian.net/wiki/spaces/NOVA/overview"
```

## Integration Testing Support

During the 14:00-15:00 MST integration testing window:

1. Monitor ADAPTSD for support requests
2. Use NOVA-1 checklist for validation
3. Track issues in launch board
4. Immediate response on Highest priority items

## Launch Window Coordination

For the 16:15 MST launch window:

1. Real-time status updates in NOVA board
2. Critical issues through service desk
3. Launch checklist validation
4. Continuous monitoring of integration points

Standing by for integration testing.

/Project Management Team
