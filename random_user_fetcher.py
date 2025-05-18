import os
import random
import time

from databunkerpro import DatabunkerproAPI

# Get credentials from environment
api_url = os.getenv("DATABUNKER_API_URL", "http://localhost")
api_token = os.getenv("DATABUNKER_API_TOKEN", "dcc33285-4bfd-6e3b-eeb8-05e879afa943")
tenant_name = os.getenv("DATABUNKER_TENANT_NAME", "")


def read_tokens_from_file(filename="user_tokens.txt"):
    """Read tokens from file and return as a list."""
    try:
        with open(filename, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {filename} not found")
        return []


def fetch_random_user(api, tokens):
    """Fetch a random user record from the list of tokens."""
    if not tokens:
        print("No tokens available")
        return None

    token = random.choice(tokens)
    try:
        result = api.get_user(token)
        if result and result.get("status") == "ok":
            return result
        else:
            print(
                f"Error fetching token {token}: {result.get('message', 'Unknown error')}"
            )
            return None
    except Exception as e:
        print(f"Exception fetching token {token}: {str(e)}")
        return None


def main():
    if not all([api_token]):
        print("Error: DATABUNKER_API_TOKEN environment variable must be set")
        return

    # Initialize API client
    api = DatabunkerproAPI(api_url, api_token, tenant_name)

    # Read tokens from file
    tokens = read_tokens_from_file()
    if not tokens:
        return

    print(f"Found {len(tokens)} tokens")

    # Fetch random users
    num_fetches = 5  # Number of random fetches to perform
    print(f"\nFetching {num_fetches} random users:")

    for i in range(num_fetches):
        print(f"\nFetch {i + 1}/{num_fetches}:")
        user = fetch_random_user(api, tokens)
        if user:
            print(f"Successfully fetched user with token: {user.get('token', 'N/A')}")
            print(f"User data: {user.get('profile', {})}")
        time.sleep(1)  # Small delay between requests


if __name__ == "__main__":
    main()
