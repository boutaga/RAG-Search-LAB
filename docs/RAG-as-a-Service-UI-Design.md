# RAG-as-a-Service UI Design Document

## Overview
This document outlines the comprehensive UI design for an open-source, vendor-agnostic RAG-as-a-Service platform built on pgvector.

## Core UI Modules

### 1. Dashboard & Analytics
- **Main Dashboard**
  - Active RAG endpoints status
  - Query volume metrics
  - Performance graphs (latency, throughput)
  - Resource utilization (CPU, Memory, pgvector index stats)
  - Active users and API key usage

### 2. Data Source Management
- **Data References Configuration**
  - Add/Edit/Delete data sources (URLs, file paths, S3 buckets)
  - Label management and categorization
  - Access permission mapping
  - Crawling/refresh schedules
  - Preview data samples
- **Supported Sources**
  - File shares (SMB, NFS)
  - Object storage (S3, MinIO)
  - Databases (direct SQL connections)
  - APIs (REST endpoints)
  - SharePoint/OneDrive
  - Service Desk systems (via DB connection)

### 3. RAG Configuration Center
- **Model Configuration**
  - OpenAI API key management (encrypted storage)
  - Model selection (GPT-4, GPT-3.5, future models)
  - Embedding model configuration
  - Token limits and cost controls
- **Retrieval Settings**
  - Vector index selection (HNSW, IVFFlat, pgvectorscale)
  - Similarity threshold tuning
  - Chunk size configuration
  - Hybrid search weight adjustment (dense vs sparse)
  - Reranking model selection
- **Performance Tuning**
  - Index parameter optimization
  - Parallel query configuration
  - Cache settings
  - Connection pooling

### 4. RBAC Management
- **User Management**
  - User creation/invitation
  - Role assignment
  - API key generation per user
  - Usage quotas and limits
- **Role Designer**
  - Predefined roles (Admin, Developer, Analyst, Viewer)
  - Custom role creation
  - Permission matrix:
    - Data source access
    - RAG endpoint access
    - Configuration permissions
    - API key management
- **Access Control Lists**
  - Fine-grained permissions per data source
  - Query result filtering rules
  - PII/sensitive data masking

### 5. Rule Engine & Guardrails
- **Business Logic Rules**
  - Visual rule builder (if-then-else)
  - JavaScript/Python code editor for complex rules
  - Rule templates library
- **Guardrail Configuration**
  - Content filtering rules
  - Response validation
  - PII detection and masking
  - Prompt injection prevention
  - Rate limiting rules
- **Testing Interface**
  - Rule testing sandbox
  - Sample query testing
  - Rule debugging tools

### 6. SSL Certificate Management
- **Certificate Store**
  - Upload/Import certificates
  - Auto-renewal configuration (Let's Encrypt)
  - Certificate expiry monitoring
- **TLS Configuration**
  - Per-component TLS settings
  - mTLS configuration for service-to-service
  - Certificate pinning options

### 7. Query Interface
- **Interactive Chat**
  - Multi-mode selection (Naive RAG, Hybrid, Raw similarity)
  - Real-time streaming responses
  - Citation viewing with source preview
  - Query history and bookmarks
- **Advanced Query Builder**
  - Natural language or SQL-like syntax
  - Filter builder UI
  - Metadata constraints
  - Date range selection
- **Performance Visualization**
  - Query execution timeline
  - Token usage breakdown
  - Retrieval scores visualization
  - Cost estimation

### 8. API Management
- **API Key Management**
  - Key generation with scopes
  - Usage tracking per key
  - Rate limit configuration
  - Key rotation scheduling
- **Documentation**
  - Interactive API explorer (Swagger UI)
  - Code examples generator
  - SDK downloads

### 9. Monitoring & Logs
- **Query Analytics**
  - Query patterns analysis
  - Popular topics identification
  - Failed query diagnostics
  - User satisfaction metrics
- **System Logs**
  - Real-time log viewer
  - Log search and filtering
  - Alert configuration
  - Export capabilities

### 10. Service Desk Integration
- **Database Mapping**
  - Visual schema explorer
  - Table/column selection for indexing
  - Field mapping configuration
  - Relationship detection
- **Ticket Analysis**
  - Ticket categorization
  - Problem pattern detection
  - Solution recommendation
  - Knowledge base integration

## UI Component Architecture

### Layout Structure
```
┌─────────────────────────────────────────────────────────┐
│ Header: Logo | Navigation | User Menu | Notifications   │
├─────────────┬───────────────────────────────────────────┤
│             │                                           │
│  Sidebar    │         Main Content Area                │
│             │                                           │
│ - Dashboard │    Dynamic content based on              │
│ - Data Src  │    selected module                       │
│ - RAG Config│                                           │
│ - RBAC      │                                           │
│ - Rules     │                                           │
│ - Query     │                                           │
│ - API Keys  │                                           │
│ - Monitoring│                                           │
│ - Settings  │                                           │
│             │                                           │
└─────────────┴───────────────────────────────────────────┘
```

### Design System
- **Theme**: Dark/Light mode support
- **Components**: 
  - Custom React component library
  - Consistent form elements
  - Data tables with sorting/filtering
  - Charts using Recharts or D3.js
  - Toast notifications
  - Modal dialogs
  - Drag-and-drop interfaces
- **Responsive**: Mobile-friendly for monitoring

## Key UI Workflows

### 1. Initial Setup Wizard
1. Database connection configuration
2. pgvector extension verification
3. First admin user creation
4. OpenAI API key setup
5. First data source configuration
6. Basic RAG endpoint creation

### 2. Data Source Addition Flow
1. Select source type
2. Enter connection details
3. Test connection
4. Configure access permissions
5. Set refresh schedule
6. Preview sample data
7. Initiate first indexing

### 3. RAG Endpoint Creation
1. Name and describe endpoint
2. Select data sources
3. Configure retrieval parameters
4. Set up guardrails
5. Define access permissions
6. Test with sample queries
7. Generate API documentation

### 4. Query Debugging Flow
1. Enter problematic query
2. View retrieval results with scores
3. Inspect prompt construction
4. Analyze token usage
5. Test parameter adjustments
6. Save optimized configuration

## Technical Implementation Notes

### Frontend Stack
- **Framework**: React 18+ with TypeScript
- **State Management**: Zustand or Redux Toolkit
- **UI Library**: Tailwind CSS + Headless UI
- **Data Fetching**: TanStack Query
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts or Victory
- **Tables**: TanStack Table
- **Code Editor**: Monaco Editor
- **Build Tool**: Vite

### Security Considerations
- All API keys encrypted at rest
- Role-based UI component rendering
- CSRF protection
- Content Security Policy headers
- Input sanitization
- Audit logging for all actions

### Performance Optimizations
- Lazy loading for large datasets
- Virtual scrolling for tables
- WebSocket for real-time updates
- Service Worker for offline capability
- Response caching strategies
- Code splitting by route