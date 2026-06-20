# Configuration Guide

Customize the Repository Auditor Agent for your specific needs.

## Core Configuration

### API Key Setup

```bash
# Via .env file
echo "GROQ_API_KEY=gsk_your_key" > .env

# Via environment variable
export GROQ_API_KEY=gsk_your_key

# Via Python
import os
os.environ["GROQ_API_KEY"] = "gsk_your_key"
```

## Agent Behavior Configuration

### In `agent.py`:

#### 1. Change LLM Model

```python
# In generate_guidance_node() method
response = self.groq_client.chat.completions.create(
    model="llama-2-70b-4096",  # Change this
    messages=messages,
    temperature=0.7,
    max_tokens=4000
)
```

**Available Models (Free Tier):**
- `mixtral-8x7b-32768` (default) - Balanced, fast
- `llama-2-70b-4096` - More capable
- `gemma-7b-it` - Lightweight

#### 2. Adjust File Reading Limits

```python
# In read_core_files_node()
core_files_to_read = state["core_files"]["core_files"][:5]  # Change 5

# In tools.py FilesystemToolkit.read_file()
with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()[:5000]  # Change 5000
```

#### 3. Customize Git History Depth

```python
# In analyze_git_history_node()
git_log = self.git_toolkit.get_git_log(max_commits=20)  # Change 20
recent_changes = self.git_toolkit.get_recent_changes(days=90)  # Change 90
```

#### 4. Control LLM Temperature and Tokens

```python
response = self.groq_client.chat.completions.create(
    model="mixtral-8x7b-32768",
    messages=messages,
    temperature=0.7,      # 0-1: 0=deterministic, 1=creative
    max_tokens=4000       # Increase for longer outputs
)
```

## Prompt Customization

### Custom System Instruction

Edit in `generate_guidance_node()`:

```python
messages = [
    {
        "role": "system",
        "content": """You are a developer documentation expert.
                    Create onboarding guides that are:
                    - Clear and concise
                    - Beginner-friendly
                    - Rich with examples
                    - Ready to use immediately
                    
                    Focus on: setup, architecture, key files, workflows."""
    },
    ...
]
```

### Custom User Prompt

```python
messages.append({
    "role": "user",
    "content": f"""Analyze this repo and create:
1. 5-minute quick start
2. Architecture overview
3. Key module descriptions
4. Development workflow guide

Repository context:
{context}

Make it useful for new team members joining tomorrow."""
})
```

## Workflow Customization

### Add New Analysis Step

In `agent.py`:

```python
def custom_analysis_node(self, state: AgentState) -> AgentState:
    """Custom step in workflow."""
    print("\n🔍 [Step X] Custom Analysis...")
    
    # Your analysis
    result = self.tools_manager.analyze_something()
    
    # Update state
    state["custom_field"] = result
    state["current_step"] = "custom_analysis"
    
    return state
```

Add to graph:

```python
def _build_graph(self):
    graph = super()._build_graph()
    
    # Insert between two nodes
    graph.add_node("custom_analysis", self.custom_analysis_node)
    graph.add_edge("identify_architecture", "custom_analysis")
    graph.add_edge("custom_analysis", "generate_guidance")
    
    return graph
```

### Add Conditional Branching

```python
def _build_graph(self):
    graph = StateGraph(AgentState)
    
    # ... add nodes ...
    
    # Add conditional logic
    graph.add_conditional_edges(
        "identify_architecture",
        self.should_run_deep_analysis,
        {
            "deep_analysis": "deep_analysis_node",
            "skip_deep": "generate_guidance"
        }
    )

def should_run_deep_analysis(self, state: AgentState) -> str:
    """Decide if deep analysis should run."""
    if state["repo_type"]["language"] in ["Python", "JavaScript"]:
        return "deep_analysis"
    return "skip_deep"
```

## Tool Customization

### Add Custom Tool

In `tools.py`:

```python
class CustomAnalyzerTools:
    """Your custom analysis tools."""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
    
    def analyze_code_quality(self) -> dict:
        """Analyze code quality metrics."""
        # Implementation
        return {
            "complexity": "medium",
            "coverage": 75,
            "issues": []
        }
```

Use in agent:

```python
class RepositoryAuditorAgent:
    def __init__(self, repo_path: str, groq_api_key: str):
        # ... existing setup ...
        self.custom_tools = CustomAnalyzerTools(repo_path)
    
    def custom_node(self, state: AgentState) -> AgentState:
        metrics = self.custom_tools.analyze_code_quality()
        state["code_quality"] = metrics
        return state
```

## Input/Output Configuration

### Change Default Repo Path

In `main.py`:

```python
parser.add_argument(
    "repo_path",
    nargs="?",
    default=".",  # Change this default
    help="Path to analyze"
)
```

### Save Output Automatically

In `main.py`:

```python
if args.output:
    # Safe write to external location
    output_path = Path(args.output).resolve()
    if not output_path.is_relative_to(repo_path):  # Safety check
        with open(output_path, 'w') as f:
            f.write(result["guidance_content"])
```

### Add Output Formats

Create in `utils.py`:

```python
def export_json(state: dict, path: str):
    """Export analysis as JSON."""
    import json
    with open(path, 'w') as f:
        json.dump(state, f, indent=2, default=str)

def export_html(guidance: str, path: str):
    """Export guidance as HTML."""
    html = f"<html><body><pre>{guidance}</pre></body></html>"
    with open(path, 'w') as f:
        f.write(html)
```

## Performance Tuning

### Parallel File Reading

```python
from concurrent.futures import ThreadPoolExecutor

def read_files_parallel(self, files: List[str]) -> dict:
    """Read multiple files concurrently."""
    contents = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(self.fs_toolkit.read_file, f): f 
            for f in files
        }
        for future in futures:
            file_path = futures[future]
            contents[file_path] = future.result()
    return contents
```

### Caching Results

```python
from functools import lru_cache

class RepositoryAuditorAgent:
    @lru_cache(maxsize=10)
    def analyze_cached(self, repo_path: str) -> dict:
        """Cache analysis results."""
        # Same as run()
        pass
```

### Rate Limiting

```python
import time
from functools import wraps

def rate_limit(calls_per_second=1):
    """Rate limit function calls."""
    min_interval = 1.0 / calls_per_second
    
    def decorator(func):
        last_called = 0.0
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_called
            elapsed = time.time() - last_called
            wait_time = min_interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            result = func(*args, **kwargs)
            last_called = time.time()
            return result
        
        return wrapper
    return decorator
```

## Logging Configuration

### Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### Log Specific Events

In agent nodes:

```python
def explore_repo_node(self, state: AgentState) -> AgentState:
    logger.info(f"Exploring repository: {state['target_repo_path']}")
    
    repo_type = self.tools_manager.detect_repo_type()
    logger.debug(f"Detected language: {repo_type['language']}")
    
    return state
```

## Environment-Specific Configuration

### Development

```python
# Set in agent.py
DEBUG = True
MAX_TOKENS = 2000
TEMPERATURE = 0.9
LOG_LEVEL = "DEBUG"
```

### Production

```python
DEBUG = False
MAX_TOKENS = 4000
TEMPERATURE = 0.5
LOG_LEVEL = "INFO"
```

### Testing

```python
DEBUG = True
MAX_TOKENS = 1000
TEMPERATURE = 0.3  # Deterministic
USE_MOCK_GROQ = True
```

## Docker Configuration

### Environment Variables

```dockerfile
ENV GROQ_API_KEY=gsk_your_key
ENV AGENT_MAX_FILES=5
ENV AGENT_MAX_COMMITS=20
ENV AGENT_TEMPERATURE=0.7
```

### Runtime Configuration

```dockerfile
ENTRYPOINT ["python", "main.py"]
CMD ["/repo"]
```

## Testing Configuration

### Mock Groq API

```python
class MockGroqClient:
    """Mock Groq for testing."""
    
    def chat.completions.create(self, **kwargs):
        """Return mock response."""
        class MockResponse:
            class Choice:
                message.content = "Mock onboarding guide..."
            
            choices = [Choice()]
        
        return MockResponse()

# Use in tests
agent.groq_client = MockGroqClient()
```

## Preset Configurations

### For Small Projects

```python
max_files = 3
max_commits = 10
max_tokens = 2000
temperature = 0.6
```

### For Large Projects

```python
max_files = 10
max_commits = 50
max_tokens = 4000
temperature = 0.7
```

### For Fast Analysis

```python
max_files = 1
max_commits = 5
max_tokens = 1000
temperature = 0.3
skip_deep_analysis = True
```

### For Detailed Analysis

```python
max_files = 20
max_commits = 100
max_tokens = 4000
temperature = 0.8
include_security_scan = True
include_complexity_analysis = True
```

## See Also

- [DEVELOPMENT.md](DEVELOPMENT.md) - Advanced development
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [README.md](README.md) - Full documentation
