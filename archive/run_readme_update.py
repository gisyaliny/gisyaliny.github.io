#!/usr/bin/env python3
"""
Simple runner script for updating README.md
This script can be run to automatically update the README based on index.html
"""

import subprocess
import sys
import os

def main():
    """Run the README update script"""
    
    print("🔄 Updating README.md from index.html...")
    print("=" * 50)
    
    try:
        # Check if update_readme.py exists
        if not os.path.exists('update_readme.py'):
            print("❌ Error: update_readme.py not found!")
            return False
        
        # Run the update script
        result = subprocess.run([sys.executable, 'update_readme.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ README.md updated successfully!")
            print("\n📋 Summary:")
            print(result.stdout)
            return True
        else:
            print("❌ Error updating README.md:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 README.md has been updated with the latest information from index.html!")
    else:
        print("\n💥 Failed to update README.md. Please check the error messages above.")
