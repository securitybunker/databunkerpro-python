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

```python
from databunkerpro import DatabunkerproAPI

# Initialize the client
api = DatabunkerproAPI(
    base_url="https://pro.databunker.org",
    x_bunker_token="your-api-token",
    x_bunker_tenant="your-tenant-name"
)

# Create a new user
user_data = {
    "email": "user@example.com",
    "name": "John Doe",
    "phone": "+1234567890"
}
result = api.create_user(user_data)
print(f"Created user with token: {result['token']}")

# Get user information
user = api.get_user("email", "user@example.com")
print(f"User profile: {user['profile']}")

# Update user information
update_data = {
    "name": "John Updated",
    "phone": "+0987654321"
}
api.update_user("email", "user@example.com", update_data)

# Create a token for sensitive data
token_result = api.create_token("creditcard", "4111111111111111")
print(f"Created token in base format (credit card): {token_result['tokenbase']}")
print(f"Created token in uuid format: {token_result['tokenuuid']}")
```

## Features

- User Management (create, read, update, delete)
- Credit Card Management
- Token Management
- System Statistics
- Type hints and comprehensive documentation
- Error handling and validation

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

For detailed API documentation, please visit the [DatabunkerPro API Documentation](https://databunker.org/databunker-pro-docs/introduction/).
