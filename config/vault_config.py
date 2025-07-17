import hvac
import sys

# 👇 private by convention
_GLOBAL_SECRETS = {}


class VaultClient:
    def __init__(self, addr: str, token: str):
        self.addr = addr
        self.token = token
        self.client = hvac.Client(url=self.addr, token=self.token)

        if not self.client.is_authenticated():
            print("❌ Failed to authenticate with Vault")
            sys.exit(1)

    def read_secret(self, path: str) -> dict:
        path_parts = path.strip("/").split("/", 1)
        mount_point = path_parts[0]
        relative_path = path_parts[1] if len(path_parts) > 1 else ""

        secret = self.client.secrets.kv.v1.read_secret(
            path=relative_path,
            mount_point=mount_point
        )
        return secret["data"]


def load_secrets(vault_addr, vault_token, secret_path):
    global _GLOBAL_SECRETS
    vault = VaultClient(vault_addr, vault_token)
    _GLOBAL_SECRETS = vault.read_secret(secret_path)
    return vault.read_secret(secret_path) # you can remove the return statement if it is not requried for your app


def get_secret(key: str):
    if key not in _GLOBAL_SECRETS:
        raise KeyError(f"🔑 Key '{key}' not found in loaded secrets.")
    return _GLOBAL_SECRETS[key]