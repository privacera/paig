import privacera_shield.client

privacera_shield.client.setup(frameworks=["None"])
with privacera_shield.client.create_shield_context(username="user1"):
    try:
        privacera_shield.client.dummy_access_denied()
    except privacera_shield.exception.AccessControlException as e:
        print(f"*** Access Denied, message: {e}")