# Individual Report: Lab 3 - Learning Material Tool & Agent Integration

- **Student Name**: Nguyễn Trọng Minh
- **Student ID**: 2A202600226
- **Date**: April 6, 2026

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

### Modules Implemented:
1. **`src/tools/learning_material_tool.py`** - Main unified tool for learning material search
2. **`src/agent/agent_with_tool.py`** - Agent integration examples  
3. **`src/tools/__init__.py`** - Updated imports for new tool

### Code Highlights:

#### 1. Learning Material Tool (`src/tools/learning_material_tool.py`)
- **LearningMaterialTool class** [Lines 13-180]: Core tool for searching learning materials
  - `__init__()`: Initialize tool with data loading
  - `search()`: Main search method returning JSON dict
  - `save_to_json_file()`: Persist results to JSON files
  - `execute()`: Agent interface method
  - `list_all_topics()`: List all available topics

**Key Method - search()**:
```python
def search(self, keyword: str, include_examples: bool = True, 
          include_mistakes: bool = True) -> Dict[str, Any]:
    """Search tài liệu theo keyword và trả về JSON Dict"""
    # Case-insensitive keyword matching
    # Structured response with topic, definition, examples, mistakes, resources
    # Returns: {"success": bool, "topic": str, "definition": str, "examples": list, ...}
```

#### 2. Agent Integration Examples (`src/agent/agent_with_tool.py`)
- **SimpleAgent class** [Lines 19-71]: Basic agent for student questions
  - `process_user_input()`: Extract keyword and call tool
  - `_extract_keyword()`: Support English & Vietnamese keywords
  - `display_result()`: Format tool output

- **AdvancedAgent class** [Lines 74-127]: Advanced features
  - `search_with_file_output()`: Search and save to file
  - `compare_topics()`: Compare 2 topics
  - `batch_search()`: Search multiple topics

#### 3. Helper Functions & Interfaces
- **search_learning_material()** [Lines 197-217]: Main function for agent to call
  - Simple interface: `search_learning_material(keyword, **options)`
  - Returns pure JSON output for agent consumption
  - Singleton pattern for efficient resource usage

### Documentation Generated:
- `AGENT_QUICK_START.md` - Quick reference for agent developers
- `IMPLEMENTATION_SUMMARY.md` - Full implementation details
- **How code interacts with tool**: Agent extracts keyword → calls search_learning_material() → receives JSON → formats for user

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

### Problem 1: Python Module Import Error

**Problem Description**: 
When running `agent_with_tool.py`, encountered `ModuleNotFoundError: No module named 'src'` because tool was trying to import from relative path without proper sys.path setup.

**Error Log**:
```
File "C:\Project\Vin AI\Day3\lab03.C401-C3\src\agent\learning_assistant.py", line 13
  from src.tools.search_learning_material import (...)
ModuleNotFoundError: No module named 'src'
```

**Diagnosis**: 
The issue occurred because Python's import system couldn't find the `src` package when running from the agent directory. The sys.path didn't include the project root directory needed for absolute imports.

**Solution**: 
Added sys.path manipulation at the beginning of `agent_with_tool.py`:
```python
import sys
from pathlib import Path

current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))
```

**Result**: ✅ All imports resolved successfully. Both `learning_material_tool.py` and `agent_with_tool.py` now execute without import errors.

---

### Problem 2: Consolidating Two Files into One

**Problem Description**: 
Initial implementation split functionality across `search_learning_material.py` (search logic) and `learning_assistant.py` (formatting). This created confusion about which file agent should use.

**Diagnosis**: 
The two-file design was not agent-friendly because:
1. Required importing from 2 modules
2. Mixed concerns (search logic vs. text formatting)
3. No clear single interface for agent to call
4. Text output instead of structured JSON

**Solution**: 
Consolidated into `learning_material_tool.py` with:
1. Unified interface: `search_learning_material(keyword)`
2. Pure JSON output (agent-ready)
3. Single import point
4. Clear method signatures with type hints
5. Singleton pattern for efficient resource management

**Result**: ✅ Clean, agent-friendly interface. Agent calls one function, gets JSON output.

---

### Problem 3: Data Folder Path Resolution

**Problem Description**: 
When tool initialized from different directories, couldn't reliably find `data/tai_lieu_hoc_tap.json` due to relative path issues.

**Diagnosis**: 
Using hardcoded relative paths like `"data/tai_lieu_hoc_tap.json"` failed when script run from different working directories.

**Solution**: 
Implemented intelligent path resolution:
```python
if data_dir is None:
    current_dir = Path(__file__).parent.parent.parent
    data_dir = current_dir / "data"
```

**Result**: ✅ Tool works regardless of execution directory. Paths resolved correctly from script location.

---

### Verification

All debugging issues resolved through 5 test cases:
```
✅ Test 1: Basic search ("pointer")
✅ Test 2: Search without examples ("recursion", include_examples=False)
✅ Test 3: Search with file save ("array", save_to_file=True)
✅ Test 4: List all topics
✅ Test 5: Invalid keyword error handling
```

---

## III. Personal Insights: Tool Design for Agents (10 Points)

*Reflect on design decisions and observations.*

### 1. Single Interface vs. Multiple Modules

**Observation**: Initial two-module design (`search_learning_material.py` + `learning_assistant.py`) vs. final unified design (`learning_material_tool.py`)

**Insight**: 
- **Two-module approach**: More modular but creates integration friction
- **Unified approach**: Simpler for agents, clear single entry point: `search_learning_material(keyword)`
- **Key lesson**: For agent tools, clarity and simplicity matter more than strict separation of concerns

### 2. Output Format Matters

**Observation**: Choice between structural JSON output vs. formatted text

**Design Decision**: 
Used pure JSON output because:
- Agents parse JSON more reliably than formatted text
- Enables downstream formatting flexibility
- Clear field semantics for tool composition
- Easier to validate and debug

### 3. Flexibility Through Options

**Observation**: Parameter design for `include_examples`, `include_mistakes`, `save_to_file`

**Insight**: 
- Agents may have different needs (quick definition vs. detailed analysis)
- File persistence useful for debugging and reporting
- Optional parameters keep simple cases simple while supporting advanced uses
- Default values (True for both includes) handle majority of agent needs

### 4. Error Handling Design

**Observation**: How to handle invalid keywords

**Design Decision**: Return structured error response with available options:
```json
{
  "success": false,
  "error": "Không tìm thấy topic",
  "available_topics": [list of valid topics]
}
```

**Why**: Helps agent recover gracefully and provide helpful feedback to user

### 5. Resource Management

**Observation**: Performance consideration in JSON loading

**Design Pattern Used**: Singleton pattern for LearningMaterialTool
```python
_tool_instance = None
def get_tool():
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = LearningMaterialTool()
    return _tool_instance
```

**Benefit**: JSON file loaded once, reused across multiple calls

---

> **Note**: Full evaluation of agent behavior (reasoning capability, reliability in edge cases, environmental feedback integration) requires real-world agent testing with actual LLM, which is outside current scope. This section reflects design observations from implementation phase.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

### 1. Scalability: Multi-Tool Management

**Current State**: Single learning material tool

**Improvement**: Extend to tool registry system:
```python
class ToolRegistry:
    def register_tool(self, name: str, tool_instance):
        """Register new tool for agent to discover"""
        self.tools[name] = tool_instance
    
    def get_tool(self, name: str, **kwargs):
        """Get tool by name with caching"""
        return self.tools[name].execute(**kwargs)
```

**Benefit**: Support dozens of domain-specific tools (math solver, code generator, etc.) with consistent interface

### 2. Performance: Async Tool Execution

**Current State**: Synchronous search calls

**Improvement**: Support concurrent tool execution:
```python
async def batch_search_async(topics: list):
    """Search multiple topics in parallel"""
    tasks = [search_learning_material_async(topic) for topic in topics]
    return await asyncio.gather(*tasks)
```

**Benefit**: For agent loops with multiple concurrent tool calls, significantly reduce latency

### 3. Reliability: Tool Validation & Versioning

**Current State**: Single version of learning materials

**Improvement**: Add schema validation and version control:
- JSON schema validation on load
- Content versioning (v1.0, v1.1, etc.)
- Rollback capability for invalid data
- A/B testing of tool implementations

### 4. Observability: Structured Logging

**Current State**: Print-based testing

**Improvement**: Production logging:
```python
import logging

logger = logging.getLogger(__name__)
logger.info(f"Tool called", extra={
    "tool": "search_learning_material",
    "keyword": keyword,
    "result": "success",
    "latency_ms": elapsed_time
})
```

**Benefit**: Monitor tool usage, performance, and failure patterns in production

### 5. Extensibility: Plugin Architecture

**Current State**: Tools hardcoded in learning_material_tool.py

**Improvement**: Plugin system:
```python
class ToolPlugin:
    """Base class for pluggable tools"""
    def execute(self, **kwargs) -> Dict:
        raise NotImplementedError

# Plugins can be loaded from external modules
# discovery_manager.load_plugins("./plugins/")
```

**Benefit**: Community can contribute new tools without modifying core code

### 6. Data Management: Caching & CDN

**Current State**: Load JSON from local disk

**Improvement**: Multi-tier caching:
- L1: In-memory cache (current implementation)
- L2: Redis cache for distributed systems
- L3: CDN for frequently accessed content
- Database backend for dynamic content updates

**Benefit**: Scale to millions of concurrent agents without data bottleneck

---

**Implementation Priority**:
1. **High Priority** (Month 1): Tool registry, structured logging, schema validation
2. **Medium Priority** (Month 2): Async execution, versioning system
3. **Low Priority** (Month 3+): Plugin architecture, advanced caching

---
---

## V. Summary of Completed Work

### Deliverables
- ✅ `src/tools/learning_material_tool.py` - Main tool implementation
- ✅ `src/agent/agent_with_tool.py` - Agent integration examples  
- ✅ `AGENT_QUICK_START.md` - Quick reference documentation
- ✅ `IMPLEMENTATION_SUMMARY.md` - Detailed specifications
- ✅ All unit tests passing (5/5 test cases)

### Code Quality
- ✅ Full type hints
- ✅ Comprehensive docstrings
- ✅ Error handling
- ✅ Singleton pattern for efficiency
- ✅ Production-ready code

### Testing Completed
- ✅ Basic keyword search (6 topics)
- ✅ Optional parameters (include_examples, include_mistakes)
- ✅ File persistence (save_to_file)
- ✅ Error cases (invalid keywords)
- ✅ Integration with SimpleAgent and AdvancedAgent

---

> [!NOTE]
> This report documents the implementation and design of the Learning Material Tool for AI agents. Sections on practical agent behavior with actual LLM models require field testing beyond this development phase. Code is ready for integration with chatbot.py and agent.py modules.
