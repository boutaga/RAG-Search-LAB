import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface LabModeState {
  // LAB mode settings
  isLabMode: boolean
  showExplanations: boolean
  trackPerformance: boolean
  compareResults: boolean
  
  // Current lab/tutorial state
  currentLab: string | null
  labProgress: Record<string, number>
  
  // Tutorial settings
  showTutorialTooltips: boolean
  autoAdvanceTutorial: boolean
  
  // Actions
  toggleLabMode: () => void
  setLabMode: (enabled: boolean) => void
  setShowExplanations: (show: boolean) => void
  setTrackPerformance: (track: boolean) => void
  setCompareResults: (compare: boolean) => void
  setCurrentLab: (lab: string | null) => void
  updateLabProgress: (lab: string, progress: number) => void
  resetLabProgress: () => void
  setTutorialTooltips: (show: boolean) => void
  setAutoAdvanceTutorial: (auto: boolean) => void
}

export const useLabModeStore = create<LabModeState>()(
  persist(
    (set, get) => ({
      // Initial state
      isLabMode: false,
      showExplanations: true,
      trackPerformance: true,
      compareResults: false,
      currentLab: null,
      labProgress: {},
      showTutorialTooltips: true,
      autoAdvanceTutorial: false,

      // Actions
      toggleLabMode: () => set((state) => ({ isLabMode: !state.isLabMode })),
      
      setLabMode: (enabled: boolean) => set({ isLabMode: enabled }),
      
      setShowExplanations: (show: boolean) => set({ showExplanations: show }),
      
      setTrackPerformance: (track: boolean) => set({ trackPerformance: track }),
      
      setCompareResults: (compare: boolean) => set({ compareResults: compare }),
      
      setCurrentLab: (lab: string | null) => set({ currentLab: lab }),
      
      updateLabProgress: (lab: string, progress: number) => 
        set((state) => ({
          labProgress: {
            ...state.labProgress,
            [lab]: Math.max(0, Math.min(100, progress))
          }
        })),
      
      resetLabProgress: () => set({ labProgress: {} }),
      
      setTutorialTooltips: (show: boolean) => set({ showTutorialTooltips: show }),
      
      setAutoAdvanceTutorial: (auto: boolean) => set({ autoAdvanceTutorial: auto }),
    }),
    {
      name: 'lab-mode-storage',
      // Only persist user preferences, not temporary state
      partialize: (state) => ({
        isLabMode: state.isLabMode,
        showExplanations: state.showExplanations,
        trackPerformance: state.trackPerformance,
        compareResults: state.compareResults,
        showTutorialTooltips: state.showTutorialTooltips,
        autoAdvanceTutorial: state.autoAdvanceTutorial,
        labProgress: state.labProgress,
      }),
    }
  )
)

// Lab definitions
export interface Lab {
  id: string
  title: string
  description: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  estimatedTime: string
  objectives: string[]
  prerequisites?: string[]
}

export const availableLabs: Lab[] = [
  {
    id: 'lab0-search-comparison',
    title: 'Lab 0: Search Method Comparison',
    description: 'Compare different search methods and understand their strengths',
    difficulty: 'beginner',
    estimatedTime: '15 minutes',
    objectives: [
      'Understand cosine vs L2 distance',
      'Compare similarity search vs RAG',
      'Analyze performance metrics',
      'Choose appropriate search method'
    ]
  },
  {
    id: 'lab1-similarity-search',
    title: 'Lab 1: Vector Similarity Search',
    description: 'Deep dive into vector similarity algorithms',
    difficulty: 'beginner',
    estimatedTime: '20 minutes',
    objectives: [
      'Understand vector embeddings',
      'Practice cosine similarity',
      'Practice L2 distance',
      'Interpret similarity scores'
    ]
  },
  {
    id: 'lab2-rag-patterns',
    title: 'Lab 2: RAG Implementation Patterns',
    description: 'Learn different RAG approaches and when to use them',
    difficulty: 'intermediate',
    estimatedTime: '30 minutes',
    objectives: [
      'Compare context-only vs open RAG',
      'Understand prompt engineering',
      'Handle edge cases',
      'Optimize for accuracy'
    ],
    prerequisites: ['lab0-search-comparison']
  },
  {
    id: 'lab3-performance-optimization',
    title: 'Lab 3: Performance Optimization',
    description: 'Optimize queries for speed, cost, and accuracy',
    difficulty: 'advanced',
    estimatedTime: '45 minutes',
    objectives: [
      'Analyze performance bottlenecks',
      'Optimize embedding generation',
      'Tune database queries',
      'Balance cost vs performance'
    ],
    prerequisites: ['lab1-similarity-search', 'lab2-rag-patterns']
  },
  {
    id: 'capstone-production-deployment',
    title: 'Capstone: Production Deployment',
    description: 'Deploy a complete RAG system to production',
    difficulty: 'advanced',
    estimatedTime: '60 minutes',
    objectives: [
      'Configure production settings',
      'Set up monitoring and alerts',
      'Implement security measures',
      'Test end-to-end workflows'
    ],
    prerequisites: ['lab3-performance-optimization']
  }
]

// Helper functions
export const getLabById = (id: string): Lab | undefined => {
  return availableLabs.find(lab => lab.id === id)
}

export const getNextLab = (currentLabId: string): Lab | undefined => {
  const currentIndex = availableLabs.findIndex(lab => lab.id === currentLabId)
  return currentIndex >= 0 && currentIndex < availableLabs.length - 1 
    ? availableLabs[currentIndex + 1] 
    : undefined
}

export const getPreviousLab = (currentLabId: string): Lab | undefined => {
  const currentIndex = availableLabs.findIndex(lab => lab.id === currentLabId)
  return currentIndex > 0 
    ? availableLabs[currentIndex - 1] 
    : undefined
}