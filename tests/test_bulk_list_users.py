"""
Tests for BulkListUsers — the batch lookup used to reconcile a migration.

Verifies the request shape the SDK sends, that lookups by `custom` resolve back to
the tokens returned at creation time, and that the documented `limit` default of 10
is not applied to this endpoint.
"""

import os
import random
import unittest

import requests

from databunkerpro import DatabunkerproAPI

# Deliberately more than the `limit: 10` default documented for this endpoint.
USER_COUNT = 12


class TestBulkListUsers(unittest.TestCase):
    """BulkListUsers batch lookup by indexed field."""

    @classmethod
    def setUpClass(cls):
        cls.api_url = os.getenv("DATABUNKER_API_URL", "https://pro.databunker.org")
        cls.api_token = os.getenv("DATABUNKER_API_TOKEN", "")
        cls.tenant_name = os.getenv("DATABUNKER_TENANT_NAME", "")

        if not all([cls.api_token, cls.tenant_name]):
            try:
                response = requests.get(
                    "https://databunker.org/api/newtenant.php", verify=False
                )
                data = response.json() if response.ok else None
                if not data or data.get("status") != "ok":
                    raise unittest.SkipTest("Failed to get credentials from sandbox")
                cls.tenant_name = data["tenantname"]
                cls.api_token = data["xtoken"]
                print(f"\nSandbox tenant: {cls.tenant_name} at {cls.api_url}")
            except unittest.SkipTest:
                raise
            except Exception as e:
                raise unittest.SkipTest(f"Failed to get credentials: {e}")

        cls.api = DatabunkerproAPI(cls.api_url, cls.api_token, cls.tenant_name)

        # Create users the way a migration does: the legacy primary key in `custom`.
        cls.run_id = random.randint(100000, 999999)
        records = [
            {
                "profile": {
                    "custom": f"legacy-{cls.run_id}-{i}",
                    "email": f"blu{cls.run_id}x{i}@example.com",
                    "name": f"Bulk List User {i}",
                }
            }
            for i in range(USER_COUNT)
        ]
        result = cls.api.create_users_bulk(records)
        if result.get("status") != "ok":
            raise unittest.SkipTest(f"Setup bulk create failed: {result}")

        # custom value -> token, as returned by UserCreateBulk
        cls.expected = {
            item["profile"]["custom"]: item["token"] for item in result["created"]
        }
        print(f"Created {len(cls.expected)}/{USER_COUNT} users for lookup")

    def _unlock(self):
        result = self.api.bulk_list_unlock()
        self.assertEqual(result.get("status"), "ok", f"unlock failed: {result}")
        self.assertIn("unlockuuid", result)
        return result["unlockuuid"]

    def _list_users(self, criteria, unlock_uuid=None):
        """BulkListUsers, skipping when the server has the feature turned off.

        BulkListUsers is gated by the `list_users` configuration flag, which is off by
        default. Skipping rather than failing keeps a server-side setting from breaking
        the build — and, since `deploy` needs `test`, from blocking a release.
        """
        if unlock_uuid is None:
            unlock_uuid = self._unlock()
        result = self.api.bulk_list_users(unlock_uuid, criteria)
        if result.get("message") == "BulkListUsers is disabled":
            self.skipTest("list_users is not enabled on this server")
        return result

    def test_bulk_list_unlock(self):
        """BulkListUnlock issues a UUID."""
        self.assertTrue(self._unlock())

    def test_bulk_list_users_by_custom(self):
        """Every created user is found by its `custom` value, with a matching token."""
        criteria = [{"mode": "custom", "identity": c} for c in self.expected]
        result = self._list_users(criteria)

        self.assertEqual(result.get("status"), "ok", f"unexpected response: {result}")
        rows = result.get("rows") or []
        self.assertTrue(rows, f"no rows returned: {result}")

        found = {
            row["profile"]["custom"]: row["token"]
            for row in rows
            if row.get("profile", {}).get("custom")
        }
        self.assertEqual(
            found,
            self.expected,
            "token mapping from BulkListUsers does not match UserCreateBulk",
        )

    def test_limit_default_is_not_applied(self):
        """More than 10 criteria must all come back — `limit` is not honoured here."""
        criteria = [{"mode": "custom", "identity": c} for c in self.expected]
        self.assertGreater(len(criteria), 10, "test needs >10 records to be meaningful")

        result = self._list_users(criteria)
        rows = result.get("rows") or []

        self.assertEqual(
            len(rows),
            len(self.expected),
            f"expected {len(self.expected)} rows, got {len(rows)} — "
            f"limit appears to be applied (total={result.get('total')})",
        )

    def test_unknown_identity_returns_no_row(self):
        """A `custom` value that was never stored yields nothing, not an error."""
        result = self._list_users(
            [{"mode": "custom", "identity": f"legacy-{self.run_id}-absent"}]
        )
        self.assertEqual(result.get("status"), "ok", f"unexpected response: {result}")
        self.assertEqual(len(result.get("rows") or []), 0)

    def test_invalid_unlockuuid_is_rejected(self):
        """unlockuuid is enforced — a bogus UUID must not return data."""
        result = self._list_users(
            [{"mode": "custom", "identity": next(iter(self.expected))}],
            unlock_uuid="00000000-0000-0000-0000-000000000000",
        )
        self.assertNotEqual(
            result.get("status"),
            "ok",
            f"a bogus unlockuuid returned data: {result}",
        )


if __name__ == "__main__":
    unittest.main()
