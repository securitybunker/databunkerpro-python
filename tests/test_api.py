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
            },
        ]
        # Test bulk creation with global options
        options = {"finaltime": "1y", "slidingtime": "30d"}
        result = self.api.create_users_bulk(users_data, options)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("status"), "ok")
        self.assertIn("created", result)
        self.assertEqual(len(result["created"]), len(users_data))
        # Verify each created user
        for user_record in result["created"]:
            self.assertIn("token", user_record)
            self.assertIn("profile", user_record)
            self.assertEqual(
                user_record["profile"]["email"], user_record["profile"]["email"]
            )
            user_record = self.api.get_user("email", user_record["profile"]["email"])
            self.assertEqual(
                user_record["profile"]["email"], user_record["profile"]["email"]
            )
            self.assertEqual(
                user_record["profile"]["name"], user_record["profile"]["name"]
            )
            self.assertEqual(
                user_record["profile"]["phone"], user_record["profile"]["phone"]
            )
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

    def test_bulk_operations_workflow(self):
        """Test complete bulk operations workflow: create users, unlock bulk, and fetch all users."""
        # Step 1: Create 10 users using bulk creation
        users_data = []
        for i in range(10):
            users_data.append(
                {
                    "profile": {
                        "email": f"bulktest{random.randint(1000, 999999)}@example.com",
                        "name": f"Bulk Test User {i+1}",
                        "phone": str(random.randint(1000000, 9999999)),
                    }
                }
            )

        # Create users in bulk
        bulk_options = {"finaltime": "1y", "slidingtime": "30d"}
        create_result = self.api.create_users_bulk(users_data, bulk_options)

        # Verify bulk creation was successful
        self.assertIsInstance(create_result, dict)
        self.assertEqual(create_result.get("status"), "ok")
        self.assertIn("created", create_result)
        self.assertEqual(len(create_result["created"]), 10)

        # Store created user tokens for verification
        created_tokens = [user["token"] for user in create_result["created"]]

        # Step 2: Initiate bulk list unlock operation
        unlock_result = self.api.bulk_list_unlock()

        # Verify unlock operation was successful
        self.assertIsInstance(unlock_result, dict)
        self.assertEqual(unlock_result.get("status"), "ok")
        self.assertIn("unlockuuid", unlock_result)

        unlock_uuid = unlock_result["unlockuuid"]

        # Step 3: Fetch all users using bulk list operation
        # First, get the total count by fetching with a large limit
        bulk_users_result = self.api.bulk_list_users(unlock_uuid, offset=0, limit=100)

        # Verify bulk fetch was successful
        self.assertIsInstance(bulk_users_result, dict)
        self.assertEqual(bulk_users_result.get("status"), "ok")
        self.assertIn("rows", bulk_users_result)

        # Verify we can find our created users in the bulk results
        bulk_users = bulk_users_result["rows"]
        found_created_users = 0

        for bulk_user in bulk_users:
            if "token" in bulk_user and bulk_user["token"] in created_tokens:
                found_created_users += 1
                # Verify the user data matches what we created
                user_profile = bulk_user.get("profile", {})
                self.assertIn("email", user_profile)
                self.assertIn("name", user_profile)
                self.assertIn("phone", user_profile)

        # Verify we found all our created users
        self.assertEqual(
            found_created_users,
            10,
            f"Expected to find 10 created users in bulk results, but found {found_created_users}",
        )

        # Step 4: Test pagination by fetching users in smaller batches
        paginated_users = []
        offset = 0
        limit = 5

        while True:
            page_result = self.api.bulk_list_users(
                unlock_uuid, offset=offset, limit=limit
            )
            self.assertEqual(page_result.get("status"), "ok")

            page_users = page_result.get("rows", [])
            if not page_users:
                break

            paginated_users.extend(page_users)
            offset += limit

            # Safety break to prevent infinite loops
            if offset > 100:
                break

        # Verify pagination worked and we got users
        self.assertGreater(
            len(paginated_users), 0, "Pagination should return some users"
        )

        # Clean up: Delete the created users
        for token in created_tokens:
            try:
                delete_result = self.api.delete_user("token", token)
                # Don't fail the test if cleanup fails
                if delete_result.get("status") != "ok":
                    print(f"Warning: Failed to delete user with token {token}")
            except Exception as e:
                print(f"Warning: Exception during cleanup for token {token}: {str(e)}")

        return created_tokens


if __name__ == "__main__":
    unittest.main()
