"""
Per-field tokenization and per-field shared identities.

Written for a customer who wants to tokenize *individual* fields rather than whole
profiles. Two flows, each exercised twice — once with single requests, once with the
bulk endpoints:

1. Shared identities — a 10-field profile is stored once, then each field is exposed
   through its own `SharedRecordCreate` UUID with its own expiration. The UUID is then
   redeemed with **no** `X-Bunker-Token` at all, which is the point of the feature: the
   partner holding the UUID never receives a vault credential.

2. Format-preserving tokenization — every field value is stringified and pushed through
   `TokenCreate` / `TokenCreateBulk` with `unique` set, so repeated values collapse onto
   one token.

Runs against https://pro.databunker.org with a throwaway sandbox tenant unless
DATABUNKER_API_URL / DATABUNKER_API_TOKEN / DATABUNKER_TENANT_NAME are set.
"""

import os
import random
import time
import unittest

import requests

from databunkerpro import DatabunkerproAPI


def make_profile(seed: int) -> dict:
    """A 10-field profile — the customer's record shape."""
    return {
        "email": f"jane{seed}@example.com",
        "phone": f"+1206555{seed % 10000:04d}",
        "login": f"jane{seed}",
        "custom": f"cust-{seed}",
        "first": "Jane",
        "last": f"Doe{seed}",
        "address": "1 Market Street, San Francisco, CA",
        "dob": "1985-04-12",
        "creditcard": "4532015112830366",
        "ssn": f"123-45-{seed % 10000:04d}",
    }


def is_luhn_valid(number: str) -> bool:
    """Luhn checksum — a format-preserving card token must still pass it."""
    digits = [int(c) for c in number][::-1]
    total = 0
    for i, digit in enumerate(digits):
        if i % 2:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


class SandboxTestCase(unittest.TestCase):
    """Shared sandbox bootstrap, matching the other test modules."""

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
        # A client with no X-Bunker-Token. The tenant header stays, because without it
        # the server cannot route the request and answers 404 for every UUID — that is
        # addressing, not authentication.
        cls.anonymous = DatabunkerproAPI(cls.api_url, "", cls.tenant_name)
        cls.seed = random.randint(100000, 999999)


class TestSharedIdentityPerField(SandboxTestCase):
    """One shared-record UUID per profile field, redeemed without a credential."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.profile = make_profile(cls.seed)

        created = cls.api.create_user(cls.profile)
        if created.get("status") != "ok":
            raise unittest.SkipTest(f"Setup UserCreate failed: {created}")
        cls.user_token = created["token"]

        # The user access token the customer hands to the end user's own session.
        cls.xtoken_result = cls.api.create_user_x_token(
            "token", cls.user_token, {"finaltime": "10m"}
        )

        # One shared identity per field, each with its own expiration and partner tag.
        cls.shares = {}
        for field in cls.profile:
            result = cls.api.create_shared_record(
                "token",
                cls.user_token,
                {
                    "fields": field,
                    "partner": f"partner-{field}",
                    "finaltime": "1d",
                },
            )
            cls.shares[field] = result

    def test_profile_has_ten_fields(self):
        self.assertEqual(len(self.profile), 10)

    def test_user_x_token_reads_own_record(self):
        """XTokenCreateForUser issues a working, scoped credential."""
        self.assertEqual(
            self.xtoken_result.get("status"), "ok", f"{self.xtoken_result}"
        )
        self.assertIn("xtoken", self.xtoken_result)

        user_api = DatabunkerproAPI(
            self.api_url, self.xtoken_result["xtoken"], self.tenant_name
        )
        result = user_api.get_user("token", self.user_token)
        self.assertEqual(result.get("status"), "ok", f"{result}")
        self.assertEqual(result.get("profile"), self.profile)

    def test_every_field_gets_its_own_share(self):
        """All 10 SharedRecordCreate calls succeed and return distinct UUIDs."""
        for field, result in self.shares.items():
            with self.subTest(field=field):
                self.assertEqual(
                    result.get("status"), "ok", f"share for {field}: {result}"
                )
                self.assertIn("recorduuid", result)

        uuids = [r["recorduuid"] for r in self.shares.values() if "recorduuid" in r]
        self.assertEqual(len(uuids), 10)
        self.assertEqual(len(set(uuids)), 10, "shared record UUIDs must be unique")

    def test_shared_identity_resolves_without_authentication(self):
        """The whole point: SharedRecordGet needs no X-Bunker-Token."""
        for field, share in self.shares.items():
            with self.subTest(field=field):
                self.assertIn("recorduuid", share, f"share for {field}: {share}")
                result = self.anonymous.get_shared_record(share["recorduuid"])
                self.assertEqual(
                    result.get("status"),
                    "ok",
                    f"unauthenticated read of {field} failed: {result}",
                )
                self.assertEqual(result.get("data"), {field: self.profile[field]})

    def test_share_exposes_only_its_own_field(self):
        """Field scoping is enforced — no other field leaks into the response."""
        for field, share in self.shares.items():
            with self.subTest(field=field):
                data = self.anonymous.get_shared_record(share["recorduuid"]).get(
                    "data", {}
                )
                self.assertEqual(list(data), [field], f"{field} share leaked: {data}")

    def test_unauthenticated_client_cannot_read_the_user_record(self):
        """The shared UUID is the only door — plain UserGet still requires a token."""
        result = self.anonymous.get_user("token", self.user_token)
        self.assertNotEqual(
            result.get("status"),
            "ok",
            f"unauthenticated UserGet returned data: {result}",
        )

    def test_unknown_uuid_is_rejected(self):
        result = self.anonymous.get_shared_record(
            "00000000-0000-0000-0000-000000000000"
        )
        self.assertNotEqual(result.get("status"), "ok", f"{result}")

    def test_share_stops_resolving_after_finaltime(self):
        """A short-lived share expires on its own, with no clean-up call."""
        share = self.api.create_shared_record(
            "token",
            self.user_token,
            {"fields": "first", "partner": "partner-expiry", "finaltime": "2s"},
        )
        self.assertEqual(share.get("status"), "ok", f"{share}")

        before = self.anonymous.get_shared_record(share["recorduuid"])
        self.assertEqual(
            before.get("status"), "ok", f"share was born expired: {before}"
        )

        time.sleep(4)

        after = self.anonymous.get_shared_record(share["recorduuid"])
        self.assertNotEqual(
            after.get("status"), "ok", f"expired share still resolves: {after}"
        )


class TestSharedIdentityPerFieldBulk(SandboxTestCase):
    """Same flow, with the users created through UserCreateBulk."""

    USER_COUNT = 3

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.profiles = [make_profile(cls.seed + i) for i in range(cls.USER_COUNT)]

        result = cls.api.create_users_bulk(
            [{"profile": p} for p in cls.profiles], {"finaltime": "1d"}
        )
        if result.get("status") != "ok":
            raise unittest.SkipTest(f"Setup UserCreateBulk failed: {result}")
        cls.bulk_result = result

        # email -> user token, so a share can be matched back to its source profile.
        cls.tokens = {
            item["profile"]["email"]: item["token"] for item in result["created"]
        }

        # (email, field) -> recorduuid
        cls.shares = {}
        for profile in cls.profiles:
            token = cls.tokens[profile["email"]]
            for field in profile:
                share = cls.api.create_shared_record(
                    "token",
                    token,
                    {
                        "fields": field,
                        "partner": f"partner-{field}",
                        "finaltime": "1d",
                    },
                )
                cls.shares[(profile["email"], field)] = share

    def test_bulk_create_returns_a_token_per_user(self):
        self.assertEqual(len(self.bulk_result["created"]), self.USER_COUNT)
        self.assertEqual(len(set(self.tokens.values())), self.USER_COUNT)

    def test_every_field_of_every_user_is_shared(self):
        self.assertEqual(len(self.shares), self.USER_COUNT * 10)
        uuids = [s["recorduuid"] for s in self.shares.values() if "recorduuid" in s]
        self.assertEqual(len(uuids), self.USER_COUNT * 10, "some shares failed")
        self.assertEqual(len(set(uuids)), len(uuids), "UUIDs collided across users")

    def test_each_share_resolves_unauthenticated_to_its_own_value(self):
        by_email = {p["email"]: p for p in self.profiles}
        for (email, field), share in self.shares.items():
            with self.subTest(email=email, field=field):
                self.assertIn("recorduuid", share, f"{share}")
                result = self.anonymous.get_shared_record(share["recorduuid"])
                self.assertEqual(result.get("status"), "ok", f"{result}")
                self.assertEqual(result.get("data"), {field: by_email[email][field]})


class TestFieldTokenization(SandboxTestCase):
    """TokenCreate per field, one request at a time, with `unique` set."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.profile = make_profile(cls.seed)
        cls.tokens = {
            field: cls.api.create_token(
                cls._token_type(field), str(value), {"unique": True}
            )
            for field, value in cls.profile.items()
        }

    @staticmethod
    def _token_type(field: str) -> str:
        """Every value is stringified and tokenized as a string.

        `text` is the API's string type, and `string` is an accepted alias for it.
        The test sends the canonical `text`, which every server version understands;
        test_string_is_an_alias_for_text covers the alias itself. Email, dates and
        timestamps all go through it rather than a specialised type. The credit card
        is the exception: it is the one field where format preservation applies.
        """
        return "creditcard" if field == "creditcard" else "text"

    def test_every_field_is_tokenized(self):
        for field, result in self.tokens.items():
            with self.subTest(field=field):
                self.assertEqual(result.get("status"), "ok", f"{field}: {result}")
                self.assertTrue(result.get("tokenuuid"), f"{field}: {result}")

    def test_tokens_are_distinct_across_fields(self):
        uuids = [r["tokenuuid"] for r in self.tokens.values() if r.get("tokenuuid")]
        self.assertEqual(len(uuids), 10)
        self.assertEqual(len(set(uuids)), 10, "two fields collapsed onto one token")

    def test_detokenization_round_trips_every_field(self):
        for field, value in self.profile.items():
            with self.subTest(field=field):
                result = self.api.get_token(self.tokens[field]["tokenuuid"])
                self.assertEqual(result.get("status"), "ok", f"{field}: {result}")
                self.assertEqual(result.get("record"), str(value))
                self.assertEqual(result.get("tokentype"), self._token_type(field))

    def test_credit_card_token_preserves_format(self):
        """`tokenbase` is same-length, all-digits and Luhn-valid — but not the card."""
        original = self.profile["creditcard"]
        tokenbase = self.tokens["creditcard"].get("tokenbase")

        self.assertTrue(tokenbase, f"no tokenbase: {self.tokens['creditcard']}")
        self.assertNotEqual(tokenbase, original, "token equals the original card")
        self.assertEqual(len(tokenbase), len(original))
        self.assertTrue(tokenbase.isdigit())
        self.assertTrue(is_luhn_valid(tokenbase), f"{tokenbase} fails the Luhn check")

    def test_format_preserving_token_also_detokenizes(self):
        """`tokenbase` works as a lookup key, not only `tokenuuid`."""
        result = self.api.get_token(self.tokens["creditcard"]["tokenbase"])
        self.assertEqual(result.get("status"), "ok", f"{result}")
        self.assertEqual(result.get("record"), self.profile["creditcard"])

    def test_only_the_card_returns_a_format_preserving_token(self):
        """The card gets a `tokenbase`; every string field gets a UUID token only."""
        for field, result in self.tokens.items():
            with self.subTest(field=field):
                if field == "creditcard":
                    self.assertTrue(result.get("tokenbase"), f"{field}: {result}")
                else:
                    self.assertFalse(result.get("tokenbase"), f"{field}: {result}")

    def test_unique_returns_the_same_token_for_the_same_value(self):
        """`unique` is the dedup flag — re-tokenizing a field is idempotent."""
        for field, value in self.profile.items():
            with self.subTest(field=field):
                again = self.api.create_token(
                    self._token_type(field), str(value), {"unique": True}
                )
                self.assertEqual(again.get("status"), "ok", f"{field}: {again}")
                self.assertEqual(
                    again["tokenuuid"],
                    self.tokens[field]["tokenuuid"],
                    f"{field}: unique=True issued a second token for one value",
                )

    def test_without_unique_each_call_mints_a_new_token(self):
        first = self.api.create_token("creditcard", self.profile["creditcard"])
        second = self.api.create_token("creditcard", self.profile["creditcard"])
        self.assertEqual(first.get("status"), "ok", f"{first}")
        self.assertEqual(second.get("status"), "ok", f"{second}")
        self.assertNotEqual(first["tokenuuid"], second["tokenuuid"])

    def test_string_is_an_alias_for_text(self):
        """ "string" and "text" are one type — same canonical name, same token.

        Skips on servers predating the alias, so the file works against a
        pro.databunker.org that has not picked up the change yet.
        """
        value = f"alias-probe-{self.seed}"
        canonical = self.api.create_token("text", value, {"unique": True})
        self.assertEqual(canonical.get("status"), "ok", f"{canonical}")

        alias = self.api.create_token("string", value, {"unique": True})
        if alias.get("message") == "Wrong token type":
            self.skipTest("server does not support the `string` alias yet")

        self.assertEqual(alias.get("status"), "ok", f"{alias}")
        self.assertEqual(
            alias["tokenuuid"],
            canonical["tokenuuid"],
            "`string` did not resolve to the same token as `text`",
        )
        stored = self.api.get_token(alias["tokenuuid"])
        self.assertEqual(stored.get("tokentype"), "text", f"{stored}")

    def test_unknown_token_types_are_rejected(self):
        """The accepted set is closed — these are not token types."""
        for name in ("phone", "date", "unixtime", "str"):
            with self.subTest(tokentype=name):
                result = self.api.create_token(name, f"probe-{self.seed}")
                self.assertNotEqual(result.get("status"), "ok", f"{name}: {result}")


class TestFieldTokenizationBulk(SandboxTestCase):
    """The same 10 fields through TokenCreateBulk, then bulk detokenization."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.profile = make_profile(cls.seed)
        cls.records = [
            {"tokentype": TestFieldTokenization._token_type(f), "record": str(v)}
            for f, v in cls.profile.items()
        ]
        cls.bulk = cls.api.create_tokens_bulk(cls.records, {"unique": True})

    def _rows(self, result):
        """created + duplicates — both carry a usable token for the record."""
        return (result.get("created") or []) + (result.get("duplicates") or [])

    def test_bulk_accepts_every_field(self):
        self.assertEqual(self.bulk.get("status"), "ok", f"{self.bulk}")
        self.assertEqual(
            self.bulk.get("summary", {}).get("errors", 0),
            0,
            f"TokenCreateBulk rejected records: {self.bulk.get('errors')}",
        )
        self.assertEqual(len(self._rows(self.bulk)), len(self.records))

    def test_bulk_round_trips_through_bulk_list_tokens(self):
        """BulkListTokens returns the original value for every token in the batch."""
        rows = self._rows(self.bulk)
        if not rows:
            self.skipTest("no tokens were created")

        unlock = self.api.bulk_list_unlock()
        self.assertEqual(unlock.get("status"), "ok", f"unlock failed: {unlock}")

        uuids = [row["tokenuuid"] for row in rows]
        result = self.api.bulk_list_tokens(unlock["unlockuuid"], uuids)
        self.assertEqual(result.get("status"), "ok", f"{result}")

        detokenized = {
            row["tokenuuid"]: row["record"] for row in result.get("rows", [])
        }
        self.assertEqual(
            len(detokenized), len(uuids), f"BulkListTokens returned {len(detokenized)}"
        )
        for row in rows:
            self.assertEqual(detokenized.get(row["tokenuuid"]), row["record"])

    def test_bulk_credit_card_token_preserves_format(self):
        card = self.profile["creditcard"]
        row = next((r for r in self._rows(self.bulk) if r["record"] == card), None)
        self.assertIsNotNone(row, f"credit card missing from batch: {self.bulk}")

        tokenbase = row.get("tokenbase")
        self.assertTrue(tokenbase, f"no tokenbase: {row}")
        self.assertNotEqual(tokenbase, card)
        self.assertEqual(len(tokenbase), len(card))
        self.assertTrue(is_luhn_valid(tokenbase), f"{tokenbase} fails the Luhn check")

    def test_bulk_unique_deduplicates_a_repeated_batch(self):
        """Re-submitting the batch with `unique` must reuse the existing tokens."""
        again = self.api.create_tokens_bulk(self.records, {"unique": True})
        self.assertEqual(again.get("status"), "ok", f"{again}")

        first = {r["record"]: r["tokenuuid"] for r in self._rows(self.bulk)}
        second = {r["record"]: r["tokenuuid"] for r in self._rows(again)}

        self.assertEqual(
            second,
            first,
            "unique=True minted new tokens for values that were already tokenized",
        )

    def test_single_create_finds_tokens_that_bulk_created(self):
        """The dedup *lookup* works for `text` — so the batch write path is at fault.

        Pairs with test_bulk_unique_deduplicates_a_repeated_batch: a single
        TokenCreate with unique=True returns the very token TokenCreateBulk stored,
        which means the value is indexed and findable. Only the bulk writer skips
        the uniqueness check.
        """
        rows = self._rows(self.bulk)
        if not rows:
            self.skipTest("no tokens were created")

        for row in rows:
            with self.subTest(record=row["record"]):
                single = self.api.create_token(
                    row["tokentype"], row["record"], {"unique": True}
                )
                self.assertEqual(single.get("status"), "ok", f"{single}")
                self.assertEqual(
                    single["tokenuuid"],
                    row["tokenuuid"],
                    "single TokenCreate did not find the bulk-created token",
                )

    def test_bulk_delete_removes_the_tokens(self):
        batch = [
            {"tokentype": "text", "record": f"disposable-{self.seed}-{i}"}
            for i in range(3)
        ]
        created = self.api.create_tokens_bulk(batch)
        self.assertEqual(created.get("status"), "ok", f"{created}")
        uuids = [row["tokenuuid"] for row in created.get("created") or []]
        self.assertEqual(len(uuids), 3, f"{created}")

        unlock = self.api.bulk_list_unlock()
        self.assertEqual(unlock.get("status"), "ok", f"{unlock}")
        deleted = self.api.bulk_delete_tokens(unlock["unlockuuid"], uuids)
        self.assertEqual(deleted.get("status"), "ok", f"{deleted}")

        gone = self.api.get_token(uuids[0])
        self.assertNotEqual(gone.get("status"), "ok", f"token survived delete: {gone}")


if __name__ == "__main__":
    unittest.main()
