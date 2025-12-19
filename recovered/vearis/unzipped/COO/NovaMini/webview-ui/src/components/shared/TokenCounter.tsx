import React, { useEffect, useState } from 'react';
import { TokenCounterProps } from '../../types';

// Simple GPT-style token estimation (not exact but fast for UI feedback)
const estimateTokenCount = (text: string): number => {
  // Average English word is ~4 characters, and 1 token is ~4 characters
  // This is a rough estimation for UI purposes only
  return Math.ceil(text.length / 4);
};

const TokenCounter: React.FC<TokenCounterProps> = ({ text, maxTokens = 8192 }) => {
  const [tokenCount, setTokenCount] = useState(0);
  const [isOverLimit, setIsOverLimit] = useState(false);

  useEffect(() => {
    const count = estimateTokenCount(text);
    setTokenCount(count);
    setIsOverLimit(count > maxTokens);
  }, [text, maxTokens]);

  return (
    <div className={`token-counter ${isOverLimit ? 'over-limit' : ''}`}>
      <span className="token-count">
        {tokenCount.toLocaleString()} / {maxTokens.toLocaleString()}
      </span>
      <div className="token-progress">
        <div 
          className="token-bar"
          style={{ 
            width: `${Math.min((tokenCount / maxTokens) * 100, 100)}%`,
            backgroundColor: isOverLimit ? '#ff4444' : '#44ff44'
          }}
        />
      </div>
      {isOverLimit && (
        <span className="token-warning">
          Token limit exceeded
        </span>
      )}
    </div>
  );
};

export default TokenCounter;