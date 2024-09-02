import privacera_shield.client

privacera_shield.client.setup(frameworks=["None"])
try:
    privacera_shield.client.set_current_user(username="user1")
    privacera_shield.client.dummy_access_denied()
    privacera_shield.client.clear()
except privacera_shield.exception.AccessControlException as e:
    print(f"*** Access Denied, message: {e}")