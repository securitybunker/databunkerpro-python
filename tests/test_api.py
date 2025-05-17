"""
Tests for the DatabunkerPro API client.
"""

import os
import random
import unittest

import requests

from databunkerpro import DatabunkerproAPI


class TestDatabunkerproAPI(unittest.TestCase):
    """Test cases for the DatabunkerPro API client."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment before running tests."""
        # Try to get credentials from environment first
        cls.api_url = os.getenv("DATABUNKER_API_URL", "https://pro.databunker.org")
        cls.api_token = os.getenv("DATABUNKER_API_TOKEN", "")
        cls.tenant_name = os.getenv("DATABUNKER_TENANT_NAME", "")

        # If credentials are not in environment, try to get them from sandbox server
        if not all([cls.api_token, cls.tenant_name]):
            try:
                response = requests.get(
                    "https://databunker.org/api/newtenant.php", verify=False
                )
                if response.ok:
                    data = response.json()
                    if data and data.get("status") == "ok":
                        cls.tenant_name = data["tenantname"]
                        cls.api_token = data["xtoken"]
                        print(
                            "\nSuccessfully connected to DatabunkerPro sandbox server"
                        )
                        print(f"Tenant: {cls.tenant_name}")
                        print(f"API URL: {cls.api_url}")
                    else:
                        raise unittest.SkipTest(
                            "Failed to get credentials from sandbox server"
                        )
                else:
                    raise unittest.SkipTest("Failed to connect to sandbox server")
            except Exception as e:
                raise unittest.SkipTest(f"Failed to get credentials: {str(e)}")

        # Initialize API client
        cls.api = DatabunkerproAPI(cls.api_url, cls.api_token, cls.tenant_name)

        # Test connection
        try:
            result = cls.api.get_system_stats()
            if not (isinstance(result, dict) and result.get("status") == "ok"):
                raise unittest.SkipTest("Failed to connect to DatabunkerPro server")
        except Exception as e:
            raise unittest.SkipTest(
                f"Failed to connect to DatabunkerPro server: {str(e)}"
            )

    def test_create_user(self):
        """Test user creation."""
        user_data = {
            "email": f"test{random.randint(1000, 999999)}@example.com",
            "name": f"Test User {random.randint(1000, 999999)}",
            "phone": str(random.randint(1000, 999999)),
        }
        result = self.api.create_user(user_data)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("status"), "ok")
        self.assertIn("token", result)
        return user_data["email"]

    def test_create_users_bulk(self):
        """Test bulk user creation."""
        # Create test data for multiple users
        users_data = [
            {
                "profile": {
                    "email": f"test{random.randint(1000, 999999)}@example.com",
                    "name": f"Test User {random.randint(1000, 999999)}",
                    "phone": str(random.randint(1000, 999999)),
                },
                # "groupname": "test-group",
                # "rolename": "test-role"
            },
            {
                "profile": {
                    "email": f"test{random.randint(1000, 999999)}@example.com",
                    "name": f"Test User {random.randint(1000, 999999)}",
                    "phone": str(random.randint(1000, 999999)),
                },
                # "groupid": 1,
                # "roleid": 1
            }
        ]
        # Test bulk creation with global options
        options = {
            "finaltime": "1y",
            "slidingtime": "30d"
        }
        result = self.api.create_users_bulk(users_data, options)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("status"), "ok")
        self.assertIn("created", result)
        self.assertEqual(len(result["created"]), len(users_data))
        # Verify each created user
        for user_record in result["created"]:
            self.assertIn("token", user_record)
            self.assertIn("profile", user_record)
            self.assertEqual(user_record["profile"]["email"], user_record["profile"]["email"])
            user_record = self.api.get_user("email", user_record["profile"]["email"])
            self.assertEqual(user_record["profile"]["email"], user_record["profile"]["email"])
            self.assertEqual(user_record["profile"]["name"], user_record["profile"]["name"])
            self.assertEqual(user_record["profile"]["phone"], user_record["profile"]["phone"])
        return [user["profile"]["email"] for user in users_data]

    def test_get_user(self):
        """Test user retrieval."""
        email = self.test_create_user()
        result = self.api.get_user("email", email)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("status"), "ok")
        self.assertIn("profile", result)
        return email

    def test_update_user(self):
        """Test user update."""
        email = self.test_get_user()
        update_data = {"name": "Updated Test User", "phone": "+9876543210"}
        result = self.api.update_user("email", email, update_data)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("status"), "ok")

        # Verify the update
        updated_user = self.api.get_user("email", email)
        self.assertEqual(updated_user["profile"]["name"], update_data["name"])
        self.assertEqual(updated_user["profile"]["phone"], update_data["phone"])

    def test_delete_user(self):
        """Test user deletion."""
        email = self.test_create_user()
        result = self.api.delete_user("email", email)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("status"), "ok")

    def test_get_system_stats(self):
        """Test getting system statistics."""
        result = self.api.get_system_stats()
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("status"), "ok")
        self.assertIn("stats", result)


if __name__ == "__main__":
    unittest.main()
