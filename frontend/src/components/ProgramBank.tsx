import React, { useState, useMemo, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAppStore } from '../store'
import { SubProgram } from '../types'
import { 
  Search, 
  Database,
  BarChart3,
  FileText,
  Settings,
  Zap,
  ArrowRight,
  CheckCircle2,
  Circle,
  Filter
} from 'lucide-react'

const ProgramBank: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [apiBank, setApiBank] = useState<any>(null)

  const {
    subPrograms,
    selectedPrograms,
    toggleProgramSelection,
    addSubProgram
  } = useAppStore()

  console.log('ProgramBank render - subPrograms count:', Object.keys(subPrograms).length)

  // Fetch API bank from backend
  useEffect(() => {
    const fetchApiBank = async () => {
      try {
        console.log('Fetching API bank from backend...')
        const response = await fetch('http://localhost:8000/api/bank')
        if (response.ok) {
          const data = await response.json()
          console.log('API bank data received:', data)
          setApiBank(data)
          
          // Convert API bank to SubProgram format for display
          Object.entries(data.apis).forEach(([name, api]: [string, any]) => {
            const program: SubProgram = {
              id: name,
              name: api.name,
              code: `${api.name}(${Object.keys(api.inputs).join(', ')}) → ${api.output_type}`,
              description: api.description,
              parameters: Object.keys(api.inputs),
              returnType: api.output_type,
              complexity: Math.ceil(Object.keys(api.inputs).length / 2) + 1,
              usageCount: Math.floor(Math.random() * 50), // Simulated usage
              tags: [api.category],
              fitness: 0.5 + Math.random() * 0.5 // Simulated fitness
            }
            addSubProgram(program)
          })
          console.log('APIs loaded successfully:', Object.keys(data.apis).length)
        } else {
          console.error('Failed to fetch API bank:', response.status, response.statusText)
        }
      } catch (error) {
        console.error('Failed to fetch API bank:', error)
      }
    }

    // Always fetch on component mount
    fetchApiBank()
  }, [addSubProgram])

  // Get category icon and color
  const getCategoryConfig = (category: string) => {
    const configs = {
      'data_source': { 
        icon: Database, 
        color: 'bg-blue-50 text-blue-700 border-blue-200',
        bgColor: 'bg-blue-500'
      },
      'analysis': { 
        icon: BarChart3, 
        color: 'bg-purple-50 text-purple-700 border-purple-200',
        bgColor: 'bg-purple-500'
      },
      'processing': { 
        icon: Settings, 
        color: 'bg-orange-50 text-orange-700 border-orange-200',
        bgColor: 'bg-orange-500'
      },
      'visualization': { 
        icon: BarChart3, 
        color: 'bg-green-50 text-green-700 border-green-200',
        bgColor: 'bg-green-500'
      },
      'output': { 
        icon: FileText, 
        color: 'bg-red-50 text-red-700 border-red-200',
        bgColor: 'bg-red-500'
      }
    }
    return configs[category as keyof typeof configs] || { 
      icon: Zap, 
      color: 'bg-gray-50 text-gray-700 border-gray-200',
      bgColor: 'bg-gray-500'
    }
  }

  // Get all unique categories
  const allCategories = Array.from(
    new Set(Object.values(subPrograms).flatMap(program => program.tags))
  )

  // Filter and sort programs
  const filteredPrograms = useMemo(() => {
    let programs = Object.values(subPrograms)

    // Apply search filter
    if (searchTerm) {
      programs = programs.filter(prog => 
        prog.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        prog.description.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Apply category filter
    if (selectedCategory) {
      programs = programs.filter(prog => prog.tags.includes(selectedCategory))
    }

    // Sort by category, then by name
    programs.sort((a, b) => {
      const categoryA = a.tags[0] || ''
      const categoryB = b.tags[0] || ''
      if (categoryA !== categoryB) {
        return categoryA.localeCompare(categoryB)
      }
      return a.name.localeCompare(b.name)
    })

    return programs
  }, [subPrograms, searchTerm, selectedCategory])

  return (
    <div className="h-full flex flex-col">
      {/* Search and Filters */}
      <div className="p-4 space-y-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
          <input
            type="text"
            placeholder="Search APIs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white/80 backdrop-blur-sm"
          />
        </div>

        {/* Category Filter */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              !selectedCategory 
                ? 'bg-blue-100 text-blue-700 border border-blue-200' 
                : 'bg-white/80 text-gray-600 border border-gray-200 hover:bg-gray-50'
            }`}
          >
            All APIs
          </button>
          {allCategories.map(category => {
            const config = getCategoryConfig(category)
            const Icon = config.icon
            return (
              <button
                key={category}
                onClick={() => setSelectedCategory(category === selectedCategory ? null : category)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                  selectedCategory === category 
                    ? config.color + ' border'
                    : 'bg-white/80 text-gray-600 border border-gray-200 hover:bg-gray-50'
                }`}
              >
                <Icon size={12} />
                {category.replace('_', ' ').toUpperCase()}
              </button>
            )
          })}
        </div>

        {/* Selection Summary */}
        {selectedPrograms.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="text-blue-600" size={16} />
                <span className="text-sm font-medium text-blue-900">
                  {selectedPrograms.length} APIs selected
                </span>
              </div>
              <div className="text-xs text-blue-700">
                Ready for composition
              </div>
            </div>
          </div>
        )}
      </div>

      {/* API List */}
      <div className="flex-1 overflow-auto px-4 pb-4">
        {filteredPrograms.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <Database className="mx-auto mb-3 text-gray-300" size={48} />
              <p className="font-medium">No APIs found</p>
              <p className="text-sm">Try adjusting your search or filters</p>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredPrograms.map(program => {
              const isSelected = selectedPrograms.includes(program.id)
              const config = getCategoryConfig(program.tags[0])
              const Icon = config.icon
              
              return (
                <motion.div
                  key={program.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`group relative bg-white/80 backdrop-blur-sm border rounded-xl p-4 cursor-pointer transition-all hover:shadow-md hover:bg-white/90 ${
                    isSelected 
                      ? 'border-blue-300 bg-blue-50/80 ring-2 ring-blue-200' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => toggleProgramSelection(program.id)}
                >
                  {/* Selection Indicator */}
                  <div className="absolute top-3 right-3">
                    {isSelected ? (
                      <CheckCircle2 className="text-blue-600" size={20} />
                    ) : (
                      <Circle className="text-gray-300 group-hover:text-gray-400" size={20} />
                    )}
                  </div>

                  {/* API Header */}
                  <div className="flex items-start gap-3 mb-3">
                    <div className={`p-2 rounded-lg ${config.bgColor}`}>
                      <Icon className="text-white" size={16} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-gray-900 truncate">
                        {program.name}
                      </h3>
                      <p className="text-sm text-gray-600 line-clamp-2">
                        {program.description}
                      </p>
                    </div>
                  </div>

                  {/* API Signature */}
                  <div className="bg-gray-50 rounded-lg p-3 mb-3">
                    <div className="flex items-center gap-2 text-sm font-mono">
                      <span className="text-gray-700">{program.name}</span>
                      <span className="text-gray-400">(</span>
                      <span className="text-blue-600">
                        {program.parameters.join(', ') || 'no params'}
                      </span>
                      <span className="text-gray-400">)</span>
                      <ArrowRight className="text-gray-400" size={14} />
                      <span className="text-green-600">{program.returnType}</span>
                    </div>
                  </div>

                  {/* Metadata */}
                  <div className="flex items-center justify-between">
                    <div className={`px-2 py-1 rounded-md text-xs font-medium ${config.color}`}>
                      {program.tags[0]?.replace('_', ' ').toUpperCase()}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-gray-500">
                      <span>{program.parameters.length} params</span>
                      <span>•</span>
                      <span>{(program.fitness * 100).toFixed(0)}% fit</span>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>
        )}
      </div>

      {/* Footer Stats */}
      <div className="p-4 border-t border-gray-200/50 bg-white/50 backdrop-blur-sm">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>{filteredPrograms.length} APIs available</span>
          <span>{selectedPrograms.length} selected</span>
        </div>
      </div>
    </div>
  )
}

export default ProgramBank