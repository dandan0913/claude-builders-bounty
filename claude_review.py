#!/usr/bin/env python3
"""
PR Review Agent - Analyzes GitHub PR diffs and generates structured review comments.

Usage:
    python claude_review.py --pr https://github.com/owner/repo/pull/123
    python claude_review.py --diff path/to/diff.patch
    python claude_review.py --pr URL --output review.md
"""

import argparse
import sys
import os
import re
from datetime import datetime

try:
    import requests
except ImportError:
    print("Error: requests library required. pip install requests")
    sys.exit(1)


class PRReviewAgent:
    """Analyzes PR diffs and generates structured review comments."""
    
    def __init__(self, github_token=None):
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN", "")
        self.headers = {
            "Accept": "application/vnd.github.v3.diff",
            "User-Agent": "PR-Review-Agent/1.0"
        }
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"
    
    def fetch_pr_diff(self, pr_url):
        """Fetch the diff for a given PR URL."""
        match = re.search(r"/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
        if not match:
            raise ValueError(f"Invalid PR URL: {pr_url}")
        
        owner, repo, pr_num = match.groups()
        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_num}/diff"
        
        print(f"Fetching PR diff from: {api_url}", file=sys.stderr)
        response = requests.get(api_url, headers=self.headers)
        response.raise_for_status()
        return response.text
    
    def analyze_diff(self, diff):
        """Analyze a diff and extract structured information."""
        analysis = {
            "summary": "",
            "risk_level": "Medium",
            "risks": [],
            "suggestions": [],
            "confidence": "Medium",
            "stats": {},
            "categories": {}
        }
        
        # Calculate basic stats
        lines_added = diff.count("+") - diff.count("+++")
        lines_removed = diff.count("-") - diff.count("---")
        
        analysis["stats"] = {
            "lines_added": max(0, lines_added),
            "lines_removed": max(0, lines_removed),
            "total_changes": max(0, lines_added + lines_removed)
        }
        
        # Identify risk patterns
        risk_patterns = {
            "Security": [r"password", r"secret", r"api.key", r"token"],
            "Database": [r"DROP TABLE", r"TRUNCATE", r"ALTER TABLE"],
            "Dependencies": [r"package.json", r"requirements.txt", r"go.sum"],
            "Configuration": [r".env", r"config.yml", r"config.json"]
        }
        
        for category, patterns in risk_patterns.items():
            for pattern in patterns:
                if re.search(pattern, diff, re.IGNORECASE):
                    analysis["risks"].append(f"{category}: Potential {category.lower()} changes detected")
                    break
        
        # Identify file changes
        file_changes = {}
        for line in diff.split("\n"):
            if line.startswith("+++ b/"):
                current_file = line[6:]
                file_changes[current_file] = {"added": 0, "removed": 0}
            elif line.startswith("+") and not line.startswith("+++"):
                if file_changes:
                    last_file = list(file_changes.keys())[-1]
                    file_changes[last_file]["added"] += 1
            elif line.startswith("-") and not line.startswith("---"):
                if file_changes:
                    last_file = list(file_changes.keys())[-1]
                    file_changes[last_file]["removed"] += 1
        
        analysis["categories"] = {
            "files_changed": len(file_changes),
            "major_changes": [f for f, stats in file_changes.items() if stats["added"] + stats["removed"] > 50]
        }
        
        # Generate summary
        total_changes = analysis["stats"]["total_changes"]
        if total_changes > 500:
            analysis["summary"] = f"This PR introduces significant changes ({total_changes} lines modified). Requires thorough review."
            analysis["confidence"] = "High"
        elif total_changes > 100:
            analysis["summary"] = f"Moderate changes ({total_changes} lines modified). Focus on core functionality and edge cases."
            analysis["confidence"] = "Medium"
        else:
            analysis["summary"] = f"Small changes ({total_changes} lines modified). Quick review should suffice."
            analysis["confidence"] = "Medium"
        
        # Generate suggestions based on patterns
        if analysis["risks"]:
            analysis["suggestions"].append("Address identified risks before merging")
            analysis["suggestions"].append("Add tests for security-sensitive changes")
        
        if file_changes:
            analysis["suggestions"].append("Ensure all changed files have appropriate tests")
            analysis["suggestions"].append("Update documentation if public APIs changed")
        
        if not analysis["suggestions"]:
            analysis["suggestions"].append("Changes look straightforward")
            analysis["suggestions"].append("Run existing test suite to verify no regressions")
        
        # Determine risk level
        if len(analysis["risks"]) >= 3:
            analysis["risk_level"] = "High"
        elif len(analysis["risks"]) >= 1:
            analysis["risk_level"] = "Medium"
        else:
            analysis["risk_level"] = "Low"
        
        return analysis
    
    def format_review(self, analysis, pr_url):
        """Format the review as structured Markdown."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        review = f"# PR Review Report\n\n"
        review += f"**Generated:** {timestamp}\n"
        review += f"**PR URL:** {pr_url}\n\n"
        review += f"## Summary\n\n{analysis['summary']}\n\n"
        review += f"## Statistics\n\n"
        review += f"- **Lines Added:** {analysis['stats']['lines_added']}\n"
        review += f"- **Lines Removed:** {analysis['stats']['lines_removed']}\n"
        review += f"- **Files Changed:** {analysis['categories']['files_changed']}\n"
        review += f"- **Major Changes:** {len(analysis['categories']['major_changes'])} files with 50+ line changes\n\n"
        review += f"## Risk Assessment\n\n"
        review += f"**Risk Level:** {analysis['risk_level']}\n"
        review += f"**Confidence:** {analysis['confidence']}\n\n"
        review += f"### Identified Risks\n\n"
        
        if analysis["risks"]:
            for i, risk in enumerate(analysis["risks"], 1):
                review += f"{i}. {risk}\n"
        else:
            review += "- No significant risks identified\n"
        
        review += "\n### Recommendations\n\n"
        
        for suggestion in analysis["suggestions"]:
            review += f"- {suggestion}\n"
        
        review += f"\n---\n*Generated by PR Review Agent v1.0*\n"
        
        return review
    
    def run(self, pr_url=None, diff_file=None):
        """Main entry point for PR review."""
        if not pr_url and not diff_file:
            raise ValueError("Either --pr or --diff must be provided")
        
        if pr_url:
            print(f"Reviewing PR: {pr_url}", file=sys.stderr)
            diff = self.fetch_pr_diff(pr_url)
        elif diff_file:
            print(f"Reading diff from: {diff_file}", file=sys.stderr)
            with open(diff_file, "r", encoding="utf-8") as f:
                diff = f.read()
        
        analysis = self.analyze_diff(diff)
        review = self.format_review(analysis, pr_url or diff_file)
        
        return review


def main():
    parser = argparse.ArgumentParser(description="PR Review Agent - Analyze GitHub PRs")
    parser.add_argument("--pr", help="GitHub PR URL to review")
    parser.add_argument("--diff", help="Path to diff/patch file")
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--token", help="GitHub token (or set GITHUB_TOKEN env var)")
    
    args = parser.parse_args()
    
    try:
        agent = PRReviewAgent(github_token=args.token)
        review = agent.run(pr_url=args.pr, diff_file=args.diff)
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(review)
            print(f"Review saved to: {args.output}", file=sys.stderr)
        else:
            print(review)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
