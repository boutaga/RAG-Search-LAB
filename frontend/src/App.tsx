import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import DataSources from './pages/DataSources'
import RAGConfig from './pages/RAGConfig'
import Users from './pages/Users'
import Roles from './pages/Roles'
import RuleEngine from './pages/RuleEngine'
import Query from './pages/Query'
import APIKeys from './pages/APIKeys'
import Settings from './pages/Settings'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/data-sources" element={<DataSources />} />
            <Route path="/rag-config" element={<RAGConfig />} />
            <Route path="/users" element={<Users />} />
            <Route path="/roles" element={<Roles />} />
            <Route path="/rules" element={<RuleEngine />} />
            <Route path="/query" element={<Query />} />
            <Route path="/api-keys" element={<APIKeys />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </Router>
      <Toaster position="top-right" />
    </QueryClientProvider>
  )
}

export default App