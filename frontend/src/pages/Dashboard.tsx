import { useState, useEffect } from 'react'
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/20/solid'
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { classNames } from '@/utils/classNames'

const stats = [
  { name: 'Total Queries', stat: '12,456', previousStat: '11,234', change: '10.9%', changeType: 'increase' },
  { name: 'Active Users', stat: '234', previousStat: '198', change: '18.2%', changeType: 'increase' },
  { name: 'Avg Response Time', stat: '1.24s', previousStat: '1.56s', change: '20.5%', changeType: 'decrease' },
  { name: 'Data Sources', stat: '18', previousStat: '15', change: '20%', changeType: 'increase' },
]

// Mock data for charts
const queryVolumeData = [
  { time: '00:00', queries: 45 },
  { time: '04:00', queries: 32 },
  { time: '08:00', queries: 125 },
  { time: '12:00', queries: 234 },
  { time: '16:00', queries: 198 },
  { time: '20:00', queries: 87 },
]

const performanceData = [
  { date: 'Mon', latency: 1.2, throughput: 450 },
  { date: 'Tue', latency: 1.1, throughput: 480 },
  { date: 'Wed', latency: 1.3, throughput: 420 },
  { date: 'Thu', latency: 1.0, throughput: 520 },
  { date: 'Fri', latency: 1.2, throughput: 490 },
  { date: 'Sat', latency: 1.4, throughput: 380 },
  { date: 'Sun', latency: 1.5, throughput: 350 },
]

const topDataSources = [
  { name: 'SharePoint Docs', queries: 3456, percentage: 28 },
  { name: 'Service Desk DB', queries: 2890, percentage: 23 },
  { name: 'Knowledge Base', queries: 2345, percentage: 19 },
  { name: 'Technical Wiki', queries: 1987, percentage: 16 },
  { name: 'Policy Documents', queries: 1778, percentage: 14 },
]

export default function Dashboard() {
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => setLoading(false), 1000)
    return () => clearTimeout(timer)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Overview of your RAG service performance and usage metrics
        </p>
      </div>

      {/* Stats */}
      <div>
        <dl className="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((item) => (
            <div
              key={item.name}
              className="relative overflow-hidden rounded-lg bg-white px-4 pb-12 pt-5 shadow sm:px-6 sm:pt-6"
            >
              <dt>
                <div className="absolute rounded-md bg-indigo-500 p-3">
                  <div className="h-6 w-6 text-white" aria-hidden="true" />
                </div>
                <p className="ml-16 truncate text-sm font-medium text-gray-500">{item.name}</p>
              </dt>
              <dd className="ml-16 flex items-baseline pb-6 sm:pb-7">
                <p className="text-2xl font-semibold text-gray-900">{item.stat}</p>
                <p
                  className={classNames(
                    item.changeType === 'increase' ? 'text-green-600' : 'text-red-600',
                    'ml-2 flex items-baseline text-sm font-semibold'
                  )}
                >
                  {item.changeType === 'increase' ? (
                    <ArrowUpIcon className="h-5 w-5 flex-shrink-0 self-center text-green-500" aria-hidden="true" />
                  ) : (
                    <ArrowDownIcon className="h-5 w-5 flex-shrink-0 self-center text-red-500" aria-hidden="true" />
                  )}
                  <span className="sr-only"> {item.changeType === 'increase' ? 'Increased' : 'Decreased'} by </span>
                  {item.change}
                </p>
                <div className="absolute inset-x-0 bottom-0 bg-gray-50 px-4 py-4 sm:px-6">
                  <div className="text-sm">
                    <span className="text-gray-500">from {item.previousStat}</span>
                  </div>
                </div>
              </dd>
            </div>
          ))}
        </dl>
      </div>

      {/* Charts */}
      <div className="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-2">
        {/* Query Volume */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Query Volume (24h)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={queryVolumeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="queries" stroke="#6366f1" fill="#818cf8" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Performance Metrics */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Metrics (7d)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Line yAxisId="left" type="monotone" dataKey="latency" stroke="#ef4444" name="Latency (s)" />
              <Line yAxisId="right" type="monotone" dataKey="throughput" stroke="#10b981" name="Throughput" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Data Sources */}
      <div className="mt-8 bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Data Sources by Usage</h3>
          <div className="space-y-4">
            {topDataSources.map((source) => (
              <div key={source.name}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">{source.name}</span>
                  <span className="text-sm text-gray-500">{source.queries} queries</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-indigo-600 h-2 rounded-full"
                    style={{ width: `${source.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mt-8 bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
          <div className="flow-root">
            <ul role="list" className="-mb-8">
              {[
                { id: 1, type: 'query', user: 'john.doe@company.com', time: '2 minutes ago', detail: 'Searched for "password reset procedures"' },
                { id: 2, type: 'config', user: 'admin@company.com', time: '15 minutes ago', detail: 'Updated RAG configuration "Support Bot v2"' },
                { id: 3, type: 'data', user: 'system', time: '1 hour ago', detail: 'Synced 234 documents from SharePoint' },
                { id: 4, type: 'user', user: 'admin@company.com', time: '3 hours ago', detail: 'Added new user sarah.smith@company.com' },
              ].map((activity, activityIdx) => (
                <li key={activity.id}>
                  <div className="relative pb-8">
                    {activityIdx !== 3 ? (
                      <span
                        className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200"
                        aria-hidden="true"
                      />
                    ) : null}
                    <div className="relative flex space-x-3">
                      <div>
                        <span
                          className={classNames(
                            activity.type === 'query' ? 'bg-blue-500' :
                            activity.type === 'config' ? 'bg-yellow-500' :
                            activity.type === 'data' ? 'bg-green-500' : 'bg-purple-500',
                            'h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white'
                          )}
                        >
                          <div className="h-5 w-5 text-white" aria-hidden="true" />
                        </span>
                      </div>
                      <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                        <div>
                          <p className="text-sm text-gray-900">
                            {activity.detail}{' '}
                            <span className="font-medium text-gray-900">{activity.user}</span>
                          </p>
                        </div>
                        <div className="whitespace-nowrap text-right text-sm text-gray-500">
                          <time>{activity.time}</time>
                        </div>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}