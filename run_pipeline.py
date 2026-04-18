#!/usr/bin/env python3
"""
MASTER PIPELINE
Runs all 4 agents in sequence to generate complete content
"""

import subprocess
import sys
import argparse

def run_command(script_name, description):
    """Run a Python script and handle errors"""
    print("\n" + "=" * 60)
    print(f"🚀 {description}")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=False,
            text=True
        )
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        return False
    except FileNotFoundError:
        print(f"❌ {script_name} not found")
        return False

def main():
    parser = argparse.ArgumentParser(description='Run the complete content generation pipeline')
    parser.add_argument('--topic', type=str, help='Override topic (optional)')
    parser.add_argument('--skip-scrape', action='store_true', help='Skip scraping (use existing data)')
    args = parser.parse_args()
    
    print("=" * 60)
    print("🤖 AI CONTENT PIPELINE - STARTING")
    print("=" * 60)
    
    # Step 1: Scrape content (unless skipped)
    if not args.skip_scrape:
        if not run_command('content_scraper.py', 'AGENT 01: Content Scraper'):
            print("\n⚠️  Scraping failed, but continuing with existing data...")
    else:
        print("\n⏭️  Skipping scrape (using existing data)")
    
    # Step 2: Validate and rank topics
    if not run_command('content_validator.py', 'AGENT 02: Content Validator'):
        print("\n❌ Pipeline stopped: Validator failed")
        sys.exit(1)
    
    # Step 3: Generate script
    if args.topic:
        print(f"\n📌 Using custom topic: {args.topic}")
        if not run_command(f'voice_writer.py {args.topic}', 'AGENT 03: Voice Script Writer'):
            print("\n❌ Pipeline stopped: Script writer failed")
            sys.exit(1)
    else:
        if not run_command('voice_writer.py', 'AGENT 03: Voice Script Writer'):
            print("\n❌ Pipeline stopped: Script writer failed")
            sys.exit(1)
    
    # Step 4: Generate hooks
    if not run_command('hook_generator.py', 'AGENT 04: Hook Generator'):
        print("\n❌ Pipeline stopped: Hook generator failed")
        sys.exit(1)
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 PIPELINE COMPLETE!")
    print("=" * 60)
    
    # Read and display final outputs
    try:
        print("\n📄 FINAL SCRIPT:")
        with open('voice_script_output.txt', 'r', encoding='utf-8') as f:
            print(f.read())
        
        print("\n" + "=" * 60)
        print("🎣 FINAL HOOKS:")
        print("=" * 60)
        with open('hooks_output.txt', 'r', encoding='utf-8') as f:
            print(f.read())
    except FileNotFoundError:
        print("⚠️  Could not read output files")
    
    print("\n" + "=" * 60)
    print("✅ All files saved:")
    print("   • content_scraper_output.csv")
    print("   • content_validator_output.csv")
    print("   • voice_script_output.txt")
    print("   • hooks_output.txt")
    print("=" * 60)

if __name__ == "__main__":
    main()
