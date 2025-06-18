#!/usr/bin/env python3
"""
Automated GitHub Push Script for Google Colab
Pushes changes from /content to DeepSkyWonder/orbital-mechanics repository
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(cmd, description="", check=True):
    """Run a shell command and handle errors"""
    print(f"📋 {description if description else cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        if result.stdout.strip():
            print(f"✅ {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return e

def setup_git_config():
    """Set up git configuration using GitHub CLI"""
    print("🔧 Setting up git configuration...")
    
    # Get GitHub username
    result = run_command("gh api user --jq '.login'", "Getting GitHub username")
    if isinstance(result, subprocess.CalledProcessError):
        print("❌ Failed to get GitHub username. Make sure you're authenticated with 'gh auth login'")
        return False
    
    username = result.stdout.strip()
    email = f"{username}@users.noreply.github.com"
    
    # Set git config
    run_command(f'git config user.name "{username}"', "Setting git username")
    run_command(f'git config user.email "{email}"', "Setting git email")
    run_command('git config pull.rebase false', "Setting merge strategy")
    
    return True

def init_repository():
    """Initialize git repository if needed"""
    if not os.path.exists('.git'):
        print("🚀 Initializing git repository...")
        run_command("git init", "Initializing git repository")
        
        # Add remote if it doesn't exist
        result = run_command("git remote get-url origin", "Checking remote origin", check=False)
        if isinstance(result, subprocess.CalledProcessError):
            run_command("git remote add origin https://github.com/DeepSkyWonder/orbital-mechanics.git", "Adding remote origin")
    else:
        print("✅ Git repository already initialized")

def check_changes():
    """Check if there are any changes to commit"""
    result = run_command("git status --porcelain", "Checking for changes")
    if isinstance(result, subprocess.CalledProcessError):
        return False
    
    changes = result.stdout.strip()
    if not changes:
        print("ℹ️  No changes detected")
        return False
    
    print(f"📝 Changes detected:\n{changes}")
    return True

def create_commit_message():
    """Generate a commit message based on current timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""Update orbital mechanics tools - {timestamp}

Automated commit from Google Colab environment.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""

def push_changes():
    """Main function to push changes to GitHub"""
    print("🚀 Starting GitHub push automation...")
    print(f"📁 Current directory: {os.getcwd()}")
    
    # Change to /content directory
    os.chdir('/content')
    print(f"📁 Changed to: {os.getcwd()}")
    
    # Setup git configuration
    if not setup_git_config():
        return False
    
    # Initialize repository
    init_repository()
    
    # Check for changes
    if not check_changes():
        print("✅ Repository is up to date!")
        return True
    
    print("📦 Staging changes...")
    
    # Remove cached files from tracking if they exist
    run_command("git rm -r --cached __pycache__/ 2>/dev/null || true", "Removing cached files", check=False)
    
    run_command("git add .", "Staging all changes")
    
    # Pull latest changes first
    print("⬇️  Pulling latest changes...")
    result = run_command("git pull origin main --allow-unrelated-histories", "Pulling from remote", check=False)
    
    # Handle merge conflicts (basic resolution - prefer local changes)
    if isinstance(result, subprocess.CalledProcessError) and "CONFLICT" in result.stderr:
        print("⚠️  Merge conflict detected. Attempting automatic resolution...")
        
        # Get list of conflicted files
        status_result = run_command("git status --porcelain", "Getting conflict status")
        if not isinstance(status_result, subprocess.CalledProcessError):
            conflicted_files = [line.strip()[3:] for line in status_result.stdout.split('\n') 
                              if line.startswith('UU ')]
            
            for file in conflicted_files:
                print(f"🔧 Resolving conflict in {file}")
                # Simple resolution: remove conflict markers and keep our changes
                try:
                    with open(file, 'r') as f:
                        content = f.read()
                    
                    # Remove conflict markers and keep HEAD version
                    lines = content.split('\n')
                    resolved_lines = []
                    skip_mode = False
                    
                    for line in lines:
                        if line.startswith('<<<<<<< HEAD'):
                            skip_mode = False
                            continue
                        elif line.startswith('======='):
                            skip_mode = True
                            continue
                        elif line.startswith('>>>>>>> '):
                            skip_mode = False
                            continue
                        
                        if not skip_mode:
                            resolved_lines.append(line)
                    
                    with open(file, 'w') as f:
                        f.write('\n'.join(resolved_lines))
                    
                    run_command(f"git add {file}", f"Staging resolved file {file}")
                    
                except Exception as e:
                    print(f"❌ Failed to automatically resolve conflict in {file}: {e}")
                    print("Please resolve conflicts manually and run the script again.")
                    return False
        
        # Commit the merge
        run_command('git commit -m "Resolve merge conflicts automatically"', "Committing merge resolution")
    
    # Create commit
    commit_msg = create_commit_message()
    print("💾 Creating commit...")
    
    # Use heredoc for commit message to handle multi-line
    escaped_msg = commit_msg.replace('"', '\\"')
    commit_cmd = f'git commit -m "{escaped_msg}"'
    result = run_command(commit_cmd, "Creating commit", check=False)
    
    if isinstance(result, subprocess.CalledProcessError):
        if "nothing to commit" in result.stdout:
            print("ℹ️  Nothing new to commit")
        else:
            print(f"❌ Commit failed: {result.stderr}")
            return False
    
    # Debug: Check current state before push
    print("🔍 Debug: Checking current state...")
    run_command("git log --oneline -3", "Recent commits")
    run_command("git status", "Git status")
    run_command("git remote -v", "Remote info")
    
    # Push to GitHub
    print("⬆️  Pushing to GitHub...")
    result = run_command("git push origin main", "Pushing to GitHub")
    
    if isinstance(result, subprocess.CalledProcessError):
        print(f"🔍 Debug: Push failed. Error: {result.stderr}")
        
        if "non-fast-forward" in result.stderr:
            print("⚠️  Non-fast-forward error. Pulling and retrying...")
            
            # Debug: Check remote state
            run_command("git fetch origin", "Fetching remote info")
            run_command("git log --oneline origin/main -3", "Remote commits")
            
            pull_result = run_command("git pull origin main --allow-unrelated-histories", "Pulling latest changes")
            
            if isinstance(pull_result, subprocess.CalledProcessError):
                print(f"❌ Failed to pull remote changes: {pull_result.stderr}")
                return False
            
            # Debug: Check state after pull
            run_command("git log --oneline -3", "Commits after pull")
            
            print("🔄 Retrying push after pull...")
            result = run_command("git push origin main", "Retrying push")
            
            if isinstance(result, subprocess.CalledProcessError):
                print(f"❌ Push still failed after pull: {result.stderr}")
                return False
            else:
                print("✅ Push succeeded after pull!")
        else:
            print("❌ Push failed for other reason. Trying to set upstream...")
            result = run_command("git push -u origin main", "Pushing with upstream")
            if isinstance(result, subprocess.CalledProcessError):
                print(f"❌ Push failed completely: {result.stderr}")
                return False
    else:
        print("✅ Push succeeded on first try!")
    
    print("✅ Successfully pushed changes to GitHub!")
    print("🔗 Repository: https://github.com/DeepSkyWonder/orbital-mechanics")
    return True

def main():
    """Entry point for the script"""
    try:
        success = push_changes()
        if success:
            print("\n🎉 All done! Your changes are now on GitHub.")
        else:
            print("\n❌ Push operation failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()