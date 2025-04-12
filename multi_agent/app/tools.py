from langchain_core.tools import tool

@tool
def write_post(wallet_address: str, content: str) -> dict:
    """Create a new post with the given content on behalf of the specified user's wallet address."""
    return {
        "name": "write_post",
        "description": "Create a new post with the given content on behalf of the specified user's wallet address. Automatically generates a unique content hash for verification purposes.",
        "parameters": {
            "wallet_address": wallet_address,
            "content": content
        }
    }

@tool
def write_comment(wallet_address: str, content: str, post_id: int) -> dict:
    """Add a new comment to an existing post."""
    return {
        "name": "write_comment",
        "description": "Add a new comment to an existing post. The comment is created by a specific user's wallet address and is linked directly to a post.",
        "parameters": {
            "wallet_address": wallet_address,
            "content": content,
            "post_id": post_id
        }
    }

@tool 
def increment_like(content_type: str, content_id: int, wallet_address: str) -> dict:
    """Increase the 'like' count of a specific post or comment and trigger a blockchain transaction to reward the author."""
    print(f"[!!LIKE TRIGGERED] {wallet_address} liked {content_type} #{content_id}")
    return {
        "name": "increment_like",
        "description": "Increase the 'like' count of a specific post or comment and trigger a blockchain transaction to reward the author.",
        "parameters": {
            "content_type": content_type,
            "content_id": content_id,
            "wallet_address": wallet_address
        }
    }

@tool
def connect_db() -> dict:
    """Connect to the database to retrieve all existing posts and comments for debugging and data verification purposes."""
    return {
        "name": "connect_db",
        "description": "Connect to the database to retrieve all existing posts and comments for debugging and data verification purposes.",
        "parameters": {}
    }
