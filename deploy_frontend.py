#!/usr/bin/env python3
"""
Helper script to deploy the GA4 MCP Chat frontend to GitHub Pages
"""

import os
import subprocess
import sys
import re
from pathlib import Path

def check_git():
    """Check if git is installed and we're in a git repository"""
    try:
        # Check if git is installed
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        
        # Check if we're in a git repository
        result = subprocess.run(["git", "status"], check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError:
        print("Error: Not in a git repository or git command failed.")
        print("Please initialize a git repository first.")
        return False
    except FileNotFoundError:
        print("Error: Git is not installed or not in PATH.")
        return False

def get_remote_url():
    """Get the GitHub remote URL"""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True
        )
        remote_url = result.stdout.strip()
        
        # Extract username and repo name from GitHub URL
        github_pattern = r"github\.com[:/]([^/]+)/([^/\.]+)(\.git)?$"
        match = re.search(github_pattern, remote_url)
        
        if match:
            username = match.group(1)
            repo_name = match.group(2)
            if match.group(3):  # Remove .git suffix if present
                repo_name = repo_name[:-4]
            return username, repo_name
        else:
            print(f"Warning: Could not parse GitHub username and repo from URL: {remote_url}")
            return None, None
    except subprocess.CalledProcessError:
        print("Error: Failed to get remote URL. Is 'origin' remote configured?")
        return None, None

def update_backend_url(username, repo_name):
    """Update the BACKEND_URL in app.js if needed"""
    app_js_path = Path("frontend/app.js")
    
    if not app_js_path.exists():
        print(f"Error: {app_js_path} not found.")
        return False
    
    with open(app_js_path, "r") as f:
        content = f.read()
    
    # Check if BACKEND_URL is still the placeholder
    if "https://YOUR-BACKEND-DEPLOYMENT/query" in content:
        print("\nThe BACKEND_URL in frontend/app.js is still set to the placeholder.")
        deploy_backend = input("Have you deployed your backend? (y/n): ").lower()
        
        if deploy_backend == 'y':
            backend_url = input("Enter your backend URL (e.g., https://your-backend.com/query): ")
            if backend_url:
                new_content = content.replace(
                    "const BACKEND_URL = \"https://YOUR-BACKEND-DEPLOYMENT/query\";",
                    f"const BACKEND_URL = \"{backend_url}\";"
                )
                
                with open(app_js_path, "w") as f:
                    f.write(new_content)
                
                print(f"Updated BACKEND_URL to {backend_url}")
                return True
        else:
            print("\nWarning: You should deploy your backend before deploying the frontend.")
            print("The chat will not work without a backend.")
            proceed = input("Do you want to proceed anyway? (y/n): ").lower()
            if proceed != 'y':
                return False
    
    return True

def deploy_to_github_pages():
    """Deploy the frontend to GitHub Pages"""
    try:
        # Check if gh-pages branch exists
        result = subprocess.run(
            ["git", "branch", "-a"],
            capture_output=True,
            text=True
        )
        
        branches = result.stdout.strip().split('\n')
        has_gh_pages = any('gh-pages' in branch for branch in branches)
        
        if has_gh_pages:
            print("The gh-pages branch already exists.")
            force_push = input("Do you want to force update it? (y/n): ").lower()
            if force_push != 'y':
                return False
        
        # Make sure we have the latest changes
        print("\nCommitting any changes to frontend...")
        subprocess.run(["git", "add", "frontend"], check=True)
        try:
            subprocess.run(
                ["git", "commit", "-m", "Update frontend before deployment"],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError:
            # It's okay if there's nothing to commit
            pass
        
        # Deploy using git subtree push
        print("\nDeploying frontend to GitHub Pages...")
        push_command = ["git", "subtree", "push", "--prefix", "frontend", "origin", "gh-pages"]
        if has_gh_pages and force_push == 'y':
            # Force push if requested
            push_command = ["git", "push", "origin", "`git subtree split --prefix frontend master`:gh-pages", "--force"]
        
        subprocess.run(push_command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during deployment: {e}")
        return False

def main():
    print("GA4 MCP Chat - Frontend Deployment Tool\n")
    
    if not check_git():
        sys.exit(1)
    
    username, repo_name = get_remote_url()
    if username and repo_name:
        print(f"\nDetected GitHub repository: {username}/{repo_name}")
        print(f"Your frontend will be available at: https://{username}.github.io/{repo_name}/")
    
        if not update_backend_url(username, repo_name):
            print("\nDeployment cancelled.")
            sys.exit(1)
        
        if deploy_to_github_pages():
            print("\nDeployment successful!")
            print(f"Your frontend is now available at: https://{username}.github.io/{repo_name}/")
            print("\nNote: It might take a few minutes for GitHub Pages to update.")
        else:
            print("\nDeployment failed.")
            sys.exit(1)
    else:
        print("\nCould not determine GitHub repository information.")
        print("Please make sure your git remote 'origin' is set to a GitHub repository.")
        sys.exit(1)

if __name__ == "__main__":
    main()