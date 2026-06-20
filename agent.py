"""
LangGraph Agent for intelligent repository analysis.
Uses agentic workflow with step-by-step reasoning and tool use.
"""

import json
from typing import TypedDict, Annotated, Sequence
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from groq import Groq
import os

from tools import FilesystemToolkit, GitToolkit, RepoAnalyzerTools


class AgentState(TypedDict):
    """State management for the agent workflow."""
    target_repo_path: str
    current_step: str
    repo_type: dict
    core_files: dict
    file_contents: dict
    git_history: dict
    git_status: dict
    directory_structure: dict
    key_insights: dict
    messages: Sequence[BaseMessage]
    guidance_content: str
    analysis_complete: bool


class RepositoryAuditorAgent:
    """Main agent orchestrator using LangGraph."""
    
    def __init__(self, repo_path: str, groq_api_key: str):
        self.repo_path = repo_path
        self.groq_client = Groq(api_key=groq_api_key)
        self.tools_manager = RepoAnalyzerTools(repo_path)
        self.fs_toolkit = FilesystemToolkit(repo_path)
        self.git_toolkit = GitToolkit(repo_path)
        
        # Initialize the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("explore_repo", self.explore_repo_node)
        graph.add_node("read_core_files", self.read_core_files_node)
        graph.add_node("analyze_git_history", self.analyze_git_history_node)
        graph.add_node("identify_architecture", self.identify_architecture_node)
        graph.add_node("generate_guidance", self.generate_guidance_node)
        graph.add_node("finalize", self.finalize_node)
        
        # Set entry point
        graph.set_entry_point("explore_repo")
        
        # Add edges
        graph.add_edge("explore_repo", "read_core_files")
        graph.add_edge("read_core_files", "analyze_git_history")
        graph.add_edge("analyze_git_history", "identify_architecture")
        graph.add_edge("identify_architecture", "generate_guidance")
        graph.add_edge("generate_guidance", "finalize")
        graph.add_edge("finalize", END)
        
        return graph.compile()
    
    def explore_repo_node(self, state: AgentState) -> AgentState:
        """Step 1: Explore repository structure and detect type."""
        print("\n📂 [Step 1] Exploring repository structure...")
        
        # Detect repo type
        repo_type = self.tools_manager.detect_repo_type()
        
        # Get directory structure
        dir_structure = self.fs_toolkit.list_directory(".")
        
        # Get core files
        core_files = self.tools_manager.get_core_files_to_read()
        
        state["current_step"] = "explore_repo"
        state["repo_type"] = repo_type
        state["directory_structure"] = dir_structure
        state["core_files"] = core_files
        state["file_contents"] = {}
        
        print(f"  ✅ Detected language: {repo_type['language']}")
        print(f"  ✅ Found {core_files['count']} core files")
        print(f"  ✅ Frameworks: {', '.join(repo_type['frameworks']) or 'None'}")
        
        return state
    
    def read_core_files_node(self, state: AgentState) -> AgentState:
        """Step 2: Read important core files identified by agent."""
        print("\n📖 [Step 2] Reading core files...")
        
        core_files_to_read = state["core_files"]["core_files"][:5]  # Read top 5
        
        for file_path in core_files_to_read:
            print(f"  📄 Reading {file_path}...")
            content = self.fs_toolkit.read_file(file_path)
            
            if "error" not in content:
                state["file_contents"][file_path] = {
                    "size": content["size"],
                    "lines": content["lines"],
                    "truncated": content.get("truncated", False),
                    "content": content["content"][:3000]  # Store first 3000 chars
                }
                print(f"    ✅ Read {content['lines']} lines")
            else:
                print(f"    ⚠️  Error: {content['error']}")
        
        state["current_step"] = "read_core_files"
        return state
    
    def analyze_git_history_node(self, state: AgentState) -> AgentState:
        """Step 3: Analyze git history and recent changes."""
        print("\n📜 [Step 3] Analyzing git history...")
        
        # Get recent commits
        git_log = self.git_toolkit.get_git_log(max_commits=20)
        git_status = self.git_toolkit.get_git_status()
        recent_changes = self.git_toolkit.get_recent_changes(days=90)
        
        state["git_history"] = git_log
        state["git_status"] = git_status
        
        if "commits" in git_log:
            print(f"  ✅ Found {git_log['count']} recent commits")
        if "recent_changes" in recent_changes:
            print(f"  ✅ Found {recent_changes['count']} changes in last 90 days")
        print(f"  ✅ Repository status: {git_status.get('status', 'unknown')}")
        
        state["current_step"] = "analyze_git_history"
        return state
    
    def identify_architecture_node(self, state: AgentState) -> AgentState:
        """Step 4: Identify architecture, patterns, and key modules."""
        print("\n🏗️  [Step 4] Identifying architecture...")
        
        # Simple architecture detection based on file structure
        insights = {
            "language": state["repo_type"]["language"],
            "has_tests": state["repo_type"]["has_tests"],
            "has_docs": state["repo_type"]["has_docs"],
            "frameworks": state["repo_type"]["frameworks"],
            "entry_points": [],
            "main_modules": []
        }
        
        # Find potential entry points
        dir_structure = state["directory_structure"]
        if "files" in dir_structure:
            for file_info in dir_structure["files"]:
                name = file_info["name"] if isinstance(file_info, dict) else file_info
                if any(entry in name.lower() for entry in ["main", "app", "index", "start"]):
                    insights["entry_points"].append(name)
        
        # Identify main modules from directory structure
        if "directories" in dir_structure:
            potential_modules = [d for d in dir_structure["directories"] 
                               if not d.startswith('.') and d not in 
                               ['node_modules', '__pycache__', 'dist', 'build', 'venv']]
            insights["main_modules"] = potential_modules[:10]
        
        state["key_insights"] = insights
        state["current_step"] = "identify_architecture"
        
        print(f"  ✅ Found {len(insights['entry_points'])} entry points")
        print(f"  ✅ Identified {len(insights['main_modules'])} main modules")
        
        return state
    
    def generate_guidance_node(self, state: AgentState) -> AgentState:
        """Step 5: Use LLM to generate onboarding guidance."""
        print("\n✨ [Step 5] Generating onboarding guidance...")
        
        # Prepare context for LLM
        context = self._prepare_llm_context(state)
        
        # Call Groq API with structured prompt
        messages = [
            {
                "role": "system",
                "content": """You are an expert developer onboarding specialist. Your task is to create a comprehensive, 
engaging guidance document for new developers joining the team. 

The document should:
1. Start with a quick overview and getting started guide
2. Explain the project structure and architecture
3. Describe key modules and their responsibilities
4. Include setup and development instructions
5. Explain git workflow and recent project changes
6. Highlight important patterns and conventions
7. List useful commands and resources

Make it clear, well-organized, and developer-friendly. Use markdown formatting."""
            },
            {
                "role": "user",
                "content": f"""Based on this repository analysis, create a detailed guidance.md for new developers:

{context}

Generate the complete onboarding guide in markdown format."""
            }
        ]
        
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Free tier model
            messages=messages,
            temperature=0.7,
            max_tokens=4000
        )
        
        guidance = response.choices[0].message.content
        state["guidance_content"] = guidance
        state["current_step"] = "generate_guidance"
        
        print("  ✅ Guidance generated successfully")
        
        return state
    
    def finalize_node(self, state: AgentState) -> AgentState:
        """Step 6: Finalize and prepare output."""
        print("\n✅ [Step 6] Finalizing analysis...")
        
        state["analysis_complete"] = True
        state["current_step"] = "finalize"
        
        return state
    
    def _prepare_llm_context(self, state: AgentState) -> str:
        """Prepare context string for LLM."""
        context_parts = []
        
        # Repository type
        context_parts.append(f"**Repository Type**: {state['repo_type']['language']}")
        if state['repo_type']['frameworks']:
            context_parts.append(f"**Frameworks/Tools**: {', '.join(state['repo_type']['frameworks'])}")
        
        # Key insights
        context_parts.append(f"\n**Architecture Summary**:")
        context_parts.append(f"- Entry Points: {', '.join(state['key_insights'].get('entry_points', [])) or 'None identified'}")
        context_parts.append(f"- Main Modules: {', '.join(state['key_insights'].get('main_modules', [])[:5]) or 'Root-level'}")
        
        # File contents
        if state["file_contents"]:
            context_parts.append(f"\n**Key Files Content**:")
            for file_path, info in list(state["file_contents"].items())[:3]:
                context_parts.append(f"\n**{file_path}** ({info['lines']} lines)")
                context_parts.append(f"```\n{info['content'][:500]}...\n```")
        
        # Git history
        if "commits" in state["git_history"]:
            context_parts.append(f"\n**Recent Commits** (last 10):")
            for commit in state["git_history"]["commits"][:10]:
                context_parts.append(f"- {commit}")
        
        # Project structure
        context_parts.append(f"\n**Directory Structure**:")
        if state["directory_structure"]["directories"]:
            context_parts.append("Directories: " + ", ".join(state["directory_structure"]["directories"][:10]))
        if state["directory_structure"]["files"]:
            files = [f["name"] if isinstance(f, dict) else f for f in state["directory_structure"]["files"]]
            context_parts.append("Root Files: " + ", ".join(files[:10]))
        
        return "\n".join(context_parts)
    
    def run(self) -> dict:
        """Execute the agent workflow."""
        print(f"\n🚀 Starting Repository Audit Agent for: {self.repo_path}")
        print("=" * 60)
        
        initial_state: AgentState = {
            "target_repo_path": self.repo_path,
            "current_step": "init",
            "repo_type": {},
            "core_files": {},
            "file_contents": {},
            "git_history": {},
            "git_status": {},
            "directory_structure": {},
            "key_insights": {},
            "messages": [],
            "guidance_content": "",
            "analysis_complete": False
        }
        
        # Run the workflow
        final_state = self.graph.invoke(initial_state)
        
        print("\n" + "=" * 60)
        print("✅ Analysis Complete!")
        print(f"Repository: {self.repo_path}")
        print(f"Language: {final_state['repo_type']['language']}")
        print(f"Files Analyzed: {len(final_state['file_contents'])}")
        
        return final_state
