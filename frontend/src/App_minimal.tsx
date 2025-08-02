function App() {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{
        textAlign: 'center',
        background: 'rgba(255,255,255,0.1)',
        padding: '2rem',
        borderRadius: '10px',
        backdropFilter: 'blur(10px)'
      }}>
        <h1>🧬 EvolDSL React Test</h1>
        <p>If you see this, React is working!</p>
        <button 
          style={{
            background: '#4CAF50',
            color: 'white',
            padding: '15px 32px',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '16px'
          }}
          onClick={() => alert('React button works!')}
        >
          Test React Button
        </button>
      </div>
    </div>
  )
}

export default App