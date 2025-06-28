import { ClockIcon, CpuChipIcon, CurrencyDollarIcon } from '@heroicons/react/24/outline'

interface QueryMetrics {
  embedding_ms?: number
  db_ms?: number
  llm_ms?: number
  total_ms?: number
  token_usage?: {
    prompt: number
    completion: number
    total: number
  }
  cost?: number
  top_score?: number
}

interface PerformanceMetricsProps {
  metrics: QueryMetrics
  isLabMode?: boolean
}

export default function PerformanceMetrics({ metrics, isLabMode = false }: PerformanceMetricsProps) {
  const formatTime = (ms: number) => {
    if (ms < 1000) return `${ms.toFixed(1)}ms`
    return `${(ms / 1000).toFixed(2)}s`
  }

  const formatCost = (cost: number) => {
    return `$${cost.toFixed(4)}`
  }

  const getTimeBreakdown = () => {
    const embedding = metrics.embedding_ms || 0
    const db = metrics.db_ms || 0
    const llm = metrics.llm_ms || 0
    const total = metrics.total_ms || embedding + db + llm
    
    return {
      embedding: { time: embedding, percentage: total > 0 ? (embedding / total) * 100 : 0 },
      db: { time: db, percentage: total > 0 ? (db / total) * 100 : 0 },
      llm: { time: llm, percentage: total > 0 ? (llm / total) * 100 : 0 },
      total
    }
  }

  const breakdown = getTimeBreakdown()

  if (!metrics.total_ms && !metrics.embedding_ms) {
    return null
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-900">Performance Metrics</h3>
        {isLabMode && (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
            LAB MODE
          </span>
        )}
      </div>

      {/* Total Time */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <div className="flex items-center">
          <ClockIcon className="h-5 w-5 text-gray-400 mr-2" />
          <span className="text-sm font-medium text-gray-900">Total Time:</span>
          <span className="ml-2 text-lg font-semibold text-indigo-600">
            {formatTime(breakdown.total)}
          </span>
        </div>

        {/* Time Breakdown Bar */}
        <div className="mt-3">
          <div className="flex text-xs text-gray-600 mb-1">
            <span>Embedding</span>
            <span className="ml-auto">Database</span>
            <span className="ml-auto">LLM</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 flex overflow-hidden">
            <div 
              className="bg-blue-500 h-2" 
              style={{ width: `${breakdown.embedding.percentage}%` }}
              title={`Embedding: ${formatTime(breakdown.embedding.time)}`}
            />
            <div 
              className="bg-green-500 h-2" 
              style={{ width: `${breakdown.db.percentage}%` }}
              title={`Database: ${formatTime(breakdown.db.time)}`}
            />
            <div 
              className="bg-purple-500 h-2" 
              style={{ width: `${breakdown.llm.percentage}%` }}
              title={`LLM: ${formatTime(breakdown.llm.time)}`}
            />
          </div>
          <div className="flex text-xs text-gray-500 mt-1">
            <span>{formatTime(breakdown.embedding.time)}</span>
            <span className="ml-auto">{formatTime(breakdown.db.time)}</span>
            <span className="ml-auto">{formatTime(breakdown.llm.time)}</span>
          </div>
        </div>
      </div>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {/* Token Usage */}
        {metrics.token_usage && (
          <div className="bg-white p-3 rounded-lg border border-gray-200">
            <div className="flex items-center mb-2">
              <CpuChipIcon className="h-4 w-4 text-gray-400 mr-1" />
              <span className="text-xs font-medium text-gray-700">Tokens</span>
            </div>
            <div className="text-lg font-semibold text-gray-900">
              {metrics.token_usage.total.toLocaleString()}
            </div>
            <div className="text-xs text-gray-500">
              {metrics.token_usage.prompt} prompt + {metrics.token_usage.completion} completion
            </div>
          </div>
        )}

        {/* Cost */}
        {metrics.cost !== undefined && (
          <div className="bg-white p-3 rounded-lg border border-gray-200">
            <div className="flex items-center mb-2">
              <CurrencyDollarIcon className="h-4 w-4 text-gray-400 mr-1" />
              <span className="text-xs font-medium text-gray-700">Cost</span>
            </div>
            <div className="text-lg font-semibold text-gray-900">
              {formatCost(metrics.cost)}
            </div>
          </div>
        )}

        {/* Top Score */}
        {metrics.top_score !== undefined && (
          <div className="bg-white p-3 rounded-lg border border-gray-200">
            <div className="flex items-center mb-2">
              <span className="text-xs font-medium text-gray-700">Best Match</span>
            </div>
            <div className="text-lg font-semibold text-gray-900">
              {metrics.top_score.toFixed(4)}
            </div>
            <div className="text-xs text-gray-500">
              similarity score
            </div>
          </div>
        )}
      </div>

      {/* LAB Mode Explanations */}
      {isLabMode && (
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <h4 className="text-sm font-medium text-blue-900 mb-2">
            📊 Understanding Performance Metrics
          </h4>
          <div className="space-y-2 text-xs text-blue-700">
            <div>
              <strong>Embedding Time:</strong> Time to convert your query text into a vector representation
            </div>
            <div>
              <strong>Database Time:</strong> Time to search the vector database and retrieve relevant documents
            </div>
            <div>
              <strong>LLM Time:</strong> Time for the language model to generate the final response
            </div>
            <div>
              <strong>Tokens:</strong> Units of text processed by the LLM (affects cost and performance)
            </div>
            {metrics.top_score !== undefined && (
              <div>
                <strong>Similarity Score:</strong> How similar the best match is to your query (lower = more similar for L2, higher = more similar for cosine)
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}