#!/usr/bin/env python3
"""
Repository Auditor Agent - Main Entry Point

Analyzes a repository and generates intelligent onboarding guidance.
Usage: python main.py /path/to/repo
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

from agent import RepositoryAuditorAgent

# Load environment variables
load_dotenv()

def main():
    parser = argparse.ArgumentParser(
        description="Analyze a repository and generate onboarding guidance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py /path/to/repo
  python main.py . --output guidance.md
  python main.py ~/projects/myapp --verbose
        """
    )
    
    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Path to the repository to analyze (default: current directory)"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file for guidance (stdout if not specified) - NOTE: writes to stdout only, doesn't modify repo"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate repo path
    repo_path = Path(args.repo_path).resolve()
    if not repo_path.exists():
        print(f"❌ Error: Repository path does not exist: {repo_path}")
        sys.exit(1)
    
    if not repo_path.is_dir():
        print(f"❌ Error: Path is not a directory: {repo_path}")
        sys.exit(1)
    
    # Verify Groq API key
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        print("❌ Error: GROQ_API_KEY environment variable not set")
        print("   Please set your Groq API key:")
        print("   - Create .env file with: GROQ_API_KEY=your_key")
        print("   - Or: export GROQ_API_KEY=your_key")
        sys.exit(1)
    
    try:
        # Initialize and run the agent
        agent = RepositoryAuditorAgent(str(repo_path), groq_api_key)
        result = agent.run()
        
        # Output the guidance
        print("\n" + "=" * 60)
        print("📋 GENERATED ONBOARDING GUIDANCE:")
        print("=" * 60)
        print(result["guidance_content"])
        
        # Optionally save to file (but don't modify the repo itself)
        if args.output:
            print(f"\n💾 Would save to: {args.output}")
            print("   (Read-only mode: set a separate output path if you want to save)")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()