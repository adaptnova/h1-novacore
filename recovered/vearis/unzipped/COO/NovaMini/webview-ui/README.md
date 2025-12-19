# Nova Mini Webview UI

Fast, responsive UI for Nova Mini VSCode extension.

## Quick Start

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

## Project Structure

```
webview-ui/
├── src/
│   ├── components/
│   │   ├── chat/
│   │   │   └── ChatView.tsx       # Main chat interface
│   │   └── shared/
│   │       ├── CodeBlock.tsx      # Code syntax highlighting
│   │       ├── TokenCounter.tsx   # Token usage display
│   │       └── StatusIndicator.tsx # System status display
│   ├── types/
│   │   └── index.ts              # TypeScript definitions
│   ├── App.tsx                   # Root component
│   ├── main.tsx                  # Entry point
│   └── styles.css                # Global styles
├── index.html                    # HTML template
├── package.json                  # Dependencies
├── tsconfig.json                 # TypeScript config
├── tsconfig.node.json           # Node-specific TS config
└── vite.config.ts               # Vite build config
```

## Features

- Real-time chat interface
- Code syntax highlighting
- Token counting
- System status monitoring
- VSCode theme integration
- Responsive design

## Development

### VSCode Integration

The UI automatically integrates with VSCode's:
- Theme colors
- Font settings
- Window state
- Message passing

### Message Protocol

```typescript
// From extension to webview
interface FromExtension {
  type: 'updateModelStatus' | 'updateSystemHealth' | 'modelSelected';
  status?: ModelStatus;
  health?: SystemHealth;
  model?: string;
}

// From webview to extension
interface ToExtension {
  type: 'sendMessage' | 'requestInitialState';
  text?: string;
  model?: string;
}
```

### Styling

- Uses VSCode CSS variables for theming
- Supports light, dark, and high contrast themes
- Responsive layout with flexbox
- Smooth animations and transitions

### Performance

- Fast initial load (<1s)
- Responsive UI (<16ms frame time)
- Efficient message handling
- Memory-conscious design

## Building

1. Development:
   - Hot module replacement
   - Source maps
   - Error overlay

2. Production:
   - Minified output
   - Tree shaking
   - Asset optimization

## Testing

```bash
# Run unit tests
npm test

# Run linter
npm run lint
```

## Best Practices

1. Component Design:
   - Pure functional components
   - React hooks for state
   - Proper type definitions
   - Error boundaries

2. Performance:
   - Memoization where needed
   - Efficient re-renders
   - Proper cleanup
   - Event debouncing

3. Accessibility:
   - ARIA attributes
   - Keyboard navigation
   - Screen reader support
   - High contrast support

4. Code Quality:
   - TypeScript strict mode
   - ESLint configuration
   - Prettier formatting
   - Clear documentation

## Contributing

1. Follow TypeScript guidelines
2. Maintain test coverage
3. Document changes
4. Update types as needed