from core.security.jwt import JWTHandler

if __name__ == "__main__":
    username = input("Enter username: ")
    expire_minutes = input("Enter expiry in minutes : ")
    payload= ({"username": username})
    token = JWTHandler.encode(payload, int(expire_minutes))
    print("Encoded Token:", token)
    decoded_token = JWTHandler.decode(token)
    print("Decoded Token:", decoded_token)
