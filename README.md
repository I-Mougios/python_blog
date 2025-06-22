# Python_blog
A structured catalog of Python library explorations and custom utilities, organized chronologically.

# May 2025

### 1. Decorators using `wrapt.decorator`

#### Key Takeaways
- **Closure Optimization**: `wrapt.decorator` reduces nesting vs traditional decorators
- **Runtime Control**: Enable/disable decorators via predicate functions
- **Method Support**: Handles instance/class/static methods seamlessly

### 2. Debugging with `icecream`

#### Key Takeaways
- **Debugging Efficiency**: Replace `print()` with `ic()` for automatic variable labeling
- **Execution Tracing**: Track code flow with automatic file/line number reporting
- **Production Ready**: Global toggle (`ic.disable()`) for clean production code
- **Custom Formatting**: Extend output with `argumentToString` registrations

### 3. Utility class for reading large CSV files

#### Key Features
- **Batch loading**: Reads rows in user-defined batches to avoid memory overload.
- **Dictionary output**: Each row is returned as a dictionary, just like csv.DictReader.
- **Iterator protocol**: Compatible with for loops like "for batch in reader".
- **Header flexibility**: Can infer headers or accept them explicitly.
- **Unicode robustness**: Automatically cleans and reopens files with decoding issues.
- **Smart delimiter handling**: Replaces conflicting delimiters when necessary.
- **Context manager support**: Ensures safe file handling via with blocks.