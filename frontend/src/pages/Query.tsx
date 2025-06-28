import { useState } from 'react'
import { useLabModeStore } from '@/stores/labModeStore'
import SearchModeSelector, { SearchMode, searchModes } from '@/components/query/SearchModeSelector'
import PerformanceMetrics from '@/components/query/PerformanceMetrics'
import { PaperAirplaneIcon, ArrowPathIcon } from '@heroicons/react/24/outline'

// Mock data for demonstration
const mockResults = {
  cosine: [
    { id: 1, title: 'Password Reset Procedure', distance: 0.23, snippet: 'To reset your password, navigate to the login page...' },
    { id: 2, title: 'Account Security Guidelines', distance: 0.34, snippet: 'Security best practices for user accounts...' },
  ],
  l2: [
    { id: 1, title: 'Password Reset Procedure', distance: 1.45, snippet: 'To reset your password, navigate to the login page...' },
    { id: 2, title: 'System Administration Guide', distance: 1.67, snippet: 'Administrative procedures for system management...' },
  ],
  rag_context: {
    answer: 'Based on the provided documentation, to reset your password you should navigate to the login page and click on "Forgot Password". This will send a reset link to your registered email address.',
    sources: ['Password Reset Procedure', 'Account Security Guidelines']
  },
  rag_open: {
    answer: 'To reset your password, you can use the "Forgot Password" link on the login page. If that doesn\'t work, you can also contact your system administrator. Based on external information: Most enterprise systems also support password reset through active directory or single sign-on systems.',
    sources: ['Password Reset Procedure']
  }
}

const mockMetrics = {
  embedding_ms: 234.5,
  db_ms: 45.2,
  llm_ms: 1200.8,
  total_ms: 1480.5,
  token_usage: {
    prompt: 150,
    completion: 75,
    total: 225
  },
  cost: 0.0045,
  top_score: 0.23
}

export default function Query() {
  const { isLabMode } = useLabModeStore()
  const [selectedMode, setSelectedMode] = useState<SearchMode>(searchModes[0])
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [metrics, setMetrics] = useState<any>(null)

  const handleSearch = async () => {
    if (!query.trim()) return
    
    setIsLoading(true)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Set mock results based on selected mode
    setResults(mockResults[selectedMode.id])
    setMetrics(mockMetrics)
    setIsLoading(false)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSearch()
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Query Interface</h1>
        <p className="mt-1 text-sm text-gray-500">
          Interactive query interface with advanced search capabilities
          {isLabMode && (
            <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
              LAB MODE ACTIVE - Educational explanations enabled
            </span>
          )}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Search Controls */}
        <div className="lg:col-span-1 space-y-6">
          {/* Search Mode Selector */}
          <SearchModeSelector 
            selectedMode={selectedMode}
            onModeChange={setSelectedMode}
            isLabMode={isLabMode}
          />

          {/* Query Input */}
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
              Your Query
            </label>
            <div className="relative">
              <textarea
                id="query"
                rows={4}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                placeholder="Enter your question or search query..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyPress}
              />
              <button
                type="button"
                onClick={handleSearch}
                disabled={!query.trim() || isLoading}
                className="absolute bottom-2 right-2 inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <ArrowPathIcon className="h-4 w-4 animate-spin" />
                ) : (
                  <PaperAirplaneIcon className="h-4 w-4" />
                )}
              </button>
            </div>
            {isLabMode && (
              <p className="mt-1 text-xs text-gray-500">
                💡 Try queries like "How do I reset my password?" or "Server troubleshooting steps"
              </p>
            )}
          </div>

          {/* Performance Metrics */}
          {metrics && (
            <PerformanceMetrics metrics={metrics} isLabMode={isLabMode} />
          )}
        </div>

        {/* Results */}
        <div className="lg:col-span-2">
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Search Results
              {selectedMode && (
                <span className="ml-2 text-sm text-gray-500">
                  ({selectedMode.name})
                </span>
              )}
            </h3>

            {isLoading && (
              <div className="flex items-center justify-center py-12">
                <ArrowPathIcon className="h-8 w-8 animate-spin text-indigo-600" />
                <span className="ml-2 text-gray-600">Searching...</span>
              </div>
            )}

            {!isLoading && !results && (
              <div className="text-center py-12">
                <div className="text-gray-400 text-lg mb-2">🔍</div>
                <p className="text-gray-500">Enter a query and select a search mode to see results</p>
                {isLabMode && (
                  <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                    <h4 className="text-sm font-medium text-blue-900 mb-2">
                      🎓 LAB Mode Tips
                    </h4>
                    <ul className="text-xs text-blue-700 space-y-1 text-left">
                      <li>• Try different search modes to compare results</li>
                      <li>• Watch the performance metrics to understand trade-offs</li>
                      <li>• Similarity search returns raw results with scores</li>
                      <li>• RAG search generates natural language answers</li>
                    </ul>
                  </div>
                )}
              </div>
            )}

            {results && selectedMode.category === 'similarity' && Array.isArray(results) && (
              <div className="space-y-4">
                {results.map((result, index) => (
                  <div key={result.id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-medium text-gray-900">{result.title}</h4>
                      <div className="flex items-center text-sm text-gray-500">
                        <span className="font-mono">
                          {selectedMode.id === 'cosine' ? '📐' : '📏'} {result.distance.toFixed(4)}
                        </span>
                        {isLabMode && (
                          <span className="ml-2 text-xs text-blue-600">
                            (Rank #{index + 1})
                          </span>
                        )}
                      </div>
                    </div>
                    <p className="text-gray-600 text-sm">{result.snippet}</p>
                    {isLabMode && (
                      <div className="mt-2 text-xs text-gray-500">
                        {selectedMode.id === 'cosine' 
                          ? 'Lower cosine distance = more similar' 
                          : 'Lower L2 distance = more similar'
                        }
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {results && selectedMode.category === 'rag' && !Array.isArray(results) && (
              <div className="space-y-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h4 className="font-medium text-green-900 mb-2">Generated Answer</h4>
                  <p className="text-gray-700">{results.answer}</p>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Sources</h4>
                  <div className="space-y-2">
                    {results.sources.map((source: string, index: number) => (
                      <div key={index} className="text-sm text-gray-600 bg-gray-50 rounded px-3 py-2">
                        📄 {source}
                      </div>
                    ))}
                  </div>
                </div>

                {isLabMode && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-blue-900 mb-2">
                      🎓 Understanding RAG Results
                    </h4>
                    <div className="text-xs text-blue-700 space-y-1">
                      <div>• The LLM generated this answer using the retrieved sources</div>
                      <div>• {selectedMode.id === 'rag_context' 
                        ? 'Context-only mode limits answers to provided documents'
                        : 'Open mode allows external knowledge when context is insufficient'
                      }</div>
                      <div>• Always verify important information from the original sources</div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}