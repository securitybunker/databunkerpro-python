import os
import random
from databunkerpro import DatabunkerproAPI

# Get credentials from environment
api_url = os.getenv("DATABUNKER_API_URL", "https://pro.databunker.org")
api_token = os.getenv("DATABUNKER_API_TOKEN", "")
tenant_name = os.getenv("DATABUNKER_TENANT_NAME", "")

def generate_random_user_data():
    """Generate random user data with 120 fields."""
    # Base fields that are always present
    base_fields = {
        "email": f"user{random.randint(1000, 999999)}@example.com",
        "name": f"User {random.randint(1000, 999999)}",
        "phone": f"+1{random.randint(1000000000, 9999999999)}",
    }
    
    # Additional fields to reach 120 fields
    additional_fields = {
        f"field_{i}": f"value_{random.randint(1000, 999999)}" for i in range(117)
    }
    
    return {**base_fields, **additional_fields}

def create_bulk_users(api, num_batches=100, users_per_batch=100):
    """Create multiple batches of users and save tokens to results file."""
    all_tokens = []
    
    for batch in range(num_batches):
        print(f"Processing batch {batch + 1}/{num_batches}")
        
        # Generate user data for this batch
        users_data = [
            {"profile": generate_random_user_data()}
            for _ in range(users_per_batch)
        ]
        
        # Create users in bulk
        result = api.create_users_bulk(users_data)
        
        if result.get("status") == "ok":
            # Extract 10 random tokens from this batch
            created_users = result.get("created", [])
            if created_users:
                batch_tokens = random.sample(
                    [user["token"] for user in created_users],
                    min(10, len(created_users))
                )
                all_tokens.extend(batch_tokens)
                
                # Save tokens to file after each batch, one token per line
                with open("user_tokens.txt", "w") as f:
                    f.write("\n".join(all_tokens))
                
                print(f"Successfully created {len(created_users)} users in batch {batch + 1}")
                print(f"Saved {len(batch_tokens)} tokens to user_tokens.txt")
        else:
            print(f"Error in batch {batch + 1}: {result.get('message', 'Unknown error')}")
    
    return all_tokens

def main():
    
    if not all([api_token, tenant_name]):
        print("Error: DATABUNKER_API_TOKEN and DATABUNKER_TENANT_NAME environment variables must be set")
        return
    
    # Initialize API client
    api = DatabunkerproAPI(api_url, api_token, tenant_name)
    
    # Create users in bulk
    tokens = create_bulk_users(api)
    print(f"\nTotal tokens saved: {len(tokens)}")

if __name__ == "__main__":
    main() 