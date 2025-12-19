import React, { useEffect, useRef } from 'react';
import { CodeBlockProps } from '../../types';
import Prism from 'prismjs';
import 'prismjs/themes/prism-tomorrow.css';
import 'prismjs/components/prism-typescript';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-json';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-yaml';

const CodeBlock: React.FC<CodeBlockProps> = ({ content, language = 'typescript' }) => {
  const codeRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (codeRef.current) {
      Prism.highlightElement(codeRef.current);
    }
  }, [content, language]);

  // Extract code from markdown-style code blocks
  const extractCode = (content: string): { code: string; lang: string } => {
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/;
    const match = content.match(codeBlockRegex);
    
    if (match) {
      return {
        code: match[2].trim(),
        lang: match[1]?.toLowerCase() || language
      };
    }
    
    return {
      code: content,
      lang: language
    };
  };

  const { code, lang } = extractCode(content);

  return (
    <div className="code-block-container">
      <div className="code-header">
        <span className="language-label">{lang}</span>
        <button
          className="copy-button"
          onClick={() => navigator.clipboard.writeText(code)}
        >
          Copy
        </button>
      </div>
      <pre className={`language-${lang}`}>
        <code ref={codeRef} className={`language-${lang}`}>
          {code}
        </code>
      </pre>
    </div>
  );
};

export default CodeBlock;