"""
Standalone script to initialize permissions in the database.

Usage:
    python init_permissions_db.py
"""

import asyncio
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.init_permissions import initialize_all


async def main():
    """
    Main entry point for permission initialization.
    """
    try:
        await initialize_all()
        print("\n✅ Permission initialization completed successfully!")
        return 0
    except Exception as e:
        print(f"\n❌ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
