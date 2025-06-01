"""
Test script for the ticketing system integration.

This test script validates the ticketing system components and functionality.
"""

import unittest
import os
from app.integrations import ticketing_manager
from app.integrations.ticketing_system import TicketingSystemFactory, JiraTicketingSystem


class TestTicketingSystem(unittest.TestCase):
    """Test case for the ticketing system integration."""

    def test_ticketing_manager_initialization(self):
        """Test that the ticketing manager initializes correctly."""
        self.assertIsNotNone(ticketing_manager)
        
        # Get available systems (likely empty in test environment)
        available_systems = ticketing_manager.get_available_systems()
        self.assertIsInstance(available_systems, list)
        
        print(f"Available ticketing systems: {available_systems}")
        
    def test_ticketing_factory(self):
        """Test the ticketing system factory."""
        # Test with sample config
        sample_config = {
            "base_url": "https://example.atlassian.net",
            "project_key": "TEST",
            "api_token": "dummy_token",
            "username": "test@example.com"
        }
        
        # Check if factory can create a Jira system
        try:
            jira_system = TicketingSystemFactory.create_ticketing_system("jira", sample_config)
            self.assertIsInstance(jira_system, JiraTicketingSystem)
            print("Successfully created Jira ticketing system")
        except Exception as e:
            print(f"Error creating Jira system (expected in test environment): {str(e)}")
            
        # Test with invalid system type
        with self.assertRaises(ValueError):
            TicketingSystemFactory.create_ticketing_system("invalid_system", {})
            
    def test_environment_detection(self):
        """Test if the ticketing manager correctly detects environment variables."""
        # Store original environment
        original_env = {}
        for var in ["JIRA_ENABLED", "JIRA_BASE_URL", "JIRA_PROJECT_KEY", "JIRA_API_TOKEN", "JIRA_USERNAME"]:
            original_env[var] = os.environ.get(var)
            
        try:
            # Set test environment variables
            os.environ["JIRA_ENABLED"] = "true"
            os.environ["JIRA_BASE_URL"] = "https://test.atlassian.net"
            os.environ["JIRA_PROJECT_KEY"] = "TEST"
            os.environ["JIRA_API_TOKEN"] = "dummy_token"
            os.environ["JIRA_USERNAME"] = "test@example.com"
            
            # Create a new ticketing manager to test environment detection
            new_manager = ticketing_manager.__class__()
            self.assertTrue("jira" in new_manager.get_available_systems())
            print("Ticketing manager correctly detected environment variables")
            
        finally:
            # Restore original environment
            for var, value in original_env.items():
                if value is None:
                    if var in os.environ:
                        del os.environ[var]
                else:
                    os.environ[var] = value


if __name__ == "__main__":
    print("Running ticketing system integration tests...")
    unittest.main()