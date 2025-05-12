# Python_blog
A structured catalog of Python library explorations, organized chronologically. Each month features hands-on experiments with different libraries, showcasing practical use cases and benchmarks.

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