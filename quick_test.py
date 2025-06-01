"""
Quick test script to verify key components before deployment.
"""

import sys
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_module_imports():
    """Test that key modules can be imported."""
    try:
        from app.main import DORAAssessmentAgent
        from app.integrations import ticketing_manager
        from app.register.database import DatabaseHandler
        from ui.ticketing import render_ticketing_page
        
        logger.info("✅ All modules imported successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Module import failed: {str(e)}")
        return False
        
def test_database_connection():
    """Test database connection."""
    try:
        from app.register.database import DatabaseHandler
        db = DatabaseHandler()
        conn = db.get_connection()
        conn.close()
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False
        
def test_ticketing_manager():
    """Test the ticketing manager."""
    try:
        from app.integrations import ticketing_manager
        systems = ticketing_manager.get_available_systems()
        logger.info(f"✅ Ticketing manager loaded successfully. Available systems: {systems}")
        return True
    except Exception as e:
        logger.error(f"❌ Ticketing manager failed: {str(e)}")
        return False
    
def run_tests():
    """Run all tests and return overall status."""
    print("=" * 50)
    print("DORA Assessment Agent Quick Test")
    print("=" * 50)
    
    tests = [
        ("Module imports", test_module_imports),
        ("Database connection", test_database_connection),
        ("Ticketing manager", test_ticketing_manager)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\nRunning test: {name}")
        result = test_func()
        results.append(result)
        status = "PASSED" if result else "FAILED"
        print(f"Test {name}: {status}")
    
    print("\n" + "=" * 50)
    overall = all(results)
    print(f"Overall status: {'PASSED' if overall else 'FAILED'}")
    print("=" * 50)
    
    return overall

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)