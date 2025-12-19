# NovaOps Development Guide

## Build Commands
- `npm start` - Run development server
- `npm run build` - Create production build
- `npm test` - Run all tests
- `npm test -- -t "test name"` - Run single test
- `npm run verify:atlassian` - Verify Atlassian integration
- `npm run verify:all` - Run all verification scripts

## Code Style Guidelines
- **Components**: PascalCase for components and classes
- **Variables/Functions**: camelCase for variables, functions, methods
- **Constants**: UPPERCASE for constants (e.g., COLORS)
- **Files**: Names should match exported component/class
- **Imports**: React first, third-party next, local last
- **Types**: Use TypeScript interfaces for data structures and APIs
- **Error Handling**: Use try/catch with specific error messages and fallbacks
- **Services**: Implement singleton pattern for services
- **Styling**: Use styled-components with consistent naming
- **Testing**: Write tests for all new functionality

Follow existing patterns in the codebase for consistency. Maintain separation between services, components, and utilities.