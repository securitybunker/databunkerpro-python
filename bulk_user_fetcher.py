import os
import asyncio
import time
from datetime import datetime
from databunkerpro import DatabunkerproAPI

# Get credentials from environment
api_url = os.getenv("DATABUNKER_API_URL", "http://localhost")
api_token = os.getenv("DATABUNKER_API_TOKEN", "dcc33285-4bfd-6e3b-eeb8-05e879afa943")
tenant_name = os.getenv("DATABUNKER_TENANT_NAME", "")

# Statistics tracking
stats = {
    "total_fetched": 0,
    "start_time": None,
    "errors": 0
}

async def fetch_user(api, token):
    """Fetch a single user record using DatabunkerproAPI."""
    try:
        result = api.get_user(token)
        if result and result.get("status") == "ok":
            stats["total_fetched"] += 1
            return result
        else:
            stats["errors"] += 1
            print(f"Error fetching token {token}: {result.get('message', 'Unknown error')}")
            return None
    except Exception as e:
        stats["errors"] += 1
        print(f"Exception fetching token {token}: {str(e)}")
        return None

async def fetch_users_batch(api, tokens, batch_size=100):
    """Fetch users in parallel batches."""
    for i in range(0, len(tokens), batch_size):
        batch = tokens[i:i + batch_size]
        tasks = [fetch_user(api, token.strip()) for token in batch]
        await asyncio.gather(*tasks)
        
        # Print progress
        elapsed_time = time.time() - stats["start_time"]
        rate = stats["total_fetched"] / (elapsed_time / 60)  # records per minute
        print(f"\rFetched {stats['total_fetched']} records | "
              f"Rate: {rate:.2f} records/min | "
              f"Errors: {stats['errors']}", end="")

def print_final_stats():
    """Print final statistics."""
    elapsed_time = time.time() - stats["start_time"]
    rate = stats["total_fetched"] / (elapsed_time / 60)
    
    print("\n\nFinal Statistics:")
    print(f"Total records fetched: {stats['total_fetched']}")
    print(f"Total errors: {stats['errors']}")
    print(f"Total time: {elapsed_time:.2f} seconds")
    print(f"Average rate: {rate:.2f} records per minute")

async def main():
    if not all([api_token]):
        print("Error: DATABUNKER_API_TOKEN environment variable must be set")
        return

    # Initialize API client
    api = DatabunkerproAPI(api_url, api_token, tenant_name)

    # Read tokens from file
    try:
        with open("user_tokens.txt", "r") as f:
            tokens = f.readlines()
    except FileNotFoundError:
        print("Error: user_tokens.txt not found")
        return

    if not tokens:
        print("No tokens found in user_tokens.txt")
        return

    print(f"Found {len(tokens)} tokens to process")
    stats["start_time"] = time.time()
    
    # Process tokens in batches
    await fetch_users_batch(api, tokens)
    print_final_stats()

if __name__ == "__main__":
    asyncio.run(main()) 