import React, { useState, useCallback, useEffect } from 'react';
import styled from 'styled-components';
import GlobalStyles, { COLORS } from './styles/GlobalStyles';
import Header from './components/layout/Header';
import TaskPanel from './components/layout/TaskPanel';
import CollaborationPanel from './components/layout/CollaborationPanel';
import AIOutputPanel from './components/layout/AIOutputPanel';
import monitoringService from './services/MonitoringService';
import atlassianService from './services/AtlassianService';

const AppContainer = styled.div`
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: ${COLORS.background};
  color: ${COLORS.text};
`;

const MainContent = styled.main`
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
  background: ${COLORS.background};

  // Thin lines between panels
  > * + * {
    border-left: 1px solid ${COLORS.border};
  }
`;

const CollabPanelWrapper = styled.div`
  flex: 1;
  min-width: 0;
  z-index: 1;
  display: flex;
  flex-direction: column;
  background: ${COLORS.background};
  transition: all 0.3s ease;
`;

const SidePanel = styled.div`
  position: relative;
  z-index: 2;
  background: ${COLORS.background};
  transition: all 0.3s ease;
  width: ${props => props.$collapsed ? '50px' : '300px'};

  &.collapsed {
    cursor: pointer;

    &:hover {
      background: ${COLORS.border};

      &::after {
        content: '';
        position: absolute;
        inset: 0;
        border: 1px solid ${COLORS.accent};
        opacity: 0.3;
        pointer-events: none;
      }
    }
  }
`;

const RightPanelContainer = styled.div`
  display: flex;
  width: ${props => props.$collapsed ? '50px' : '600px'};
  transition: all 0.3s ease;
  background: ${COLORS.background};
  border-left: 1px solid ${COLORS.border};
  position: relative;

  > * {
    flex: 1;
    min-width: 0;
    border-left: 1px solid ${COLORS.border};

    &:first-child {
      border-left: none;
    }
  }

  ${props => props.$collapsed && `
    > * {
      border-left: none;
    }
  `}
`;

const CollapseButton = styled.button`
  position: absolute;
  top: 50%;
  left: -12px;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  border-radius: 12px;
  background: ${COLORS.background};
  border: 1px solid ${COLORS.border};
  color: ${COLORS.text};
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: all 0.2s ease;

  &:hover {
    background: ${COLORS.border};
    border-color: ${COLORS.accent};
    box-shadow: none;
  }

  &:focus {
    outline: none;
    box-shadow: none;
  }

  &::before {
    content: '${props => props.$collapsed ? '>' : '<'}';
    font-size: 12px;
  }
`;

function App() {
  const [taskPanelCollapsed, setTaskPanelCollapsed] = useState(false);
  const [aiPanelCollapsed, setAIPanelCollapsed] = useState(false);

  const handleTaskPanelDoubleClick = useCallback(() => {
    if (taskPanelCollapsed) {
      setTaskPanelCollapsed(false);
    }
  }, [taskPanelCollapsed]);

  useEffect(() => {
    // Initialize services
    const initializeServices = async () => {
      try {
        await monitoringService.initialize();
        await atlassianService.initialize();
        console.log('Services initialized successfully');
      } catch (error) {
        console.error('Service initialization failed:', error);
      }
    };

    initializeServices();

    // Cleanup on unmount
    return () => {
      monitoringService.cleanup();
      atlassianService.cleanup();
    };
  }, []);

  return (
    <AppContainer>
      <GlobalStyles />
      <Header />
      <MainContent>
        <SidePanel
          className={taskPanelCollapsed ? 'collapsed' : ''}
          onDoubleClick={handleTaskPanelDoubleClick}
          $collapsed={taskPanelCollapsed}
        >
          <TaskPanel
            collapsed={taskPanelCollapsed}
            onCollapse={setTaskPanelCollapsed}
          />
        </SidePanel>

        <CollabPanelWrapper>
          <CollaborationPanel />
        </CollabPanelWrapper>

        <RightPanelContainer $collapsed={aiPanelCollapsed}>
          <CollapseButton
            onClick={() => setAIPanelCollapsed(!aiPanelCollapsed)}
            $collapsed={aiPanelCollapsed}
          />
          <AIOutputPanel
            collapsed={aiPanelCollapsed}
            type="model"
          />
          <AIOutputPanel
            collapsed={aiPanelCollapsed}
            type="backend"
          />
        </RightPanelContainer>
      </MainContent>
    </AppContainer>
  );
}

export default App;
