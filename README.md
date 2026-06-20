# Repository Auditor Agent 🚀

An intelligent, **read-only** agentic workflow that analyzes codebases and generates comprehensive onboarding guidance for new developers.

## 🎯 Purpose

Automate the creation of high-quality `guidance.md` documents by:
- Reading repository structure and core files
- Analyzing git history and recent changes
- Understanding project architecture and patterns
- Using LLM intelligence to synthesize developer-friendly onboarding guides

**Zero file writes** - fully read-only operation. Analysis output goes to stdout.

## ✨ Features

✅ **Intelligent Agent Workflow** - Multi-step analysis with LangGraph
✅ **Language Agnostic** - Works with Python, JavaScript, Java, Go, Rust, etc.
✅ **Git Integration** - Analyzes commit history and project evolution
✅ **Core File Analysis** - Automatically identifies and reads README, requirements, main files
✅ **Architecture Detection** - Identifies project structure, frameworks, build systems
✅ **Zero Cost** - Uses free Groq API tier
✅ **No Writes** - Fully read-only, respects repository integrity
✅ **Local First** - Runs entirely on your machine

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         LangGraph Agent Workflow                │
├─────────────────────────────────────────────────┤
│ 1. Explore          → Detect repo type & structure
│ 2. Read Core Files  → Analyze README, config, main files
│ 3. Git Analysis     → Fetch history & recent changes
│ 4. Architecture     → Identify modules & patterns
│ 5. Generate         → LLM synthesizes guidance.md
│ 6. Finalize         → Prepare output
└─────────────────────────────────────────────────┘
         ↓ (using)
┌─────────────────────────────────────────────────┐
│    Custom Tool Kits (Read-Only Access)          │
├─────────────────────────────────────────────────┤
│ • FilesystemToolkit   - Safe file/dir reading
│ • GitToolkit         - Git commands & history
│ • RepoAnalyzerTools  - High-level analysis
└─────────────────────────────────────────────────┘
         ↓ (using)
┌─────────────────────────────────────────────────┐
│      Groq API (Mixtral 8x7B - Free Tier)       │
└─────────────────────────────────────────────────┘
```

## 📋 Tech Stack

- **Agent Framework**: LangGraph (state management + workflows)
- **LLM**: Groq API (Mixtral 8x7B) - free tier
- **Language**: Python 3.11+
- **Git Integration**: subprocess (native git commands)
- **File Access**: Direct filesystem (no MCP needed for MVP)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Clone/navigate to the project
cd repo-auditor-agent

# Install dependencies
pip install -r requirements.txt
# OR with uv (recommended)
uv sync
```

### 2. Set Up Groq API Key

Get your free API key from [Groq Console](https://console.groq.com/keys)

```bash
# Create .env file
echo "GROQ_API_KEY=gsk_your_api_key_here" > .env
```

### 3. Run the Agent

```bash
# Analyze current directory
python main.py .

# Analyze specific repository
python main.py /path/to/your/repo

# Verbose mode
python main.py /path/to/repo --verbose
```

### Example Output

```
🚀 Starting Repository Audit Agent for: /home/user/myproject
============================================================

📂 [Step 1] Exploring repository structure...
  ✅ Detected language: Python
  ✅ Found 8 core files
  ✅ Frameworks: FastAPI, Docker

📖 [Step 2] Reading core files...
  📄 Reading README.md...
    ✅ Read 45 lines
  📄 Reading pyproject.toml...
    ✅ Read 32 lines
  [...]

📜 [Step 3] Analyzing git history...
  ✅ Found 127 recent commits
  ✅ Found 89 changes in last 90 days
  ✅ Repository status: clean

🏗️  [Step 4] Identifying architecture...
  ✅ Found 2 entry points
  ✅ Identified 7 main modules

✨ [Step 5] Generating onboarding guidance...
  ✅ Guidance generated successfully

============================================================
✅ Analysis Complete!
Repository: /home/user/myproject
Language: Python
Files Analyzed: 5

============================================================
📋 GENERATED ONBOARDING GUIDANCE:
============================================================

# Project Onboarding Guide

## Quick Start
...
```

## 📚 Project Structure

```
repo-auditor-agent/
├── main.py                 # Entry point
├── agent.py               # LangGraph agent orchestrator
├── tools.py               # FilesystemToolkit, GitToolkit, RepoAnalyzerTools
├── utils.py               # Helper functions
├── examples.py            # Code examples and use cases
├── pyproject.toml         # Dependencies
├── requirements.txt       # Pip requirements
├── .env.example           # Example environment variables
├── README.md              # This file
├── QUICKSTART.md          # 5-minute quick start
├── CONFIG.md              # Configuration guide
├── DEVELOPMENT.md         # Advanced development guide
└── .gitignore             # Git ignore rules
```

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** ⭐ - **Get started in 5 minutes**
- **[CONFIG.md](CONFIG.md)** - Customize agent behavior and prompts
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Advanced development and extension
- **[examples.py](examples.py)** - 10+ code examples

## 🔧 Configuration

### Environment Variables

```env
GROQ_API_KEY=gsk_your_key_here  # Required: Groq API key
```

### Agent Behavior

Edit in `agent.py`:
- `max_commits`: Number of git commits to analyze (default: 20)
- `max_lines_per_file`: Maximum lines to read from files (default: 5000)
- `core_files_count`: How many core files to analyze (default: 5)

## 🎯 Agent Nodes Explained

### 1. **explore_repo** 
- Maps directory structure
- Detects language/frameworks
- Identifies core files to read
- **Output**: repo_type, directory_structure, core_files

### 2. **read_core_files**
- Reads README, requirements, main files
- Stores content summaries
- **Output**: file_contents dict

### 3. **analyze_git_history**
- Fetches recent commits
- Gets git status
- Analyzes 90-day change history
- **Output**: git_history, git_status

### 4. **identify_architecture**
- Identifies entry points (main.py, app.js, etc.)
- Maps main modules/directories
- **Output**: key_insights

### 5. **generate_guidance**
- Prepares comprehensive context
- Calls Groq LLM with structured prompt
- **Output**: guidance_content (full markdown)

### 6. **finalize**
- Marks analysis complete
- **Output**: Updated state

## 🛡️ Safety & Read-Only Design

✅ **No file writes** to analyzed repository  
✅ **Read-only file access** via FilesystemToolkit  
✅ **Git commands are read-only** (git log, git status)  
✅ **Output goes to stdout** - user controls where it's saved  
✅ **No external dependencies modified**

## 🔄 Workflow Customization

Modify the agent workflow in `agent.py`:

```python
# Add a new analysis node
def custom_analysis_node(self, state: AgentState) -> AgentState:
    print("\n🔍 [Step N] Custom analysis...")
    # Your analysis here
    state["key_insights"]["custom_data"] = data
    return state

# Add it to the graph in _build_graph()
graph.add_node("custom_analysis", self.custom_analysis_node)
graph.add_edge("identify_architecture", "custom_analysis")
graph.add_edge("custom_analysis", "generate_guidance")
```

## 📊 Next Steps & Enhancements

- [ ] **Local LLM Support** - Ollama integration for fully offline operation
- [ ] **Advanced Analysis** - Test suite analysis, dependency mapping
- [ ] **Language Plugins** - Language-specific insights
- [ ] **Web UI** - Simple interface for non-technical users
- [ ] **Multi-repo Support** - Analyze multiple repos, compare patterns
- [ ] **Custom Prompts** - User-provided templates and instructions
- [ ] **Structured Output** - JSON export for tool integration

## 🤝 Contributing

Ideas for enhancement:

1. **Better Architecture Detection** - Parse AST for more accurate analysis
2. **Code Metrics** - Cyclomatic complexity, test coverage, etc.
3. **Security Scanning** - Identify potential security patterns
4. **Performance Analysis** - Detect performance-critical files
5. **Pattern Recognition** - Identify design patterns used in codebase

## 📝 License

Open source - use freely!

## 💡 Tips

- **First run slower**: Agent explores and analyzes - subsequent runs can leverage cache
- **Large repos**: First 5 core files analyzed; add more if needed
- **Git history**: Analyzes last 20 commits and 90-day window
- **Free tier**: Groq free tier has rate limits; cache results if analyzing many repos

## 🐛 Troubleshooting

**Q: "GROQ_API_KEY not set"**
```bash
# Create .env file with your API key
echo "GROQ_API_KEY=gsk_..." > .env
```

**Q: "Not a git repository"**
- Agent gracefully handles non-git repos
- Git analysis skipped, other analysis proceeds

**Q: "Permission denied"**
- Ensure you have read access to the repository path
- Run with user that has access

**Q: Output is too short/incomplete**
- Increase token limit in Groq API call (agent.py, line ~200)
- Set `max_tokens=4000` or higher

## 📞 Support

For issues or questions about the agent workflow:
1. Check the troubleshooting section
2. Review agent.py for configuration options
3. Ensure Groq API key is valid and has quota
#   O n b o a r d i n g - H e l p e r  
 