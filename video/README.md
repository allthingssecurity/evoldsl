# EvolDSL Video

This Remotion project creates a video demonstration of the EvolDSL system.

## Setup

```bash
npm install
```

## Development

```bash
npm start
```

This will open the Remotion Studio where you can preview and edit the video.

## Render

```bash
npm run render
```

This will render the video to `out/evoldsl-demo.mp4`.

## Video Structure

The video demonstrates:

1. **Title Sequence** (0-5s): Introduction to EvolDSL
2. **MCTS Tree** (4-10s): Shows how MCTS explores program space with GPT-4o guidance
3. **Code Evolution** (10-16s): Demonstrates function morphing from primitives to evolved functions
4. **Population Dynamics** (15-22s): Shows evolution population with fitness-based selection
5. **Bootstrap Cycles** (21-28s): Illustrates the complete bootstrap process
6. **Final Results** (27-30s): Shows the achieved hierarchical DSL functions

## Components

- `AdvancedMCTSTree`: Visualizes MCTS search with UCB scores and GPT-4o integration
- `CodeMorphing`: Animates code transformation from primitives to evolved functions
- `EvolutionPopulation`: Shows population-based evolution with fitness visualization
- `BootstrapCycle`: Demonstrates the 4-phase bootstrap process
- `FinalResults`: Displays the successful evolution outcomes