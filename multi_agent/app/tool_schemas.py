function_schemas = [
    {
        "name": "increment_like",
        "description": "Increase the 'like' count of a specific post or comment and trigger a blockchain transaction to reward the author.",
        "parameters": {
            "type": "object",
            "properties": {
                "content_type": {
                    "type": "string",
                    "enum": ["post", "comment"],
                    "description": "The type of content to like (either 'post' or 'comment')."
                },
                "content_id": {
                    "type": "integer",
                    "description": "The unique identifier (ID) of the content to increment likes for."
                },
                "wallet_address": {
                    "type": "string",
                    "description": "The Ethereum wallet address of the user who is liking the content. Used to initiate the reward transaction."
                }
            },
            "required": ["content_type", "content_id", "wallet_address"]
        }
    },
    {
        "name": "write_post",
        "description": "Create a new post with the given content on behalf of the specified user's wallet address. Automatically generates a unique content hash for verification purposes.",
        "parameters": {
            "type": "object",
            "properties": {
                "wallet_address": {
                    "type": "string",
                    "description": "The Ethereum wallet address of the user creating the new post."
                },
                "content": {
                    "type": "string",
                    "description": "The content of the new post."
                }
            },
            "required": ["wallet_address", "content"]
        }
    },
    {
        "name": "write_comment",
        "description": "Add a new comment to an existing post. The comment is created by a specific user's wallet address and is linked directly to a post.",
        "parameters": {
            "type": "object",
            "properties": {
                "wallet_address": {
                    "type": "string",
                    "description": "The Ethereum wallet address of the user creating the comment."
                },
                "content": {
                    "type": "string",
                    "description": "The content of the comment."
                },
                "post_id": {
                    "type": "integer",
                    "description": "The unique identifier (ID) of the post to which this comment belongs."
                }
            },
            "required": ["wallet_address", "content", "post_id"]
        }
    },
    {
        "name": "connect_db",
        "description": "Connect to the database to retrieve all existing posts and comments for debugging and data verification purposes. This function does not require any arguments.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]
