import platform

v=platform.python_version_tuple()
python_version = f"cp{v[0]}{v[1]}"
python_system = platform.system().lower()
if python_system == "darwin":
    mac_ver = platform.mac_ver()
    mac_rel = mac_ver[0].split(".")
    python_system = f"macosx_{mac_rel[0]}_{mac_rel[1]}"
elif python_system == "windows":
    python_system = "win"
elif python_system == "linux":
    python_system = "linux"
else:
    python_system = "none"

arch=platform.machine().lower()

#print(f"python_version={python_version}, python_system={python_system}, arch={arch}")

print(f"{python_version}-{python_version}-{python_system}_{arch}")