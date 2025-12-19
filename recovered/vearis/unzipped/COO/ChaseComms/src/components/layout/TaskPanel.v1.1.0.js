import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { COLORS } from '../../styles/GlobalStyles';
import { 
  ATLASSIAN_CONFIG, 
  formatJiraTitle, 
  ATLASSIAN_ERRORS,
  checkAtlassianStatus 
} from '../../config/atlassian';

const TaskPanelContainer = styled.div`
  width: ${props => props.$collapsed ? '50px' : '20%'};
  background: #000000;
  border-right: 1px solid ${COLORS.border};
  display: flex;
  flex-direction: column;
  height: 100%;
  transition: width 0.3s ease;
  position: relative;
  min-width: ${props => props.$collapsed ? '50px' : '250px'};
`;

const CollapseButton = styled.button`
  position: absolute;
  right: -12px;
  top: 20px;
  width: 24px;
  height: 24px;
  background: ${COLORS.primary};
  border: 1px solid ${COLORS.border};
  border-radius: 50%;
  color: ${COLORS.accent};
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: all 0.3s ease;

  &:hover {
    background: ${COLORS.secondary};
    border-color: ${COLORS.accent};
    box-shadow: 0 0 5px ${COLORS.accent};
  }
`;

const CollapsedContent = styled.div`
  writing-mode: vertical-rl;
  text-orientation: mixed;
  transform: rotate(180deg);
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${COLORS.accent};
  padding: 20px 0;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 2px;
  background: ${COLORS.primary};
`;

const SectionHeader = styled.div`
  padding: 10px 15px;
  background: ${COLORS.primary};
  border-bottom: 1px solid ${COLORS.border};
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease;
  
  &:hover {
    background: ${COLORS.secondary};
    border-bottom-color: ${COLORS.accent};
  }

  .arrow {
    color: ${COLORS.accent};
    font-size: 12px;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 204, 0, 0.1);
    border-radius: 3px;
    margin-right: 8px;
  }
`;

const SectionTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: ${COLORS.accent};
  font-size: 0.9em;
  font-weight: 500;
`;

const SectionContent = styled.div`
  background: ${COLORS.primary};
  overflow: hidden;
  transition: height 0.3s ease;
  height: ${props => props.$expanded ? 'auto' : '0'};
  display: ${props => props.$expanded ? 'block' : 'none'};
`;

const FilterSection = styled.div`
  padding: 10px;
  border-bottom: 1px solid ${COLORS.border};
  background: ${COLORS.primary};
`;

const FilterGroup = styled.div`
  margin-bottom: 8px;

  &:last-child {
    margin-bottom: 0;
  }
`;

const FilterLabel = styled.div`
  font-size: 0.8em;
  color: ${COLORS.textDim};
  margin-bottom: 4px;
`;

const Select = styled.select`
  width: 100%;
  padding: 8px;
  background: ${COLORS.secondary};
  border: 1px solid ${COLORS.border};
  color: ${COLORS.text};
  border-radius: 4px;
  margin-bottom: 5px;

  &:focus {
    border-color: ${COLORS.accent};
    box-shadow: 0 0 5px ${COLORS.accent};
    outline: none;
  }
`;

const TaskList = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 10px;

  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: ${COLORS.primary};
  }

  &::-webkit-scrollbar-thumb {
    background: ${COLORS.border};
    border-radius: 4px;
  }
`;

const TaskItem = styled.div`
  padding: 10px;
  margin: 5px 0;
  background: ${COLORS.primary};
  border: 1px solid ${props => {
    switch(props.$priority) {
      case 'high': return COLORS.error;
      case 'medium': return COLORS.warning;
      case 'low': return COLORS.success;
      default: return COLORS.border;
    }
  }};
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: ${COLORS.secondary};
    box-shadow: 0 0 5px ${COLORS.accent};
  }
`;

const TaskHeader = styled.div`
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 5px;
`;

const TaskTitle = styled.div`
  font-weight: 500;
`;

const TaskMeta = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 5px;
`;

const TeamTag = styled.span`
  background: ${COLORS.secondary};
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.8em;
  color: ${COLORS.accent};
`;

const StatusTag = styled.span`
  background: ${props => {
    switch(props.$status) {
      case 'in_progress': return 'rgba(0, 255, 255, 0.1)';
      case 'blocked': return 'rgba(255, 0, 0, 0.1)';
      case 'review': return 'rgba(255, 255, 0, 0.1)';
      default: return 'rgba(128, 128, 128, 0.1)';
    }
  }};
  color: ${props => {
    switch(props.$status) {
      case 'in_progress': return '#00FFFF';
      case 'blocked': return COLORS.error;
      case 'review': return COLORS.warning;
      default: return COLORS.textDim;
    }
  }};
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.8em;
`;

const JiraLink = styled.a`
  color: ${COLORS.accent};
  text-decoration: none;
  font-size: 0.8em;
  display: flex;
  align-items: center;
  gap: 4px;

  &:hover {
    text-decoration: underline;
  }
`;

const AddTaskButton = styled.button`
  margin: 10px;
  padding: 10px;
  background: ${COLORS.secondary};
  border: 1px solid ${COLORS.border};
  color: ${COLORS.text};
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  width: calc(100% - 20px);

  &:hover {
    border-color: ${COLORS.accent};
    box-shadow: 0 0 5px ${COLORS.accent};
  }
`;

const ErrorMessage = styled.div`
  padding: 10px;
  margin: 10px;
  background: rgba(255, 0, 0, 0.1);
  border: 1px solid ${COLORS.error};
  border-radius: 4px;
  color: ${COLORS.error};
  font-size: 0.9em;
`;

const ConnectionStatus = styled.div`
  padding: 8px 10px;
  background: ${props => props.$connected ? 'rgba(0, 204, 0, 0.1)' : 'rgba(255, 0, 0, 0.1)'};
  border-bottom: 1px solid ${props => props.$connected ? COLORS.success : COLORS.error};
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9em;
  color: ${props => props.$connected ? COLORS.success : COLORS.error};
`;

const SyncButton = styled.button`
  background: transparent;
  border: none;
  color: ${COLORS.accent};
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 5px;
  border-radius: 3px;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(0, 204, 0, 0.1);
  }

  .sync-icon {
    transition: transform 1s ease;
  }

  &:hover .sync-icon {
    transform: rotate(180deg);
  }
`;

const TaskPanel = ({ collapsed, onCollapse }) => {
  const [sections, setSections] = useState({
    filters: true,
    tasks: true
  });
  const [atlassianStatus, setAtlassianStatus] = useState({
    connected: true,
    error: null
  });

  useEffect(() => {
    const checkConnection = async () => {
      try {
        const status = await checkAtlassianStatus();
        setAtlassianStatus({
          connected: status.status === 'connected',
          error: null
        });
      } catch (error) {
        setAtlassianStatus({
          connected: false,
          error: error.message || ATLASSIAN_ERRORS.CONNECTION_FAILED
        });
      }
    };

    checkConnection();
    // Check connection status periodically
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  const toggleSection = (section) => {
    setSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const mockTasks = [
    {
      id: 'NOVA-1234',
      title: formatJiraTitle('Leads', 'Review System Architecture'),
      team: 'Leads',
      priority: 'high',
      status: 'in_progress',
      assignee: 'John Doe',
      description: 'Complete system architecture review for Nova field integration'
    },
    {
      id: 'NOVA-1235',
      title: formatJiraTitle('Orchestrators', 'Update Deployment Scripts'),
      team: 'Orchestrators',
      priority: 'medium',
      status: 'review',
      assignee: 'Jane Smith',
      description: 'Update deployment scripts for new system configuration'
    },
    {
      id: 'NOVA-1236',
      title: formatJiraTitle('Leads', 'Monitor System Health'),
      team: 'Leads',
      priority: 'low',
      status: 'blocked',
      assignee: 'Alice Johnson',
      description: 'Implement continuous monitoring for system health metrics'
    }
  ];

  if (collapsed) {
    return (
      <TaskPanelContainer $collapsed={collapsed}>
        <CollapseButton onClick={() => onCollapse(false)}>→</CollapseButton>
        <CollapsedContent>Tasks</CollapsedContent>
      </TaskPanelContainer>
    );
  }

  return (
    <TaskPanelContainer $collapsed={collapsed}>
      <CollapseButton onClick={() => onCollapse(true)}>←</CollapseButton>
      
      <ConnectionStatus $connected={atlassianStatus.connected}>
        <span>
          {atlassianStatus.connected 
            ? 'Connected to Jira' 
            : 'Jira Connection Failed'}
        </span>
        {atlassianStatus.connected && (
          <SyncButton onClick={() => checkAtlassianStatus()}>
            <span className="sync-icon">↻</span>
            Sync
          </SyncButton>
        )}
      </ConnectionStatus>

      {atlassianStatus.error && (
        <ErrorMessage>{atlassianStatus.error}</ErrorMessage>
      )}
      
      <SectionHeader onClick={() => toggleSection('filters')}>
        <SectionTitle>
          <span className="arrow">{sections.filters ? '▼' : '▶'}</span>
          <span>Filters</span>
        </SectionTitle>
      </SectionHeader>
      
      <SectionContent $expanded={sections.filters}>
        <FilterSection>
          <FilterGroup>
            <FilterLabel>Team</FilterLabel>
            <Select defaultValue="">
              <option value="">All Teams</option>
              <option value="leads">Leads</option>
              <option value="orchestrators">Orchestrators</option>
              <option value="monitoring">Monitoring</option>
            </Select>
          </FilterGroup>

          <FilterGroup>
            <FilterLabel>Priority</FilterLabel>
            <Select defaultValue="">
              <option value="">All Priorities</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </Select>
          </FilterGroup>

          <FilterGroup>
            <FilterLabel>Status</FilterLabel>
            <Select defaultValue="">
              <option value="">All Statuses</option>
              <option value="in_progress">In Progress</option>
              <option value="review">In Review</option>
              <option value="blocked">Blocked</option>
            </Select>
          </FilterGroup>
        </FilterSection>
      </SectionContent>

      <SectionHeader onClick={() => toggleSection('tasks')}>
        <SectionTitle>
          <span className="arrow">{sections.tasks ? '▼' : '▶'}</span>
          <span>Tasks</span>
        </SectionTitle>
      </SectionHeader>

      <SectionContent $expanded={sections.tasks}>
        <TaskList>
          {mockTasks.map(task => (
            <TaskItem key={task.id} $priority={task.priority}>
              <TaskHeader>
                <TaskTitle>{task.title}</TaskTitle>
              </TaskHeader>
              <TaskMeta>
                <TeamTag>{task.team}</TeamTag>
                <StatusTag $status={task.status}>
                  {task.status.replace('_', ' ')}
                </StatusTag>
              </TaskMeta>
              <JiraLink 
                href={`${ATLASSIAN_CONFIG.baseUrl}/browse/${task.id}`} 
                target="_blank"
                rel="noopener noreferrer"
              >
                {task.id} →
              </JiraLink>
            </TaskItem>
          ))}
        </TaskList>
        <AddTaskButton>+ Add Task</AddTaskButton>
      </SectionContent>
    </TaskPanelContainer>
  );
};

export default TaskPanel;
