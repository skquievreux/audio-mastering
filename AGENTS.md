# 🎛️ Audio Mastering - Agent Guidelines

## Build/Test Commands
```bash
# Run main tool with default settings
python mastering_tool.py

# Test single file processing
python -c "from audio_processor import AudioProcessor; p = AudioProcessor(); p.process_file('input.wav', 'output.wav')"

# Run performance benchmark
python benchmark_performance.py

# Development server
python mastering_tool.py --web --port 8080

# Batch processing with custom preset
python mastering_tool.py --preset gentle --workers 4
```

## Code Style
- **Language**: Python 3.12+ (optimiert für NumPy 2.0+)
- **Imports**: Standard library first, then third-party, then local modules
- **Type hints**: Use for function signatures and complex data structures
- **Naming**: snake_case for variables/functions, UPPER_CASE for constants
- **Logging**: Use `logging.getLogger(__name__)` in each module
- **Error handling**: Always log exceptions with context, raise informative errors
- **Audio processing**: Handle mono/stereo with helper functions, avoid code duplication
- **Presets**: Default to 'suno' preset (no compression, just LUFS + limiter)

## Key Patterns
- Use pathlib.Path for file operations
- Process audio in numpy arrays, handle stereo with column_stack
- Log each processing step with before/after measurements
- Validate inputs early, create output directories as needed
- Use German comments for user-facing messages, English for technical docs