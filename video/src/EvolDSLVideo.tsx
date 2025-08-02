import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  Sequence,
} from 'remotion';
import {
  AdvancedMCTSTree,
  CodeMorphing,
  EvolutionPopulation,
  BootstrapCycle,
} from './Components';

export const EvolDSLVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Background gradient
  const backgroundOpacity = interpolate(
    frame,
    [0, 60],
    [0, 1]
  );

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`,
        opacity: backgroundOpacity,
      }}
    >
      {/* Extended Title Sequence - 10 seconds */}
      <Sequence from={0} durationInFrames={300}>
        <TitleSequence />
      </Sequence>

      {/* DSL Introduction - 15 seconds */}
      <Sequence from={240} durationInFrames={450}>
        <DSLIntroduction startFrame={240} />
      </Sequence>

      {/* Detailed MCTS Tree Visualization - 30 seconds */}
      <Sequence from={630} durationInFrames={900}>
        <DetailedMCTSSection startFrame={630} />
      </Sequence>

      {/* Step-by-Step Code Evolution - 25 seconds */}
      <Sequence from={1470} durationInFrames={750}>
        <StepByStepEvolution startFrame={1470} />
      </Sequence>

      {/* Evolution Population Detailed - 25 seconds */}
      <Sequence from={2160} durationInFrames={750}>
        <DetailedEvolutionSection startFrame={2160} />
      </Sequence>

      {/* Complete Bootstrap Cycle - 35 seconds */}
      <Sequence from={2850} durationInFrames={1050}>
        <CompleteBootstrapDemo startFrame={2850} />
      </Sequence>

      {/* Function Hierarchy Demonstration - 20 seconds */}
      <Sequence from={3840} durationInFrames={600}>
        <FunctionHierarchyDemo startFrame={3840} />
      </Sequence>

      {/* Live Testing Results - 15 seconds */}
      <Sequence from={4380} durationInFrames={450}>
        <LiveTestingResults startFrame={4380} />
      </Sequence>

      {/* Extended Final Results - 15 seconds */}
      <Sequence from={4770} durationInFrames={450}>
        <ExtendedFinalResults startFrame={4770} />
      </Sequence>

      {/* Call to Action - 15 seconds */}
      <Sequence from={5160} durationInFrames={240}>
        <CallToAction startFrame={5160} />
      </Sequence>
    </AbsoluteFill>
  );
};

const TitleSequence: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = spring({
    frame,
    fps,
    config: { damping: 8, stiffness: 60 },
  });

  const subtitleOpacity = spring({
    frame: frame - 60,
    fps,
    config: { damping: 12, stiffness: 40 },
  });

  const featuresOpacity = spring({
    frame: frame - 120,
    fps,
    config: { damping: 15, stiffness: 50 },
  });

  return (
    <AbsoluteFill
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        textAlign: 'center',
      }}
    >
      <div
        style={{
          fontSize: '96px',
          fontWeight: 'bold',
          color: 'white',
          opacity: Math.min(1, titleOpacity),
          textShadow: '4px 4px 8px rgba(0,0,0,0.7)',
          marginBottom: '30px',
        }}
      >
        🧬 EvolDSL
      </div>
      
      <div
        style={{
          fontSize: '42px',
          color: 'white',
          opacity: Math.min(1, subtitleOpacity),
          textShadow: '2px 2px 4px rgba(0,0,0,0.7)',
          marginBottom: '50px',
          maxWidth: '1200px',
          lineHeight: '1.3',
        }}
      >
        Self-Bootstrapping Programming with MCTS + Evolution
      </div>

      <div
        style={{
          fontSize: '24px',
          color: 'rgba(255,255,255,0.95)',
          opacity: Math.min(1, featuresOpacity),
          marginTop: '40px',
          maxWidth: '1000px',
          lineHeight: '1.8',
        }}
      >
        <div style={{ marginBottom: '20px' }}>🤖 <strong>GPT-4o Guided</strong> • AI learns to program by programming itself</div>
        <div style={{ marginBottom: '20px' }}>🌳 <strong>Self-Bootstrapping</strong> • From 9 primitives to complex hierarchical functions</div>
        <div style={{ marginBottom: '20px' }}>⚡ <strong>Real Evolution</strong> • Watch DSL grow in real-time</div>
        <div>🔬 <strong>Research Grade</strong> • Monte Carlo Tree Search + Evolutionary Programming</div>
      </div>
    </AbsoluteFill>
  );
};

const DSLIntroduction: React.FC<{ startFrame: number }> = ({ startFrame }) => {
  const frame = useCurrentFrame();
  const relativeFrame = frame - startFrame;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '60px',
      }}
    >
      <div style={{ fontSize: '48px', fontWeight: 'bold', color: '#1F2937', marginBottom: '40px' }}>
        🏗️ What is a Domain Specific Language?
      </div>
      
      <div style={{ display: 'flex', gap: '80px', alignItems: 'center', maxWidth: '1600px' }}>
        <div style={{ flex: 1 }}>
          <h3 style={{ fontSize: '32px', color: '#4B5563', marginBottom: '30px' }}>Starting Primitives</h3>
          <div style={{ 
            backgroundColor: '#1F2937', 
            color: '#E5E7EB', 
            padding: '30px', 
            borderRadius: '12px',
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '18px',
            lineHeight: '1.6'
          }}>
            <div>def add(x, y): return x + y</div>
            <div>def mul(x, y): return x * y</div>
            <div>def sub(x, y): return x - y</div>
            <div>def div(x, y): return x // y</div>
            <div>def eq(x, y): return x == y</div>
            <div>def lt(x, y): return x &lt; y</div>
            <div>def gt(x, y): return x &gt; y</div>
            <div>def if_then_else(c, t, e):</div>
            <div>    return t if c else e</div>
            <div>def identity(x): return x</div>
          </div>
          <div style={{ fontSize: '20px', color: '#6B7280', marginTop: '20px', textAlign: 'center' }}>
            <strong>9 primitive functions</strong>
          </div>
        </div>
        
        <div style={{ fontSize: '64px', color: '#10B981' }}>→</div>
        
        <div style={{ flex: 1 }}>
          <h3 style={{ fontSize: '32px', color: '#4B5563', marginBottom: '30px' }}>After Evolution</h3>
          <div style={{ 
            backgroundColor: '#1F2937', 
            color: '#E5E7EB', 
            padding: '30px', 
            borderRadius: '12px',
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '18px',
            lineHeight: '1.6'
          }}>
            <div style={{ color: '#10B981' }}>def factorial(n):</div>
            <div>    if eq(n, 0): return 1</div>
            <div>    return mul(n, factorial(sub(n, 1)))</div>
            <div style={{ margin: '15px 0' }}></div>
            <div style={{ color: '#10B981' }}>def power(base, exp):</div>
            <div>    if eq(exp, 0): return 1</div>
            <div>    return mul(base, power(base, sub(exp, 1)))</div>
            <div style={{ margin: '15px 0' }}></div>
            <div style={{ color: '#F59E0B' }}>def advanced_combo(n):</div>
            <div>    return max_two(factorial(n), power(n, 2))</div>
          </div>
          <div style={{ fontSize: '20px', color: '#6B7280', marginTop: '20px', textAlign: 'center' }}>
            <strong>14+ functions</strong> • <span style={{ color: '#10B981' }}>Hierarchical composition!</span>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const DetailedMCTSSection: React.FC<{ startFrame: number }> = ({ startFrame }) => {
  const frame = useCurrentFrame();
  const relativeFrame = frame - startFrame;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '40px',
      }}
    >
      <div style={{ fontSize: '48px', fontWeight: 'bold', color: '#1F2937', marginBottom: '40px' }}>
        🔍 Monte Carlo Tree Search with GPT-4o
      </div>
      
      <div style={{ display: 'flex', gap: '60px', width: '100%', maxWidth: '1800px' }}>
        {/* MCTS Tree - Larger */}
        <div style={{ flex: 2 }}>
          <svg width="1200" height="800" viewBox="0 0 1200 800">
            <AdvancedMCTSTree startFrame={startFrame} />
          </svg>
        </div>
        
        {/* Explanation Panel */}
        <div style={{ flex: 1, paddingLeft: '40px' }}>
          <div style={{
            backgroundColor: 'white',
            padding: '40px',
            borderRadius: '16px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
          }}>
            <h3 style={{ fontSize: '28px', color: '#1F2937', marginBottom: '30px' }}>
              How MCTS Works
            </h3>
            
            <div style={{ fontSize: '18px', lineHeight: '1.8', color: '#4B5563' }}>
              <div style={{ marginBottom: '25px' }}>
                <strong style={{ color: '#3B82F6' }}>🔍 Selection:</strong><br/>
                GPT-4o policy network suggests which nodes to explore based on UCB scores
              </div>
              
              <div style={{ marginBottom: '25px' }}>
                <strong style={{ color: '#10B981' }}>🌿 Expansion:</strong><br/>
                Add new child nodes representing programming actions
              </div>
              
              <div style={{ marginBottom: '25px' }}>
                <strong style={{ color: '#F59E0B' }}>⚡ Simulation:</strong><br/>
                GPT-4o value network evaluates program quality and potential
              </div>
              
              <div style={{ marginBottom: '25px' }}>
                <strong style={{ color: '#8B5CF6' }}>📈 Backpropagation:</strong><br/>
                Update all parent nodes with evaluation results
              </div>
            </div>
            
            <div style={{
              backgroundColor: '#EF4444',
              color: 'white',
              padding: '20px',
              borderRadius: '12px',
              marginTop: '30px',
              textAlign: 'center',
              fontSize: '16px',
              fontWeight: 'bold'
            }}>
              🧠 GPT-4o guides every decision!
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const StepByStepEvolution: React.FC<{ startFrame: number }> = ({ startFrame }) => {
  const frame = useCurrentFrame();
  const relativeFrame = frame - startFrame;
  
  // Show different evolution steps
  const currentStep = Math.floor(relativeFrame / 150); // Each step lasts 5 seconds
  
  const evolutionSteps = [
    {
      title: "Step 1: MCTS discovers patterns",
      from: `# Simple multiplication pattern
def simple_mul(x, y):
    return mul(x, y)`,
      to: `# MCTS finds recursive pattern!
def factorial_pattern(n):
    if eq(n, 0):
        return 1
    else:
        return mul(n, factorial_pattern(sub(n, 1)))`
    },
    {
      title: "Step 2: Evolution refines the function",
      from: `# Rough factorial pattern
def factorial_pattern(n):
    if eq(n, 0):
        return 1
    else:
        return mul(n, factorial_pattern(sub(n, 1)))`,
      to: `# GPT-4o suggests improvements
def factorial(n):
    """Computes n! recursively"""
    if eq(n, 0):
        return 1
    else:
        return mul(n, factorial(sub(n, 1)))`
    },
    {
      title: "Step 3: Function gets promoted to DSL",
      from: `# DSL before evolution
Available functions:
- add, sub, mul, div
- eq, lt, gt  
- if_then_else, identity`,
      to: `# DSL after evolution
Available functions:
- add, sub, mul, div
- eq, lt, gt
- if_then_else, identity
+ factorial  ← NEW!`
    },
    {
      title: "Step 4: New function enables higher compositions",
      from: `# Before: Limited capabilities
def simple_math(x, y):
    return add(mul(x, 2), y)`,
      to: `# After: Complex compositions possible!
def advanced_combo(n):
    fact_n = factorial(n)
    power_n = power(n, 2)
    return max_two(fact_n, power_n)`
    }
  ];
  
  const step = evolutionSteps[Math.min(currentStep, evolutionSteps.length - 1)] || evolutionSteps[evolutionSteps.length - 1];

  return (
    <AbsoluteFill
      style={{
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '60px',
      }}
    >
      <div style={{ fontSize: '48px', fontWeight: 'bold', color: '#1F2937', marginBottom: '50px' }}>
        🧬 {step.title}
      </div>
      
      <svg width="1600" height="700" viewBox="0 0 1600 700">
        <CodeMorphing
          startFrame={startFrame + currentStep * 150}
          title=""
          fromCode={step.from}
          toCode={step.to}
        />
      </svg>
      
      {/* Progress indicator */}
      <div style={{ display: 'flex', gap: '15px', marginTop: '40px' }}>
        {evolutionSteps.map((_, i) => (
          <div
            key={i}
            style={{
              width: '20px',
              height: '20px',
              borderRadius: '50%',
              backgroundColor: i <= currentStep ? '#10B981' : '#D1D5DB',
              transition: 'all 0.3s ease',
            }}
          />
        ))}
      </div>
    </AbsoluteFill>
  );
};

const DetailedEvolutionSection: React.FC<{ startFrame: number }> = ({ startFrame }) => {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '40px',
      }}
    >
      <div style={{ fontSize: '48px', fontWeight: 'bold', color: '#1F2937', marginBottom: '40px' }}>
        🧬 Population-Based Evolution
      </div>
      
      <div style={{ display: 'flex', gap: '60px', width: '100%', maxWidth: '1800px' }}>
        {/* Evolution Population - Larger */}
        <div style={{ flex: 2 }}>
          <svg width="1200" height="700" viewBox="0 0 1200 700">
            <EvolutionPopulation startFrame={startFrame} />
          </svg>
        </div>
        
        {/* Evolution Process */}
        <div style={{ flex: 1 }}>
          <div style={{
            backgroundColor: 'white',
            padding: '40px',
            borderRadius: '16px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
          }}>
            <h3 style={{ fontSize: '28px', color: '#1F2937', marginBottom: '30px' }}>
              Evolution Process
            </h3>
            
            <div style={{ fontSize: '18px', lineHeight: '2', color: '#4B5563' }}>
              <div style={{ marginBottom: '25px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                  <div style={{ width: '20px', height: '20px', backgroundColor: '#10B981', borderRadius: '50%' }}></div>
                  <strong>High Fitness (&gt;0.7)</strong>
                </div>
                <span style={{ fontSize: '16px', color: '#6B7280' }}>
                  Functions that work well and solve target tasks effectively
                </span>
              </div>
              
              <div style={{ marginBottom: '25px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                  <div style={{ width: '20px', height: '20px', backgroundColor: '#F59E0B', borderRadius: '50%' }}></div>
                  <strong>Medium Fitness (0.4-0.7)</strong>
                </div>
                <span style={{ fontSize: '16px', color: '#6B7280' }}>
                  Promising patterns that need refinement
                </span>
              </div>
              
              <div style={{ marginBottom: '25px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                  <div style={{ width: '20px', height: '20px', backgroundColor: '#EF4444', borderRadius: '50%' }}></div>
                  <strong>Low Fitness (&lt;0.4)</strong>
                </div>
                <span style={{ fontSize: '16px', color: '#6B7280' }}>
                  Functions that don't work or are too simple
                </span>
              </div>
              
              <div style={{ marginBottom: '30px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                  <div style={{ 
                    width: '20px', 
                    height: '20px', 
                    backgroundColor: '#8B5CF6', 
                    borderRadius: '50%',
                    border: '3px dashed #A855F7'
                  }}></div>
                  <strong>Mutated Functions</strong>
                </div>
                <span style={{ fontSize: '16px', color: '#6B7280' }}>
                  GPT-4o suggested improvements and variations
                </span>
              </div>
            </div>
            
            <div style={{
              backgroundColor: '#8B5CF6',
              color: 'white',
              padding: '20px',
              borderRadius: '12px',
              textAlign: 'center',
              fontSize: '16px',
              fontWeight: 'bold'
            }}>
              🎯 Only the best survive to next generation!
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const CompleteBootstrapDemo: React.FC<{ startFrame: number }> = ({ startFrame }) => {
  const frame = useCurrentFrame();
  const relativeFrame = frame - startFrame;
  
  // Each phase lasts ~8.5 seconds (255 frames)
  const currentPhase = Math.min(3, Math.floor(relativeFrame / 255));
  
  return (
    <AbsoluteFill
      style={{
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '60px',
      }}
    >
      <div style={{ fontSize: '48px', fontWeight: 'bold', color: '#1F2937', marginBottom: '50px' }}>
        ♻️ Complete Bootstrap Cycle
      </div>
      
      {/* Large Bootstrap Cycle Indicator */}
      <svg width="1000" height="200" viewBox="0 0 1000 200">
        <BootstrapCycle currentPhase={currentPhase} cycleNumber={1} />
      </svg>
      
      <div style={{ marginTop: '60px', textAlign: 'center', maxWidth: '1200px' }}>
        <PhaseDescription phase={currentPhase} large={true} />
      </div>
      
      {/* DSL Growth Visualization - Larger */}
      <div style={{ marginTop: '60px' }}>
        <LargeDSLGrowthChart phase={currentPhase} />
      </div>
      
      {/* Real-time stats */}
      <div style={{ 
        marginTop: '50px',
        display: 'flex',
        gap: '60px',
        fontSize: '20px',
        color: '#4B5563'
      }}>
        <div>Functions: <strong>{9 + Math.min(currentPhase, 1)}</strong></div>
        <div>Cycles: <strong>1</strong></div>
        <div>Phase: <strong>{['MCTS', 'Evolution', 'Integration', 'Bootstrap'][currentPhase]}</strong></div>
      </div>
    </AbsoluteFill>
  );
};

const PhaseDescription: React.FC<{ phase: number; large?: boolean }> = ({ phase, large = false }) => {
  const descriptions = [
    {
      title: '🔍 MCTS Phase',
      description: 'GPT-4o policy network guides search through program space',
      details: 'Exploring 147 nodes, discovering factorial pattern with 0.84 fitness score...',
      color: '#3B82F6'
    },
    {
      title: '🧬 Evolution Phase', 
      description: 'GPT-4o suggests mutations and improvements to discovered patterns',
      details: 'Mutating successful patterns, adding recursion, optimizing base cases...',
      color: '#10B981'
    },
    {
      title: '🔗 Integration Phase',
      description: 'Best functions promoted to DSL as new primitives',
      details: 'factorial(n) now available! DSL expanded from 9 to 10 functions.',
      color: '#F59E0B'
    },
    {
      title: '♻️ Bootstrap Phase',
      description: 'DSL expanded - ready for next complexity level',
      details: 'Can now discover power(x,y), advanced_combo(n), and higher-order functions...',
      color: '#8B5CF6'
    }
  ];

  const current = descriptions[phase] || descriptions[0];
  const fontSize = large ? { title: '36px', desc: '24px', details: '20px' } : { title: '24px', desc: '16px', details: '14px' };

  return (
    <div style={{ maxWidth: large ? '1000px' : '600px' }}>
      <h2 style={{ 
        fontSize: fontSize.title, 
        color: current.color, 
        marginBottom: '20px',
        fontWeight: 'bold'
      }}>
        {current.title}
      </h2>
      <p style={{ 
        fontSize: fontSize.desc, 
        color: '#4B5563', 
        marginBottom: '15px',
        lineHeight: '1.6'
      }}>
        {current.description}
      </p>
      <p style={{ 
        fontSize: fontSize.details, 
        color: '#6B7280', 
        fontStyle: 'italic',
        lineHeight: '1.5'
      }}>
        {current.details}
      </p>
    </div>
  );
};

const LargeDSLGrowthChart: React.FC<{ phase: number }> = ({ phase }) => {
  const functionCounts = [9, 9, 10, 10];
  
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '30px' }}>
      <div style={{ fontSize: '24px', color: '#1F2937', fontWeight: 'bold' }}>
        DSL Functions:
      </div>
      
      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        {Array.from({ length: functionCounts[phase] }, (_, i) => (
          <div
            key={i}
            style={{
              width: '40px',
              height: '40px',
              backgroundColor: i < 9 ? '#3B82F6' : '#10B981',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '16px',
              color: 'white',
              fontWeight: 'bold',
              boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
            }}
          >
            {i + 1}
          </div>
        ))}
      </div>
      
      <div style={{ fontSize: '20px', color: '#6B7280' }}>
        <strong>({functionCounts[phase]} total)</strong>
        {functionCounts[phase] > 9 && (
          <span style={{ color: '#10B981', marginLeft: '10px' }}>
            +{functionCounts[phase] - 9} evolved!
          </span>
        )}
      </div>
    </div>
  );
};

const FunctionHierarchyDemo: React.FC<{ startFrame: number }> = ({ startFrame }) => {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '60px',
      }}
    >
      <div style={{ fontSize: '48px', fontWeight: 'bold', color: '#1F2937', marginBottom: '50px' }}>
        🌳 Hierarchical Function Composition
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '40px', alignItems: 'center' }}>
        {/* Level 0: Primitives */}
        <div style={{ textAlign: 'center' }}>
          <h3 style={{ fontSize: '28px', color: '#6B7280', marginBottom: '20px' }}>Level 0: Primitives</h3>
          <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', justifyContent: 'center' }}>
            {['add', 'mul', 'sub', 'div', 'eq', 'lt', 'gt', 'if_then_else', 'identity'].map(func => (
              <div key={func} style={{
                backgroundColor: '#E5E7EB',
                color: '#374151',
                padding: '12px 20px',
                borderRadius: '8px',
                fontSize: '16px',
                fontFamily: 'JetBrains Mono, monospace'
              }}>
                {func}
              </div>
            ))}
          </div>
        </div>
        
        {/* Arrow */}
        <div style={{ fontSize: '32px', color: '#10B981' }}>↓</div>
        
        {/* Level 1: Evolved Functions */}
        <div style={{ textAlign: 'center' }}>
          <h3 style={{ fontSize: '28px', color: '#10B981', marginBottom: '20px' }}>Level 1: Evolved Functions</h3>
          <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', justifyContent: 'center' }}>
            {[
              { name: 'factorial', fitness: '0.850' },
              { name: 'power', fitness: '0.780' },
              { name: 'max_two', fitness: '0.720' },
              { name: 'fib_helper', fitness: '0.690' }
            ].map(func => (
              <div key={func.name} style={{
                backgroundColor: '#10B981',
                color: 'white',
                padding: '15px 25px',
                borderRadius: '12px',
                fontSize: '18px',
                fontFamily: 'JetBrains Mono, monospace',
                textAlign: 'center'
              }}>
                <div style={{ fontWeight: 'bold' }}>{func.name}</div>
                <div style={{ fontSize: '14px', opacity: 0.9 }}>fitness: {func.fitness}</div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Arrow */}
        <div style={{ fontSize: '32px', color: '#F59E0B' }}>↓</div>
        
        {/* Level 2: Composed Functions */}
        <div style={{ textAlign: 'center' }}>
          <h3 style={{ fontSize: '28px', color: '#F59E0B', marginBottom: '20px' }}>Level 2: Composed Functions</h3>
          <div style={{
            backgroundColor: '#F59E0B',
            color: 'white',
            padding: '20px 30px',
            borderRadius: '16px',
            fontSize: '20px',
            fontFamily: 'JetBrains Mono, monospace',
            textAlign: 'center',
            boxShadow: '0 8px 32px rgba(0,0,0,0.2)'
          }}>
            <div style={{ fontWeight: 'bold', marginBottom: '10px' }}>advanced_combo</div>
            <div style={{ fontSize: '16px', opacity: 0.9 }}>uses: factorial + power + max_two</div>
            <div style={{ fontSize: '14px', opacity: 0.8, marginTop: '5px' }}>fitness: 0.920 ⭐</div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const LiveTestingResults: React.FC<{ startFrame: number }> = ({ startFrame }) => {
  const frame = useCurrentFrame();
  const relativeFrame = frame - startFrame;
  
  const tests = [
    { call: 'factorial(5)', result: '120', color: '#10B981' },
    { call: 'power(2, 3)', result: '8', color: '#10B981' },
    { call: 'max_two(7, 3)', result: '7', color: '#10B981' },
    { call: 'fib_helper(6)', result: '8', color: '#10B981' },
    { call: 'advanced_combo(4)', result: '24', color: '#F59E0B' }
  ];
  
  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#1F2937',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '60px',
      }}
    >
      <div style={{ fontSize: '48px', fontWeight: 'bold', color: 'white', marginBottom: '50px' }}>
        🧪 Live Testing Results
      </div>
      
      <div style={{
        backgroundColor: '#111827',
        padding: '40px',
        borderRadius: '16px',
        fontFamily: 'JetBrains Mono, monospace',
        fontSize: '24px',
        color: '#E5E7EB',
        width: '100%',
        maxWidth: '1000px',
        boxShadow: '0 8px 32px rgba(0,0,0,0.5)'
      }}>
        <div style={{ color: '#10B981', marginBottom: '30px', fontSize: '20px' }}>
          &gt;&gt;&gt; Testing evolved DSL functions...
        </div>
        
        {tests.map((test, i) => {
          const shouldShow = relativeFrame > i * 60;
          return shouldShow ? (
            <div key={i} style={{ 
              marginBottom: '25px',
              opacity: spring({
                frame: relativeFrame - i * 60,
                fps: 30,
                config: { damping: 10 }
              })
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                <span style={{ color: '#6B7280' }}>&gt;&gt;&gt;&gt; </span>
                <span>{test.call}</span>
                <span style={{ color: test.color }}>✅</span>
                <span style={{ color: test.color, fontWeight: 'bold' }}>{test.result}</span>
              </div>
            </div>
          ) : null;
        })}
        
        {relativeFrame > 300 && (
          <div style={{ 
            marginTop: '40px', 
            color: '#10B981', 
            fontSize: '20px',
            opacity: spring({
              frame: relativeFrame - 300,
              fps: 30,
              config: { damping: 10 }
            })
          }}>
            🎉 All tests passed! DSL evolution successful!
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};

const ExtendedFinalResults: React.FC<{ startFrame: number }> = ({ startFrame }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 8, stiffness: 80 },
  });

  return (
    <AbsoluteFill
      style={{
        background: 'linear-gradient(135deg, #1e3a8a 0%, #7c3aed 100%)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        color: 'white',
        textAlign: 'center',
        opacity: Math.min(1, opacity),
        padding: '60px',
      }}
    >
      <h1 style={{ fontSize: '64px', marginBottom: '40px', textShadow: '2px 2px 4px rgba(0,0,0,0.5)' }}>
        🎉 Evolution Achievement Unlocked!
      </h1>
      
      <div style={{ display: 'flex', gap: '80px', marginBottom: '50px', flexWrap: 'wrap', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', fontWeight: 'bold', color: '#10B981' }}>9 → 14</div>
          <div style={{ fontSize: '20px' }}>Functions</div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', fontWeight: 'bold', color: '#F59E0B' }}>2</div>
          <div style={{ fontSize: '20px' }}>Hierarchy Levels</div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', fontWeight: 'bold', color: '#EF4444' }}>0.920</div>
          <div style={{ fontSize: '20px' }}>Best Fitness</div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', fontWeight: 'bold', color: '#8B5CF6' }}>100%</div>
          <div style={{ fontSize: '20px' }}>Tests Passed</div>
        </div>
      </div>
      
      <div style={{ 
        fontSize: '24px', 
        lineHeight: '1.8', 
        maxWidth: '1200px',
        backgroundColor: 'rgba(255, 255, 255, 0.15)',
        padding: '40px',
        borderRadius: '16px',
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{ marginBottom: '30px' }}>
          <strong>🚀 Self-Bootstrapping Achieved:</strong><br/>
          AI successfully learned to program by programming itself
        </div>
        <div style={{ marginBottom: '30px' }}>
          <strong>🌳 Hierarchical Composition:</strong><br/>
          Level 2 functions building on Level 1 discoveries
        </div>
        <div style={{ marginBottom: '30px' }}>
          <strong>🧠 GPT-4o Integration:</strong><br/>
          Real AI guidance for policy, value, and evolution
        </div>
        <div>
          <strong>💾 Persistent Evolution:</strong><br/>
          Functions survive across sessions and continue evolving
        </div>
      </div>
    </AbsoluteFill>
  );
};

const CallToAction: React.FC<{ startFrame: number }> = ({ startFrame }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 10, stiffness: 60 },
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#111827',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        color: 'white',
        textAlign: 'center',
        opacity: Math.min(1, opacity),
        padding: '60px',
      }}
    >
      <div style={{ fontSize: '56px', fontWeight: 'bold', marginBottom: '40px' }}>
        🧬 Try EvolDSL Today!
      </div>
      
      <div style={{ fontSize: '24px', marginBottom: '50px', maxWidth: '800px', lineHeight: '1.6' }}>
        Watch your own DSL evolve from simple primitives to complex hierarchical functions
      </div>
      
      <div style={{
        backgroundColor: '#10B981',
        color: 'white',
        padding: '20px 40px',
        borderRadius: '12px',
        fontSize: '24px',
        fontWeight: 'bold',
        marginBottom: '40px',
        fontFamily: 'JetBrains Mono, monospace'
      }}>
        github.com/allthingssecurity/evoldsl
      </div>
      
      <div style={{ fontSize: '18px', color: '#9CA3AF', lineHeight: '1.8' }}>
        <div>✅ GPT-4o Integration</div>
        <div>✅ Persistent Evolution</div>
        <div>✅ Real Function Testing</div>
        <div>✅ Complete Source Code</div>
      </div>
      
      <div style={{ fontSize: '16px', color: '#6B7280', marginTop: '40px' }}>
        Star ⭐ the repo to support autonomous programming research!
      </div>
    </AbsoluteFill>
  );
};