# Frontend Development Guide

## Quick Start

### Prerequisites
- Node.js 18+ and npm 9+
- Git
- A code editor (VS Code recommended)

### Initial Setup

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd RAG-Search-LAB
   ```

2. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

3. **Install dependencies**:
   ```bash
   npm install
   ```

4. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

5. **Start development server**:
   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:3000`

## Development Modes

### 1. Full Stack Mode (Requires Backend)
Start the backend services first:
```bash
# Terminal 1 - Start FastAPI backend
cd RAG_Scripts
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2 - Start frontend
cd frontend
npm run dev
```

### 2. Mock API Mode (Frontend Only)
For UI development without backend:

1. Set in `.env`:
   ```
   VITE_ENABLE_MOCK_API=true
   ```

2. Start frontend:
   ```bash
   npm run dev
   ```

## Available Scripts

### Development
```bash
npm run dev          # Start dev server with hot reload
npm run build        # Build for production
npm run preview      # Preview production build
npm run type-check   # Check TypeScript types
npm run lint         # Run ESLint
npm run test         # Run tests (when added)
```

### Testing UI Features

#### 1. Dashboard Testing
- Navigate to `/` or `/dashboard`
- Check if metrics load properly
- Verify charts render correctly
- Test responsive design on different screen sizes

#### 2. Data Source Management
- Navigate to `/data-sources`
- Test CRUD operations:
  - Create new data source
  - Edit existing source
  - Delete source (with confirmation)
- Verify form validations
- Test connection testing feature

#### 3. RAG Configuration
- Navigate to `/rag-config`
- Test parameter adjustments:
  - Similarity threshold slider
  - Index type selection
  - Model configuration
- Verify real-time preview updates
- Test configuration save/load

#### 4. RBAC Management
- Navigate to `/users` and `/roles`
- Test user creation and role assignment
- Verify permission matrix updates
- Test API key generation

#### 5. Query Interface
- Navigate to `/query`
- Test different query modes
- Verify streaming responses
- Check citation display
- Test performance metrics visualization

## UI Component Structure

```
src/
├── components/           # Reusable components
│   ├── common/          # Generic components
│   ├── dashboard/       # Dashboard specific
│   ├── data-sources/    # Data source management
│   ├── rag-config/      # RAG configuration
│   ├── rbac/           # RBAC components
│   └── query/          # Query interface
├── pages/              # Page components
├── hooks/              # Custom React hooks
├── services/           # API service layer
├── stores/             # Zustand stores
├── types/              # TypeScript types
├── utils/              # Utility functions
└── mocks/              # Mock data for testing
```

## Mock API Development

When `VITE_ENABLE_MOCK_API=true`, the app uses mock services. Add mock endpoints in `src/mocks/`:

```typescript
// src/mocks/handlers.ts
export const handlers = [
  // Dashboard metrics
  http.get('/api/metrics/overview', () => {
    return HttpResponse.json({
      totalQueries: 1234,
      activeUsers: 56,
      avgResponseTime: 1.2,
      // ... more mock data
    })
  }),
  
  // Data sources
  http.get('/api/data-sources', () => {
    return HttpResponse.json([
      { id: '1', name: 'SharePoint Docs', type: 'sharepoint' },
      // ... more sources
    ])
  }),
]
```

## Testing Checklist

### Visual Testing
- [ ] All pages load without errors
- [ ] Components render correctly
- [ ] Forms validate properly
- [ ] Modals and dialogs work
- [ ] Loading states display
- [ ] Error states handle gracefully
- [ ] Responsive design works on mobile/tablet/desktop

### Functional Testing
- [ ] Navigation between pages works
- [ ] Forms submit correctly
- [ ] Data persists appropriately
- [ ] Real-time updates work (if applicable)
- [ ] Search and filtering work
- [ ] Pagination functions correctly

### Performance Testing
- [ ] Pages load quickly
- [ ] No unnecessary re-renders
- [ ] Large lists virtualize properly
- [ ] Images and assets optimize

## Debugging Tips

### Browser DevTools
1. **React Developer Tools**: Install browser extension
2. **Network Tab**: Monitor API calls
3. **Console**: Check for errors
4. **Performance Tab**: Profile rendering

### VS Code Extensions
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- TypeScript React code snippets
- Prettier - Code formatter

### Common Issues

#### 1. Module not found errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### 2. TypeScript errors
```bash
# Check types
npm run type-check

# If persistent, restart TS server in VS Code:
# Cmd/Ctrl + Shift + P → "TypeScript: Restart TS Server"
```

#### 3. Styling not applying
- Ensure Tailwind classes are correct
- Check if PostCSS is running
- Verify `index.css` is imported in `main.tsx`

#### 4. API connection issues
- Verify backend is running
- Check proxy configuration in `vite.config.ts`
- Ensure correct API URL in `.env`

## Build and Deployment

### Production Build
```bash
# Build optimized version
npm run build

# Test production build locally
npm run preview
```

### Build Output
- Output directory: `dist/`
- Static assets optimized and hashed
- Code split by route for performance

## Next Steps

1. **Start Development Server**: Follow Quick Start above
2. **Explore UI**: Navigate through different modules
3. **Test Features**: Use the testing checklist
4. **Report Issues**: Document any problems found
5. **Iterate**: Make improvements based on testing

## Resources

- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [Vite Documentation](https://vitejs.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [Zustand State Management](https://github.com/pmndrs/zustand)
- [React Query](https://tanstack.com/query/latest)