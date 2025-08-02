import React, { useMemo } from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, spring, random } from 'remotion';

// Advanced MCTS Tree with Node Values and UCB Scores
export const AdvancedMCTSTree = ({ startFrame }: { startFrame: number }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = Math.max(0, (frame - startFrame) / (fps * 6));
  
  const treeData = useMemo(() => {
    const nodes = [
      { id: 0, x: 400, y: 100, level: 0, visits: 147, value: 0.73, ucb: 0.85, code: 'root', children: [1, 2, 3] },
      { id: 1, x: 200, y: 200, level: 1, visits: 52, value: 0.68, ucb: 0.82, code: 'add(x,y)', children: [4, 5] },
      { id: 2, x: 400, y: 200, level: 1, visits: 43, value: 0.71, ucb: 0.88, code: 'mul(x,y)', children: [6, 7] },
      { id: 3, x: 600, y: 200, level: 1, visits: 52, value: 0.76, ucb: 0.79, code: 'if_then_else', children: [8] },
      { id: 4, x: 100, y: 300, level: 2, visits: 23, value: 0.45, ucb: 0.67, code: 'add(add(x,1),y)', children: [] },
      { id: 5, x: 300, y: 300, level: 2, visits: 29, value: 0.84, ucb: 0.91, code: 'factorial_pattern!', children: [] },
      { id: 6, x: 350, y: 300, level: 2, visits: 18, value: 0.62, ucb: 0.73, code: 'mul(mul(x,2),y)', children: [] },
      { id: 7, x: 450, y: 300, level: 2, visits: 25, value: 0.78, ucb: 0.85, code: 'power_pattern!', children: [] },
      { id: 8, x: 600, y: 300, level: 2, visits: 52, value: 0.76, ucb: 0.79, code: 'conditional_logic', children: [] },
    ];
    return nodes;
  }, []);
  
  const renderNode = (node: any, index: number) => {
    const nodeProgress = Math.max(0, Math.min(1, (progress - index * 0.1)));
    const scale = spring({
      frame: frame - startFrame - index * 8,
      fps,
      config: { damping: 12, stiffness: 80 }
    });
    
    const isHighValue = node.code.includes('pattern!');
    const nodeColor = isHighValue ? '#10B981' : '#3B82F6';
    const strokeColor = isHighValue ? '#059669' : '#1E40AF';
    
    return (
      <g key={node.id} opacity={nodeProgress}>
        {/* Node circle */}
        <circle
          cx={node.x}
          cy={node.y}
          r={30 * scale}
          fill={nodeColor}
          stroke={strokeColor}
          strokeWidth="3"
        />
        
        {/* UCB score indicator */}
        <rect
          x={node.x - 20}
          y={node.y - 50}
          width={40 * node.ucb}
          height={8}
          fill="#F59E0B"
          rx="4"
        />
        
        {/* Node label */}
        <text
          x={node.x}
          y={node.y - 5}
          textAnchor="middle"
          fill="white"
          fontSize="10"
          fontWeight="bold"
        >
          {node.code.slice(0, 12)}
        </text>
        
        {/* Visit count */}
        <text
          x={node.x}
          y={node.y + 8}
          textAnchor="middle"
          fill="white"
          fontSize="8"
        >
          {node.visits} visits
        </text>
        
        {/* Value display */}
        <text
          x={node.x + 45}
          y={node.y + 5}
          fill="#1F2937"
          fontSize="10"
          fontWeight="bold"
        >
          V: {node.value.toFixed(2)}
        </text>
      </g>
    );
  };
  
  const renderEdges = () => {
    return treeData.map(node => 
      node.children.map(childId => {
        const child = treeData.find(n => n.id === childId);
        if (!child) return null;
        
        const edgeProgress = Math.max(0, (progress - node.id * 0.1));
        
        return (
          <line
            key={`${node.id}-${childId}`}
            x1={node.x}
            y1={node.y + 30}
            x2={child.x}
            y2={child.y - 30}
            stroke="#60A5FA"
            strokeWidth="2"
            opacity={edgeProgress}
            markerEnd="url(#arrowhead)"
          />
        );
      })
    ).flat();
  };
  
  return (
    <g>
      {/* Arrowhead marker definition */}
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="7"
          refX="9"
          refY="3.5"
          orient="auto"
        >
          <polygon
            points="0 0, 10 3.5, 0 7"
            fill="#60A5FA"
          />
        </marker>
      </defs>
      
      {/* Title */}
      <text x={400} y={50} textAnchor="middle" fill="#1F2937" fontSize="20" fontWeight="bold">
        🔍 MCTS Program Space Exploration
      </text>
      
      {/* GPT-4o indicators */}
      <rect x={50} y={60} width={300} height={30} fill="#EF4444" rx="15" opacity="0.9" />
      <text x={200} y={80} textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">
        🧠 GPT-4o Policy Network Active
      </text>
      
      <rect x={450} y={60} width={300} height={30} fill="#F59E0B" rx="15" opacity="0.9" />
      <text x={600} y={80} textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">
        📊 GPT-4o Value Network Evaluating
      </text>
      
      {/* Tree visualization */}
      {renderEdges()}
      {treeData.map(renderNode)}
      
      {/* Legend */}
      <g transform="translate(50, 400)">
        <rect width={200} height={120} fill="white" stroke="#D1D5DB" rx="8" />
        <text x={100} y={20} textAnchor="middle" fill="#1F2937" fontSize="12" fontWeight="bold">
          Node Information
        </text>
        <circle cx={20} cy={35} r={8} fill="#3B82F6" />
        <text x={35} y={40} fill="#1F2937" fontSize="10">Regular nodes</text>
        <circle cx={20} cy={55} r={8} fill="#10B981" />
        <text x={35} y={60} fill="#1F2937" fontSize="10">High-value patterns</text>
        <rect x={12} y={70} width={16} height={4} fill="#F59E0B" />
        <text x={35} y={78} fill="#1F2937" fontSize="10">UCB confidence</text>
        <text x={10} y={95} fill="#1F2937" fontSize="9">V: Value estimate</text>
        <text x={10} y={108} fill="#1F2937" fontSize="9">Visits: Exploration count</text>
      </g>
    </g>
  );
};

// Code Morphing Animation
export const CodeMorphing = ({ startFrame, fromCode, toCode, title }: { 
  startFrame: number; 
  fromCode: string; 
  toCode: string; 
  title: string; 
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = Math.max(0, Math.min(1, (frame - startFrame) / (fps * 3)));
  
  const morphedCode = useMemo(() => {
    if (progress === 0) return fromCode;
    if (progress === 1) return toCode;
    
    const fromLines = fromCode.split('\n');
    const toLines = toCode.split('\n');
    const maxLines = Math.max(fromLines.length, toLines.length);
    
    return Array.from({ length: maxLines }, (_, i) => {
      const fromLine = fromLines[i] || '';
      const toLine = toLines[i] || '';
      
      if (progress < 0.3) return fromLine;
      if (progress > 0.7) return toLine;
      
      // Character-by-character morphing
      const morphProgress = (progress - 0.3) / 0.4;
      const maxLength = Math.max(fromLine.length, toLine.length);
      
      return Array.from({ length: maxLength }, (_, j) => {
        const fromChar = fromLine[j] || ' ';
        const toChar = toLine[j] || ' ';
        
        if (j / maxLength < morphProgress) return toChar;
        return fromChar;
      }).join('');
    }).join('\n');
  }, [progress, fromCode, toCode]);
  
  return (
    <g>
      <text x={400} y={80} textAnchor="middle" fill="#1F2937" fontSize="20" fontWeight="bold">
        {title}
      </text>
      
      {/* Code background */}
      <rect
        x={100}
        y={120}
        width={600}
        height={300}
        fill="#1F2937"
        rx="12"
        stroke="#374151"
        strokeWidth="2"
      />
      
      {/* Code text */}
      <foreignObject x={120} y={140} width={560} height={260}>
        <pre style={{
          color: '#E5E7EB',
          fontSize: '14px',
          fontFamily: 'JetBrains Mono, monospace',
          lineHeight: '1.4',
          margin: 0,
          padding: '10px'
        }}>
          {morphedCode}
        </pre>
      </foreignObject>
      
      {/* Morphing particles */}
      {Array.from({ length: 20 }, (_, i) => {
        const particleProgress = (progress + i * 0.05) % 1;
        const x = interpolate(particleProgress, [0, 1], [150, 650]);
        const y = 280 + Math.sin(particleProgress * Math.PI * 4) * 20;
        const opacity = Math.sin(particleProgress * Math.PI);
        
        return (
          <circle
            key={i}
            cx={x}
            cy={y}
            r="3"
            fill="#10B981"
            opacity={opacity}
          />
        );
      })}
      
      {/* Progress indicator */}
      <rect
        x={150}
        y={450}
        width={500}
        height={8}
        fill="#374151"
        rx="4"
      />
      <rect
        x={150}
        y={450}
        width={500 * progress}
        height={8}
        fill="#10B981"
        rx="4"
      />
    </g>
  );
};

// Evolution Population Visualization
export const EvolutionPopulation = ({ startFrame }: { startFrame: number }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = Math.max(0, (frame - startFrame) / (fps * 5));
  
  const population = useMemo(() => {
    return Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: 100 + (i % 10) * 60,
      y: 150 + Math.floor(i / 10) * 60,
      fitness: random(`fitness-${i}`) * 0.9 + 0.1,
      generation: Math.floor(i / 10),
      mutated: random(`mutated-${i}`) > 0.7
    }));
  }, []);
  
  return (
    <g>
      <text x={400} y={50} textAnchor="middle" fill="#1F2937" fontSize="20" fontWeight="bold">
        🧬 Evolution Population Dynamics
      </text>
      
      {/* Generation labels */}
      {Array.from({ length: 5 }, (_, gen) => (
        <text
          key={gen}
          x={50}
          y={180 + gen * 60}
          fill="#6B7280"
          fontSize="12"
          fontWeight="bold"
        >
          Gen {gen}
        </text>
      ))}
      
      {/* Population individuals */}
      {population.map((individual, index) => {
        const appearProgress = Math.max(0, (progress - index * 0.02));
        const scale = spring({
          frame: frame - startFrame - index * 2,
          fps,
          config: { damping: 10, stiffness: 100 }
        });
        
        const color = individual.fitness > 0.7 ? '#10B981' : 
                     individual.fitness > 0.4 ? '#F59E0B' : '#EF4444';
        
        return (
          <g key={individual.id} opacity={appearProgress}>
            <circle
              cx={individual.x}
              cy={individual.y}
              r={15 * scale}
              fill={color}
              stroke={individual.mutated ? '#8B5CF6' : 'none'}
              strokeWidth={individual.mutated ? '3' : '0'}
              strokeDasharray={individual.mutated ? '5,5' : '0'}
            />
            
            {/* Fitness bar */}
            <rect
              x={individual.x - 10}
              y={individual.y - 25}
              width={20 * individual.fitness}
              height={4}
              fill={color}
              rx="2"
            />
            
            {/* Selection arrows for high fitness */}
            {individual.fitness > 0.7 && progress > 0.5 && (
              <path
                d={`M ${individual.x} ${individual.y - 35} L ${individual.x - 5} ${individual.y - 45} L ${individual.x + 5} ${individual.y - 45} Z`}
                fill="#10B981"
                opacity={Math.sin((frame - startFrame) * 0.1) * 0.5 + 0.5}
              />
            )}
          </g>
        );
      })}
      
      {/* Statistics panel */}
      <g transform="translate(550, 150)">
        <rect width={200} height={150} fill="white" stroke="#D1D5DB" rx="8" />
        <text x={100} y={25} textAnchor="middle" fill="#1F2937" fontSize="14" fontWeight="bold">
          Population Stats
        </text>
        
        <text x={15} y={45} fill="#10B981" fontSize="12">
          High Fitness: {population.filter(p => p.fitness > 0.7).length}
        </text>
        <text x={15} y={65} fill="#F59E0B" fontSize="12">
          Medium Fitness: {population.filter(p => p.fitness > 0.4 && p.fitness <= 0.7).length}
        </text>
        <text x={15} y={85} fill="#EF4444" fontSize="12">
          Low Fitness: {population.filter(p => p.fitness <= 0.4).length}
        </text>
        <text x={15} y={105} fill="#8B5CF6" fontSize="12">
          Mutated: {population.filter(p => p.mutated).length}
        </text>
        
        <text x={15} y={130} fill="#1F2937" fontSize="10">
          🎯 GPT-4o guiding selection
        </text>
      </g>
    </g>
  );
};

// Bootstrap Cycle Indicator
export const BootstrapCycle = ({ currentPhase, cycleNumber }: { currentPhase: number; cycleNumber: number }) => {
  const frame = useCurrentFrame();
  const phases = ['MCTS', 'Evolution', 'Integration', 'Bootstrap'];
  const phaseColors = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6'];
  
  return (
    <g transform="translate(50, 50)">
      <text x={150} y={30} textAnchor="middle" fill="#1F2937" fontSize="16" fontWeight="bold">
        Bootstrap Cycle {cycleNumber}
      </text>
      
      {phases.map((phase, index) => {
        const isActive = index === currentPhase;
        const isCompleted = index < currentPhase;
        
        const centerX = 75 * index + 75;
        const centerY = 60;
        
        return (
          <g key={phase}>
            {/* Phase circle */}
            <circle
              cx={centerX}
              cy={centerY}
              r={25}
              fill={isActive ? phaseColors[index] : (isCompleted ? phaseColors[index] : '#E5E7EB')}
              stroke={isActive ? '#1F2937' : 'none'}
              strokeWidth={isActive ? '3' : '0'}
            />
            
            {/* Phase label */}
            <text
              x={centerX}
              y={centerY + 5}
              textAnchor="middle"
              fill={isActive || isCompleted ? 'white' : '#6B7280'}
              fontSize="10"
              fontWeight="bold"
            >
              {phase}
            </text>
            
            {/* Connection arrow */}
            {index < phases.length - 1 && (
              <path
                d={`M ${centerX + 25} ${centerY} L ${centerX + 50} ${centerY}`}
                stroke={isCompleted ? phaseColors[index] : '#D1D5DB'}
                strokeWidth="3"
                markerEnd="url(#arrowhead)"
              />
            )}
            
            {/* Completion checkmark */}
            {isCompleted && (
              <path
                d={`M ${centerX - 8} ${centerY} L ${centerX - 3} ${centerY + 5} L ${centerX + 8} ${centerY - 5}`}
                stroke="white"
                strokeWidth="3"
                fill="none"
              />
            )}
            
            {/* Active pulse */}
            {isActive && (
              <circle
                cx={centerX}
                cy={centerY}
                r={30}
                fill="none"
                stroke={phaseColors[index]}
                strokeWidth="2"
                opacity={Math.sin(frame * 0.2) * 0.3 + 0.7}
              />
            )}
          </g>
        );
      })}
      
      {/* Cycle completion arrow */}
      <path
        d="M 275 60 Q 320 30 320 100 Q 320 130 75 130 Q 50 130 50 105 L 55 110 L 50 105 L 55 100"
        stroke="#8B5CF6"
        strokeWidth="2"
        fill="none"
        opacity={currentPhase === 3 ? 1 : 0.3}
      />
    </g>
  );
};