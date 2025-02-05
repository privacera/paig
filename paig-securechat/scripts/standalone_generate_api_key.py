import base64
import secrets


def generate_api_key(username: str):
    token = secrets.token_hex(32)  # 64-character secure token
    api_key = f"{username}:{token}"  # Embed username in key
    encoded_key = base64.urlsafe_b64encode(api_key.encode()).decode()  # Encode to Base64
    return encoded_key, token


if __name__ == "__main__":
    username = "sally"
    api_key, token = generate_api_key(username)
    print("Generated API Key:", api_key)
    print("Generated Token:", token)