from werkzeug.security import generate_password_hash


def create_hash_password(password: str) -> str:
    return generate_password_hash(password)


if __name__ == "__main__":
    password = input("Enter password: ")
    hash_password = create_hash_password(password)
    print(f"Hashed password: {hash_password}")
