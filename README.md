# Databunker Pro Python Client

A Python client library for interacting with the DatabunkerPro API. This library provides a simple and intuitive interface for managing user data, tokens, and other DatabunkerPro features.

## Installation

You can install the package using pip:

```bash
pip install databunkerpro
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/securitybunker/databunkerpro-python.git
```

## Quick Start

You need a Databunker Pro instance to talk to. Demo mode gives you one in a single command — no database, no configuration, everything held in memory:

```bash
docker run -p 3000:3000 -d --rm --name databunkerpro securitybunker/databunkerpro demo
```

Check that it came up:

```bash
docker logs databunkerpro
```

```
 Databunker Pro demo is ready
  Web UI:            http://localhost:3000/
  Root access token: DEMO
  Database:          in-memory, erased on restart
```

The root access token in demo mode is the fixed string `DEMO`. Save this as `quickstart.py`:

```python
import base64

from databunkerpro import DatabunkerproAPI

api = DatabunkerproAPI("http://localhost:3000", "DEMO")

# Create a user record. The vault encrypts the profile and returns a user token.
created = api.create_user({
    "email": "john@pythontest.com",
    "name": "John Doe",
    "phone": "+15551234567",
})
print("User token:", created["token"])

# Read the record back by any indexed field: token, login, email, phone, custom.
user = api.get_user("email", "john@pythontest.com")
print("Profile:", user["profile"])

# Store an encrypted file against that user, tagged by document type.
filedata = base64.b64encode(b"fake passport scan bytes").decode()
file = api.create_file(
    "email",
    "john@pythontest.com",
    "passport.jpg",
    filedata,
    {"tags": ["passport", "kyc"]},
)
print("File uuid:", file["fileuuid"], "| tags:", file["tags"])

# List the user's files, filtered by tag.
listing = api.list_user_files("email", "john@pythontest.com", "kyc")
print("Files tagged kyc:", [f["filename"] for f in listing["files"]])

# Fetch the file back. Content returns base64-encoded in filedata.
fetched = api.get_file("email", "john@pythontest.com", fileuuid=file["fileuuid"])
print("Decrypted:", base64.b64decode(fetched["filedata"]).decode())

# Delete user record.
api.delete_user("email", "john@pythontest.com")
print("User deleted")
```

```bash
python quickstart.py
```

```
User token: c6688d6a-a87e-d332-2086-31c69fef4564
Profile: {'email': 'john@pythontest.com', 'name': 'John Doe', 'phone': '+15551234567'}
File uuid: c8517c4c-14f9-2e9d-2413-610b982065e8 | tags: ['kyc', 'passport']
Files tagged kyc: ['passport.jpg']
Decrypted: fake passport scan bytes
User deleted
```

Tags are lowercased, de-duplicated and sorted on write, which is why they come back in a different order than they were sent.

When you are done, stop the instance. It was started with `--rm`, so the container and its in-memory database are discarded:

```bash
docker stop databunkerpro
```

> **Demo mode is for evaluation only.** The database is in memory, the wrapping key is a fixed public value, and the root token is the well-known string `DEMO`. Never point it at real personal data. For a real deployment see the [installation guide](https://docs.databunker.org/pro/installation/docker-compose).

### Connecting to your own instance

```python
from databunkerpro import DatabunkerproAPI

api = DatabunkerproAPI(
    base_url="https://your-databunker-instance.com",
    x_bunker_token="your-api-token",
    x_bunker_tenant="your-tenant-name",   # multi-tenant deployments only
)

# Update user information
api.update_user("email", "john@pythontest.com", {
    "name": "John Updated",
    "phone": "+0987654321",
})

# Tokenize sensitive data
token_result = api.create_token("creditcard", "4111111111111111")
print(f"Created token in base format (credit card): {token_result['tokenbase']}")
print(f"Created token in uuid format: {token_result['tokenuuid']}")
```

### File storage

Files are attached to a user and can carry tags for later lookup:

```python
# Replace the complete tag set on a file. This overwrites, it does not merge.
api.replace_file_tags("email", "john@pythontest.com", file["fileuuid"], ["archived"])

api.delete_file("email", "john@pythontest.com", file["fileuuid"])
```

Files can also be listed by tag across every user in the tenant, which needs a
bulk-unlock uuid first:

```python
unlock = api.bulk_list_unlock()
tagged = api.bulk_list_files_by_tag(unlock["unlockuuid"], "archived", 0, 100)
```

## Features

- User Management
- App Data Management
- File Storage
- Tokenization
- Legal Basis & Agreement Management
- Processing Activity Management
- Group Management
- Role & Policy Management
- Session Management
- Shared Records
- Bulk Operations
- Audit Management
- Tenant Management
- Authentication & Access Tokens
- System Operations

Python-specific:

- Type hints and comprehensive documentation
- Error handling and validation
- Continuous security scanning (Semgrep SAST, pinned CI actions)

## Development

To set up the development environment:

1. Clone the repository:
```bash
git clone https://github.com/securitybunker/databunkerpro-python.git
cd databunkerpro-python
```

2. Install development dependencies:
```bash
pip install -e ".[dev]"
```

3. Run tests:
```bash
pytest
```

## Security

This library is scanned on every push and pull request, with a weekly scheduled sweep to catch drift:

- **SAST (Semgrep):** static analysis using the `p/python`, `p/secrets`, `p/security-audit`, and `p/owasp-top-ten` rulesets. A finding fails the check, and results are published to the repository's **Code Scanning** tab. See [`.github/workflows/semgrep.yml`](.github/workflows/semgrep.yml).
- **Supply-chain hardening:** every GitHub Action is pinned to a full commit SHA, so a mutable tag (`@v4`) cannot be silently repointed to malicious code.

Reproduce the SAST scan locally:

```bash
pip install semgrep
semgrep scan \
    --config p/python \
    --config p/secrets \
    --config p/security-audit \
    --config p/owasp-top-ten
```

To report a security vulnerability, please email hello@databunker.org rather than opening a public issue.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/securitybunker/databunkerpro-python/issues) on GitHub.

## API Documentation

For detailed API documentation, please visit the [DatabunkerPro API Documentation](https://docs.databunker.org/pro/get-started/overview).
