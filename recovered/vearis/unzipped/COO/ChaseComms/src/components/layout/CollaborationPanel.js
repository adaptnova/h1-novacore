import React, { useState } from 'react';
import styled, { keyframes } from 'styled-components';
import { COLORS } from '../../styles/GlobalStyles';

const quantumPulse = keyframes`
  0% {
    transform: scale(1) rotate(0deg);
    filter: brightness(1) saturate(1);
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
  }
  50% {
    transform: scale(1.1) rotate(180deg);
    filter: brightness(1.3) saturate(1.5);
    box-shadow: 0 0 40px rgba(0, 255, 0, 0.5),
                0 0 60px rgba(0, 255, 0, 0.3),
                0 0 80px rgba(0, 255, 0, 0.2);
  }
  100% {
    transform: scale(1) rotate(360deg);
    filter: brightness(1) saturate(1);
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
  }
`;

const plasmaField = keyframes`
  0% {
    background-position: 0% 0%;
    filter: hue-rotate(0deg) brightness(1);
    opacity: 0.5;
  }
  50% {
    background-position: 100% 100%;
    filter: hue-rotate(180deg) brightness(1.3);
    opacity: 0.8;
  }
  100% {
    background-position: 0% 0%;
    filter: hue-rotate(360deg) brightness(1);
    opacity: 0.5;
  }
`;

const energyBurst = keyframes`
  0% {
    transform: scale(1);
    opacity: 0;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.5;
  }
  100% {
    transform: scale(1);
    opacity: 0;
  }
`;

const PanelContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background: ${COLORS.background};
`;

const TeamSelector = styled.div`
  padding: 10px;
  border-bottom: 1px solid ${COLORS.border};
`;

const Select = styled.select`
  width: 100%;
  padding: 8px;
  background: ${COLORS.background};
  color: ${COLORS.text};
  border: 1px solid ${COLORS.border};
  border-radius: 4px;

  &:focus {
    border-color: ${COLORS.accent};
    outline: none;
  }
`;

const ChatArea = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const MessageList = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: ${COLORS.background};
  }

  &::-webkit-scrollbar-thumb {
    background: ${COLORS.border};
    border-radius: 3px;
  }
`;

const Message = styled.div`
  padding: 10px;
  border-radius: 4px;
  background: ${props => props.$isSystem ? 'rgba(0, 204, 0, 0.1)' : COLORS.surface};
  border: 1px solid ${props => props.$isSystem ? COLORS.success : COLORS.border};

  .header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
    font-size: 0.9em;
  }

  .sender {
    color: ${COLORS.accent};
    font-weight: 500;
  }

  .time {
    color: ${COLORS.textDim};
  }

  .content {
    color: ${COLORS.text};
  }
`;

const InputArea = styled.div`
  padding: 15px;
  border-top: 1px solid ${COLORS.border};
  display: flex;
  gap: 10px;
`;

const Input = styled.textarea`
  flex: 1;
  padding: 10px;
  background: ${COLORS.background};
  color: ${COLORS.text};
  border: 1px solid ${COLORS.border};
  border-radius: 4px;
  resize: none;
  min-height: 60px;

  &:focus {
    border-color: ${COLORS.accent};
    outline: none;
  }
`;

const SendButton = styled.button`
  padding: 0 20px;
  background: ${COLORS.accent};
  color: ${COLORS.background};
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${COLORS.accentHover};
  }

  &:disabled {
    background: ${COLORS.border};
    cursor: not-allowed;
  }
`;

const CollaborationPanel = () => {
  const [selectedTeam, setSelectedTeam] = useState('all');
  const [message, setMessage] = useState('');
  const [messages] = useState([
    {
      id: 1,
      sender: 'System Lead',
      team: 'Leads',
      content: 'Initiating deployment sequence for Nova field calibration',
      time: '10:30 AM',
      isSystem: true
    },
    {
      id: 2,
      sender: 'Orchestrator',
      team: 'Orchestrators',
      content: '@Nova Dev Please review the system architecture',
      time: '10:35 AM',
      isSystem: false
    }
  ]);

  const handleTeamChange = (event) => {
    setSelectedTeam(event.target.value);
  };

  const handleMessageChange = (event) => {
    setMessage(event.target.value);
  };

  const handleSend = () => {
    if (message.trim()) {
      // Send message logic here
      setMessage('');
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <PanelContainer>
      <TeamSelector>
        <Select value={selectedTeam} onChange={handleTeamChange}>
          <option value="all">All Teams</option>
          <option value="leads">Leads</option>
          <option value="orchestrators">Orchestrators</option>
          <option value="developers">Developers</option>
        </Select>
      </TeamSelector>

      <ChatArea>
        <MessageList>
          {messages.map(msg => (
            <Message key={msg.id} $isSystem={msg.isSystem}>
              <div className="header">
                <span className="sender">{msg.sender}</span>
                <span className="time">{msg.time}</span>
              </div>
              <div className="content">{msg.content}</div>
            </Message>
          ))}
        </MessageList>

        <InputArea>
          <Input
            value={message}
            onChange={handleMessageChange}
            onKeyPress={handleKeyPress}
            placeholder="Type your message... Use @ to mention teams or members"
          />
          <SendButton onClick={handleSend} disabled={!message.trim()}>
            Send
          </SendButton>
        </InputArea>
      </ChatArea>
    </PanelContainer>
  );
};

export default CollaborationPanel;
