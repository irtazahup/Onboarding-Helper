"""
Examples of using and extending the Repository Auditor Agent.
"""

# ============================================================================
# EXAMPLE 1: Basic Usage
# ============================================================================

def example_basic_usage():
    """Run the agent on a repository."""
    from agent import RepositoryAuditorAgent
    import os
    
    repo_path = "/path/to/your/repo"
    api_key = os.environ.get("GROQ_API_KEY")
    
    # Initialize and run
    agent = RepositoryAuditorAgent(repo_path, api_key)
    result = agent.run()
    
    # Access results
    print("Repository Type:", result["repo_type"]["language"])
    print("Files Analyzed:", len(result["file_contents"]))
    print("\nGuidance:\n", result["guidance_content"])


# ============================================================================
# EXAMPLE 2: Custom Post-Processing
# ============================================================================

def example_post_process_results():
    """Process agent results and save guidance to file."""
    from agent import RepositoryAuditorAgent
    from pathlib import Path
    import os
    
    repo_path = "/path/to/your/repo"
    api_key = os.environ.get("GROQ_API_KEY")
    
    # Run agent
    agent = RepositoryAuditorAgent(repo_path, api_key)
    result = agent.run()
    
    # Save to separate location (doesn't modify repo)
    output_path = Path("/output/guidance.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result["guidance_content"])
    
    print(f"✅ Saved to: {output_path}")


# ============================================================================
# EXAMPLE 3: Batch Analysis
# ============================================================================

def example_analyze_multiple_repos():
    """Analyze multiple repositories and compare insights."""
    from agent import RepositoryAuditorAgent
    import os
    from pathlib import Path
    
    repos = [
        "/path/to/repo1",
        "/path/to/repo2",
        "/path/to/repo3",
    ]
    
    api_key = os.environ.get("GROQ_API_KEY")
    results = []
    
    for repo_path in repos:
        if Path(repo_path).exists():
            print(f"\n📊 Analyzing {repo_path}...")
            agent = RepositoryAuditorAgent(repo_path, api_key)
            result = agent.run()
            results.append({
                "repo": repo_path,
                "language": result["repo_type"]["language"],
                "modules": result["key_insights"]["main_modules"],
                "has_tests": result["repo_type"]["has_tests"]
            })
    
    # Summary
    print("\n📈 Analysis Summary:")
    for r in results:
        print(f"  {r['repo']}: {r['language']}, {len(r['modules'])} modules")


# ============================================================================
# EXAMPLE 4: Custom Node - Add Security Analysis
# ============================================================================

def example_custom_security_node():
    """Extend agent with custom security analysis node."""
    from agent import RepositoryAuditorAgent, AgentState
    from langgraph.graph import StateGraph, END
    
    class SecurityAwareAgent(RepositoryAuditorAgent):
        """Agent with security analysis."""
        
        def _build_graph(self):
            """Build graph with security analysis node."""
            graph = super()._build_graph()
            
            # Add security analysis
            graph.add_node("security_scan", self.security_scan_node)
            
            # Insert before guidance generation
            # ... (modify graph edges as needed)
            
            return graph
        
        def security_scan_node(self, state: AgentState) -> AgentState:
            """Analyze for security patterns."""
            print("\n🔒 [Security] Scanning for security concerns...")
            
            security_findings = {
                "has_credentials_in_files": False,
                "uses_https": True,
                "dependencies_checked": False,
                "findings": []
            }
            
            # Simple check: look for common security anti-patterns
            for file_path, content in state["file_contents"].items():
                file_text = content.get("content", "").lower()
                
                if any(x in file_text for x in ["password=", "api_key=", "secret="]):
                    security_findings["has_credentials_in_files"] = True
                    security_findings["findings"].append(f"⚠️  Possible credentials in {file_path}")
            
            state["security_analysis"] = security_findings
            return state


# ============================================================================
# EXAMPLE 5: Integration with External Systems
# ============================================================================

def example_webhook_integration():
    """Send analysis results to external webhook."""
    from agent import RepositoryAuditorAgent
    import os
    import json
    import requests
    
    repo_path = "/path/to/repo"
    api_key = os.environ.get("GROQ_API_KEY")
    webhook_url = "https://your-api.example.com/webhook"
    
    # Run analysis
    agent = RepositoryAuditorAgent(repo_path, api_key)
    result = agent.run()
    
    # Send to webhook
    payload = {
        "repository": repo_path,
        "language": result["repo_type"]["language"],
        "modules": result["key_insights"]["main_modules"],
        "guidance": result["guidance_content"],
        "timestamp": str(__import__('datetime').datetime.now())
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ Sent to webhook successfully")
        else:
            print(f"⚠️  Webhook returned {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to send webhook: {e}")


# ============================================================================
# EXAMPLE 6: Cache Results for Quick Access
# ============================================================================

def example_caching():
    """Cache analysis results to avoid re-analysis."""
    from agent import RepositoryAuditorAgent
    import os
    import json
    from pathlib import Path
    
    def get_analysis(repo_path: str) -> dict:
        """Get analysis with caching."""
        cache_file = Path(f".cache_{Path(repo_path).name}.json")
        api_key = os.environ.get("GROQ_API_KEY")
        
        # Return cached if fresh
        if cache_file.exists():
            with open(cache_file) as f:
                cached = json.load(f)
                print("📦 Using cached analysis")
                return cached
        
        # Otherwise analyze and cache
        print("🔄 Running fresh analysis...")
        agent = RepositoryAuditorAgent(repo_path, api_key)
        result = agent.run()
        
        # Cache key fields
        cache_data = {
            "repo_type": result["repo_type"],
            "key_insights": result["key_insights"],
            "guidance_content": result["guidance_content"]
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        return cache_data
    
    # Use it
    analysis = get_analysis("/path/to/repo")
    print(analysis["repo_type"]["language"])


# ============================================================================
# EXAMPLE 7: Generate Multiple Output Formats
# ============================================================================

def example_multi_format_output():
    """Generate guidance in multiple formats."""
    from agent import RepositoryAuditorAgent
    import os
    import json
    from pathlib import Path
    
    repo_path = "/path/to/repo"
    api_key = os.environ.get("GROQ_API_KEY")
    
    agent = RepositoryAuditorAgent(repo_path, api_key)
    result = agent.run()
    
    # Save as Markdown
    Path("guidance.md").write_text(result["guidance_content"])
    
    # Save as JSON (structured)
    json_output = {
        "repository": repo_path,
        "analysis": {
            "language": result["repo_type"]["language"],
            "frameworks": result["repo_type"]["frameworks"],
            "modules": result["key_insights"]["main_modules"],
        },
        "guidance": result["guidance_content"]
    }
    Path("analysis.json").write_text(json.dumps(json_output, indent=2))
    
    # Save as HTML (simple)
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Project Onboarding</title>
    <style>body {{ font-family: Arial; margin: 20px; }}</style>
</head>
<body>
    <h1>{repo_path}</h1>
    <pre>{result['guidance_content']}</pre>
</body>
</html>"""
    Path("guidance.html").write_text(html)
    
    print("✅ Generated guidance.md, analysis.json, guidance.html")


# ============================================================================
# EXAMPLE 8: Command-Line Tool Enhancement
# ============================================================================

def example_cli_enhancement():
    """Enhance CLI with additional options."""
    import argparse
    from agent import RepositoryAuditorAgent
    import os
    from pathlib import Path
    
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_path")
    parser.add_argument("--format", choices=["md", "json", "html"], default="md")
    parser.add_argument("--depth", choices=["quick", "medium", "deep"], default="medium")
    parser.add_argument("--output", "-o")
    parser.add_argument("--cache", action="store_true")
    
    args = parser.parse_args()
    
    # Handle depth (modify agent behavior based on selection)
    # Handle format (different output formats)
    # Handle caching
    
    api_key = os.environ.get("GROQ_API_KEY")
    agent = RepositoryAuditorAgent(args.repo_path, api_key)
    result = agent.run()
    
    # Output based on format
    if args.output:
        if args.format == "json":
            import json
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
        else:  # md or html
            Path(args.output).write_text(result["guidance_content"])
        print(f"✅ Saved to {args.output}")


# ============================================================================
# EXAMPLE 9: Streaming Results (for large outputs)
# ============================================================================

def example_streaming_output():
    """Stream guidance output for real-time viewing."""
    from agent import RepositoryAuditorAgent
    import os
    
    repo_path = "/path/to/repo"
    api_key = os.environ.get("GROQ_API_KEY")
    
    agent = RepositoryAuditorAgent(repo_path, api_key)
    result = agent.run()
    
    # Stream output line by line
    print("📄 Onboarding Guide:")
    print("-" * 60)
    for line in result["guidance_content"].split('\n'):
        print(line)
        # Could add processing per line here


# ============================================================================
# EXAMPLE 10: Error Handling and Retry Logic
# ============================================================================

def example_error_handling_and_retry():
    """Handle errors gracefully with retry logic."""
    from agent import RepositoryAuditorAgent
    import os
    import time
    
    def analyze_with_retry(repo_path: str, max_retries: int = 3) -> dict:
        """Analyze with retry logic."""
        api_key = os.environ.get("GROQ_API_KEY")
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 Attempt {attempt + 1}/{max_retries}...")
                agent = RepositoryAuditorAgent(repo_path, api_key)
                result = agent.run()
                return result
            
            except KeyError as e:
                print(f"⚠️  Missing key: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
            
            except Exception as e:
                print(f"❌ Error: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        
        return None
    
    # Use it
    try:
        result = analyze_with_retry("/path/to/repo")
        if result:
            print("✅ Analysis successful!")
    except Exception as e:
        print(f"❌ All retries failed: {e}")


if __name__ == "__main__":
    print("📚 Repository Auditor Agent - Examples")
    print("=" * 60)
    print("\nThese are code examples showing various ways to use the agent.")
    print("Import and call any example function to see it in action.")
    print("\nAvailable examples:")
    print("  1. example_basic_usage() - Simple usage")
    print("  2. example_post_process_results() - Save results")
    print("  3. example_analyze_multiple_repos() - Batch processing")
    print("  4. example_custom_security_node() - Extend agent")
    print("  5. example_webhook_integration() - External integration")
    print("  6. example_caching() - Cache results")
    print("  7. example_multi_format_output() - Multiple formats")
    print("  8. example_cli_enhancement() - Better CLI")
    print("  9. example_streaming_output() - Stream results")
    print(" 10. example_error_handling_and_retry() - Robust handling")
