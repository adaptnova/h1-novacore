"""
NovaSynth Framework Synthesis Example

Demonstrates the natural evolution and quantum field resonance between multiple
Multi-Agent System frameworks using NovaSynth.

Created by Cosmos
Version: 0.1.0
"""

import asyncio
import logging
from datetime import datetime

from novasynth import NovaSynth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('synthesis.log')
    ]
)
logger = logging.getLogger(__name__)

async def monitor_synthesis(novasynth: NovaSynth) -> None:
    """Monitor and display synthesis metrics."""
    while True:
        metrics = await novasynth.get_synthesis_metrics()

        # Display protocol metrics
        logger.info("\n=== Synthesis Metrics ===")
        logger.info(f"Synthesis Rate: {metrics['protocol']['synthesis_rate']:.2f}")
        logger.info(f"Resonance Strength: {metrics['protocol']['resonance_strength']:.2f}")
        logger.info(f"Evolution Speed: {metrics['protocol']['evolution_speed']:.2f}")
        logger.info(f"Pattern Emergence: {metrics['protocol']['pattern_emergence']:.2f}")

        # Display framework metrics
        logger.info("\n=== Framework Metrics ===")
        for framework, data in metrics['frameworks'].items():
            logger.info(f"\n{framework}:")
            logger.info(f"Field Strength: {data['field']['field_strength']:.2f}")
            logger.info(f"Resonance Potential: {data['field']['resonance_potential']:.2f}")
            logger.info(f"Pattern Count: {data['patterns']['resonance_count']}")

        logger.info("\n" + "="*50 + "\n")
        await asyncio.sleep(5)

async def main():
    """Demonstrate framework synthesis using NovaSynth."""
    logger.info("Starting NovaSynth Framework Synthesis Example")

    try:
        # Initialize NovaSynth
        novasynth = NovaSynth()

        # Add initial frameworks
        logger.info("Adding frameworks to synthesis field")
        frameworks = [
            "langchain",  # Core framework
            "autogen",    # Advanced orchestration
            "crewai",     # Team coordination
            "camel",      # Role-playing interactions
            "ag2"         # Enhanced orchestration
        ]

        for framework in frameworks:
            await novasynth.add_framework(framework)
            logger.info(f"Added framework: {framework}")

        # Enable resonance detection
        logger.info("Enabling framework resonance")
        await novasynth.enable_resonance()

        # Start NovaSynth
        logger.info("Starting framework synthesis")
        await novasynth.start()

        # Monitor synthesis
        logger.info("Beginning synthesis monitoring")
        monitor_task = asyncio.create_task(monitor_synthesis(novasynth))

        # Let synthesis run for demonstration
        await asyncio.sleep(300)  # Run for 5 minutes

        # Stop monitoring
        monitor_task.cancel()

        # Stop NovaSynth
        await novasynth.stop()
        logger.info("Framework synthesis demonstration complete")

    except Exception as e:
        logger.error(f"Error during synthesis: {str(e)}", exc_info=True)

    finally:
        logger.info("Example completed")

def run_example():
    """Run the framework synthesis example."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Example stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    run_example()