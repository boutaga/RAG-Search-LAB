import { Switch } from '@headlessui/react'
import { AcademicCapIcon, CogIcon } from '@heroicons/react/24/outline'
import { useLabModeStore } from '@/stores/labModeStore'
import { classNames } from '@/utils/classNames'

interface LabModeToggleProps {
  className?: string
}

export default function LabModeToggle({ className = '' }: LabModeToggleProps) {
  const { isLabMode, toggleLabMode } = useLabModeStore()

  return (
    <div className={classNames('flex items-center space-x-3', className)}>
      <div className="flex items-center">
        <CogIcon className="h-5 w-5 text-gray-500 mr-2" />
        <span className="text-sm font-medium text-gray-700">Production</span>
      </div>
      
      <Switch
        checked={isLabMode}
        onChange={toggleLabMode}
        className={classNames(
          isLabMode ? 'bg-blue-600' : 'bg-gray-200',
          'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
        )}
      >
        <span className="sr-only">Enable LAB mode</span>
        <span
          aria-hidden="true"
          className={classNames(
            isLabMode ? 'translate-x-5' : 'translate-x-0',
            'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out'
          )}
        />
      </Switch>
      
      <div className="flex items-center">
        <AcademicCapIcon className="h-5 w-5 text-blue-500 mr-2" />
        <span className="text-sm font-medium text-gray-700">LAB Mode</span>
        {isLabMode && (
          <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
            Active
          </span>
        )}
      </div>
      
      {isLabMode && (
        <div className="hidden lg:block">
          <div className="text-xs text-gray-500">
            Educational mode with step-by-step explanations
          </div>
        </div>
      )}
    </div>
  )
}