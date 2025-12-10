#!/usr/bin/env python3
"""Quick test to verify all modules import correctly"""
import sys

try:
    from src.sanitizer import InputSanitizer
    print("✅ sanitizer imported")
    
    from src.selector import ToolSelector
    print("✅ selector imported")
    
    from src.executor import ToolExecutor
    print("✅ executor imported")
    
    from src.reporter import Reporter
    print("✅ reporter imported")
    
    # Test basic functionality
    result = InputSanitizer.sanitize_task({"target": "127.0.0.1"})
    print(f"✅ sanitizer works: {result}")
    
    print("\n🎉 All modules working correctly!")
    sys.exit(0)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
