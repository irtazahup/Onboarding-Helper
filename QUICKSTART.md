# 🚀 Quick Start Guide

Get your Repository Auditor Agent running in 5 minutes!

## Step 1: Get Your API Key (2 min)

1. Go to [Groq Console](https://console.groq.com/keys)
2. Sign up for free (email only)
3. Copy your API key

## Step 2: Set Up Environment (1 min)

```bash
# Navigate to project directory
cd repo-auditor-agent

# Create .env file with your API key
echo "GROQ_API_KEY=gsk_your_actual_key_here" > .env
```

**OR** on Windows PowerShell:
```powershell
@"
GROQ_API_KEY=gsk_your_actual_key_here
"@ | Out-File .env
```

## Step 3: Install Dependencies (1 min)

```bash
# Option A: Using pip
pip install -r requirements.txt

# Option B: Using uv (faster)
uv sync
```

## Step 4: Run It! (1 min)

```bash
# Analyze current directory
python main.py .

# Analyze any repo
python main.py /path/to/repo

# Verbose output
python main.py /path/to/repo --verbose
```

## That's It! 🎉

You'll see:
```
🚀 Starting Repository Audit Agent for: /path/to/repo
============================================================

📂 [Step 1] Exploring repository structure...
📖 [Step 2] Reading core files...
📜 [Step 3] Analyzing git history...
🏗️  [Step 4] Identifying architecture...
✨ [Step 5] Generating onboarding guidance...
✅ [Step 6] Finalizing analysis...

============================================================
📋 GENERATED ONBOARDING GUIDANCE:
============================================================

# Project Onboarding Guide
...
```

## Next Steps

- Review the full [README.md](README.md)
- Check [DEVELOPMENT.md](DEVELOPMENT.md) for advanced usage
- Customize the agent prompts in `agent.py`
- Add your own analysis nodes to the workflow

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `GROQ_API_KEY not found` | Create `.env` file with your key |
| `Module not found` | Run `pip install -r requirements.txt` |
| `Permission denied` | Ensure you can read the repo directory |
| `Not a git repository` | Agent works without git, continues analysis |

## Example: Analyzing This Project

```bash
# Analyze the repo-auditor-agent itself!
python main.py .
```

Output will be a detailed onboarding guide for developers new to this project.

## Want More?

- **Add custom analysis**: See DEVELOPMENT.md
- **Change LLM model**: Edit `generate_guidance_node()` in agent.py
- **Analyze differently**: Modify system prompt
- **Multiple repos**: Run in a loop, cache results

---

**Questions?** Check README.md or DEVELOPMENT.md!
