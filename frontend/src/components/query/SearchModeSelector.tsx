import { Fragment } from 'react'
import { Listbox, Transition } from '@headlessui/react'
import { CheckIcon, ChevronUpDownIcon } from '@heroicons/react/20/solid'
import { classNames } from '@/utils/classNames'

export interface SearchMode {
  id: 'cosine' | 'l2' | 'rag_context' | 'rag_open'
  name: string
  description: string
  category: 'similarity' | 'rag'
  icon: string
}

const searchModes: SearchMode[] = [
  {
    id: 'cosine',
    name: 'Cosine Similarity',
    description: 'Vector cosine similarity search (<=>) - Best for semantic similarity',
    category: 'similarity',
    icon: '📐'
  },
  {
    id: 'l2',
    name: 'L2 Distance',
    description: 'Euclidean distance vector search (<->) - Best for exact matches',
    category: 'similarity',
    icon: '📏'
  },
  {
    id: 'rag_context',
    name: 'RAG (Context Only)',
    description: 'RAG responses limited to provided context - Safe, factual answers',
    category: 'rag',
    icon: '🎯'
  },
  {
    id: 'rag_open',
    name: 'RAG (Open Fallback)',
    description: 'RAG with external knowledge fallback - Comprehensive answers',
    category: 'rag',
    icon: '🌐'
  }
]

interface SearchModeSelectorProps {
  selectedMode: SearchMode
  onModeChange: (mode: SearchMode) => void
  isLabMode?: boolean
}

export default function SearchModeSelector({ 
  selectedMode, 
  onModeChange, 
  isLabMode = false 
}: SearchModeSelectorProps) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        Search Mode
        {isLabMode && (
          <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
            LAB MODE
          </span>
        )}
      </label>
      
      <Listbox value={selectedMode} onChange={onModeChange}>
        <div className="relative">
          <Listbox.Button className="relative w-full cursor-default rounded-md border border-gray-300 bg-white py-2 pl-3 pr-10 text-left shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 sm:text-sm">
            <span className="flex items-center">
              <span className="text-lg mr-2">{selectedMode.icon}</span>
              <span className="block truncate font-medium">{selectedMode.name}</span>
              <span className="ml-2 text-xs text-gray-500">({selectedMode.category})</span>
            </span>
            <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
              <ChevronUpDownIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
            </span>
          </Listbox.Button>

          <Transition
            as={Fragment}
            leave="transition ease-in duration-100"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <Listbox.Options className="absolute z-10 mt-1 max-h-96 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
              {/* Group by category */}
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide border-b">
                Similarity Search
              </div>
              {searchModes
                .filter(mode => mode.category === 'similarity')
                .map((mode) => (
                  <Listbox.Option
                    key={mode.id}
                    className={({ active }) =>
                      classNames(
                        active ? 'text-white bg-indigo-600' : 'text-gray-900',
                        'relative cursor-default select-none py-2 pl-3 pr-9'
                      )
                    }
                    value={mode}
                  >
                    {({ selected, active }) => (
                      <>
                        <div className="flex items-center">
                          <span className="text-lg mr-2">{mode.icon}</span>
                          <div className="flex flex-col">
                            <span className={classNames(selected ? 'font-semibold' : 'font-normal', 'block truncate')}>
                              {mode.name}
                            </span>
                            <span className={classNames(active ? 'text-indigo-200' : 'text-gray-500', 'text-xs')}>
                              {mode.description}
                            </span>
                          </div>
                        </div>

                        {selected ? (
                          <span
                            className={classNames(
                              active ? 'text-white' : 'text-indigo-600',
                              'absolute inset-y-0 right-0 flex items-center pr-4'
                            )}
                          >
                            <CheckIcon className="h-5 w-5" aria-hidden="true" />
                          </span>
                        ) : null}
                      </>
                    )}
                  </Listbox.Option>
                ))}
              
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide border-b border-t">
                RAG Search
              </div>
              {searchModes
                .filter(mode => mode.category === 'rag')
                .map((mode) => (
                  <Listbox.Option
                    key={mode.id}
                    className={({ active }) =>
                      classNames(
                        active ? 'text-white bg-indigo-600' : 'text-gray-900',
                        'relative cursor-default select-none py-2 pl-3 pr-9'
                      )
                    }
                    value={mode}
                  >
                    {({ selected, active }) => (
                      <>
                        <div className="flex items-center">
                          <span className="text-lg mr-2">{mode.icon}</span>
                          <div className="flex flex-col">
                            <span className={classNames(selected ? 'font-semibold' : 'font-normal', 'block truncate')}>
                              {mode.name}
                            </span>
                            <span className={classNames(active ? 'text-indigo-200' : 'text-gray-500', 'text-xs')}>
                              {mode.description}
                            </span>
                          </div>
                        </div>

                        {selected ? (
                          <span
                            className={classNames(
                              active ? 'text-white' : 'text-indigo-600',
                              'absolute inset-y-0 right-0 flex items-center pr-4'
                            )}
                          >
                            <CheckIcon className="h-5 w-5" aria-hidden="true" />
                          </span>
                        ) : null}
                      </>
                    )}
                  </Listbox.Option>
                ))}
            </Listbox.Options>
          </Transition>
        </div>
      </Listbox>

      {isLabMode && (
        <div className="mt-3 p-3 bg-blue-50 rounded-md border border-blue-200">
          <h4 className="text-sm font-medium text-blue-900 mb-1">
            📚 LAB Mode: {selectedMode.name}
          </h4>
          <p className="text-sm text-blue-700">{selectedMode.description}</p>
          {selectedMode.category === 'similarity' && (
            <div className="mt-2 text-xs text-blue-600">
              <strong>How it works:</strong> Compares your query vector with document vectors using {' '}
              {selectedMode.id === 'cosine' ? 'cosine similarity (angle-based)' : 'L2 distance (magnitude-based)'} 
              {' '} to find the most similar content.
            </div>
          )}
          {selectedMode.category === 'rag' && (
            <div className="mt-2 text-xs text-blue-600">
              <strong>How it works:</strong> Retrieves relevant documents, then uses an LLM to generate answers {' '}
              {selectedMode.id === 'rag_context' ? 'strictly from the provided context' : 'with fallback to external knowledge'}.
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export { searchModes }