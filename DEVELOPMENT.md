# Development Guide

## Project Architecture Details

### Agent State Flow

```
AgentState TypedDict
├── target_repo_path: str            # Repository path being analyzed
├── current_step: str                # Current workflow step
├── repo_type: dict                  # Language, frameworks detected
├── core_files: dict                 # Files to analyze
├── file_contents: dict              # Read file content summaries
├── git_history: dict                # Git commits & history
├── git_status: dict                 # Repository status
├── directory_structure: dict        # Directory tree
├── key_insights: dict               # Architecture & patterns
├── messages: Sequence[BaseMessage]  # Chat messages (for future use)
├── guidance_content: str            # Generated onboarding guide
└── analysis_complete: bool          # Workflow completion flag
```

### Tool Kits

#### FilesystemToolkit
- `list_directory(path)` - List files/folders recursively
- `read_file(file_path)` - Read file content (up to 5000 lines)
- `find_files(pattern)` - Find files matching pattern

#### GitToolkit
- `get_git_log(max_commits)` - Fetch recent commits
- `get_git_branches()` - List all branches
- `get_git_status()` - Get repo status
- `get_recent_changes(days)` - Changes in time period

#### RepoAnalyzerTools
- `detect_repo_type()` - Detect language & frameworks
- `get_core_files_to_read()` - Identify priority files

## Extending the Agent

### Adding a New Analysis Node

```python
def custom_node(self, state: AgentState) -> AgentState:
    """Custom analysis step."""
    print("\n🔍 [Step X] Custom Analysis...")
    
    # Your analysis logic here
    result = self.tools_manager.your_method()
    
    # Update state
    state["custom_field"] = result
    state["current_step"] = "custom_node"
    
    return state
```

Add to graph in `_build_graph()`:
```python
graph.add_node("custom_step", self.custom_node)
graph.add_edge("previous_step", "custom_step")
graph.add_edge("custom_step", "next_step")
```

### Adding Custom Tools

Create methods in `RepoAnalyzerTools`:

```python
def analyze_dependencies(self) -> dict:
    """Analyze project dependencies."""
    # Implementation here
    return {"dependencies": [...]}
```

Use in agent:
```python
dependencies = self.tools_manager.analyze_dependencies()
state["dependencies"] = dependencies
```

### Conditional Workflow

For conditional branching:

```python
# In _build_graph()
graph.add_conditional_edges(
    "identify_architecture",
    self.should_analyze_tests,  # Decides next node
    {
        "analyze_tests": "analyze_tests_node",
        "skip_tests": "generate_guidance"
    }
)

def should_analyze_tests(self, state: AgentState) -> str:
    """Decide if tests should be analyzed."""
    if state["repo_type"]["has_tests"]:
        return "analyze_tests"
    return "skip_tests"
```

## Advanced Configuration

### Custom LLM Models

Edit in `generate_guidance_node()`:

```python
# Use different Groq model
response = self.groq_client.chat.completions.create(
    model="llama-2-70b-4096",  # or other Groq model
    messages=messages,
    temperature=0.5,  # More deterministic
    max_tokens=4000
)
```

### Groq Model Options (Free Tier)
- `mixtral-8x7b-32768` - Fast, balanced
- `llama-2-70b-4096` - More capable
- `gemma-7b-it` - Lightweight

### Custom Prompts

Edit system instruction in `generate_guidance_node()`:

```python
messages = [
    {
        "role": "system",
        "content": """Your custom system prompt here.
                    Make it specific to your needs.
                    """
    },
    ...
]
```

## Performance Optimization

### Caching Analysis Results

```python
import json

def cache_analysis(repo_path: str, state: AgentState):
    """Cache analysis results."""
    cache_file = f".cache_{Path(repo_path).name}.json"
    with open(cache_file, 'w') as f:
        json.dump({
            "repo_type": state["repo_type"],
            "insights": state["key_insights"]
        }, f)

def load_cached_analysis(repo_path: str):
    """Load cached results if available."""
    cache_file = f".cache_{Path(repo_path).name}.json"
    if Path(cache_file).exists():
        with open(cache_file) as f:
            return json.load(f)
    return None
```

### Parallel File Analysis

For large repositories, parallelize file reading:

```python
from concurrent.futures import ThreadPoolExecutor

def read_files_parallel(self, files: List[str]) -> dict:
    """Read multiple files in parallel."""
    contents = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(self.fs_toolkit.read_file, files)
        for file_path, content in zip(files, results):
            contents[file_path] = content
    return contents
```

## Testing

### Unit Tests for Tools

```python
# test_tools.py
import pytest
from tools import FilesystemToolkit

def test_list_directory():
    toolkit = FilesystemToolkit(".")
    result = toolkit.list_directory(".")
    assert "files" in result
    assert "directories" in result

def test_read_file():
    toolkit = FilesystemToolkit(".")
    result = toolkit.read_file("README.md")
    assert "content" in result
    assert result["lines"] > 0
```

### Testing Agent

```python
# test_agent.py
def test_agent_workflow():
    agent = RepositoryAuditorAgent(".", "test_key")
    result = agent.run()
    assert result["analysis_complete"]
    assert len(result["guidance_content"]) > 0
```

## Integration with External Systems

### Export to JSON

```python
def export_analysis(state: AgentState, output_file: str):
    """Export analysis results as JSON."""
    output = {
        "repository": state["target_repo_path"],
        "repo_type": state["repo_type"],
        "insights": state["key_insights"],
        "guidance": state["guidance_content"]
    }
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
```

### Webhook Integration

```python
import requests

def send_to_webhook(state: AgentState, webhook_url: str):
    """Send analysis to external webhook."""
    data = {
        "repository": state["target_repo_path"],
        "analysis": state["guidance_content"]
    }
    requests.post(webhook_url, json=data)
```

## Debugging

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In agent nodes
logger.debug(f"Processing files: {state['core_files']}")
```

### Inspect Agent State

```python
def debug_state(state: AgentState):
    """Print formatted state."""
    print(f"\nState at {state['current_step']}:")
    print(f"  Repo Type: {state['repo_type']}")
    print(f"  Files Read: {len(state['file_contents'])}")
    print(f"  Insights: {state['key_insights']}")
```

## Production Deployment

### Docker Setup

```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV GROQ_API_KEY=gsk_your_key

CMD ["python", "main.py", "/repo"]
```

### Error Handling

Wrap agent execution:

```python
def safe_analyze(repo_path: str) -> Optional[str]:
    """Safely analyze repository with error handling."""
    try:
        agent = RepositoryAuditorAgent(repo_path, os.environ.get("GROQ_API_KEY"))
        result = agent.run()
        return result["guidance_content"]
    except FileNotFoundError:
        logger.error(f"Repository not found: {repo_path}")
        return None
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return None
```

## Future Enhancements

1. **Multi-Language Support**
   - Language-specific analyzers
   - Framework-specific insights

2. **Advanced Metrics**
   - Code complexity analysis
   - Test coverage reports
   - Dependency graphs

3. **AI Improvements**
   - Fine-tuned models for code
   - Context-aware file selection
   - Semantic understanding of architecture

4. **User Interface**
   - Web dashboard
   - Interactive analysis explorer
   - Real-time progress tracking

5. **Integration**
   - GitHub/GitLab API integration
   - CI/CD pipeline integration
   - Knowledge base generation
