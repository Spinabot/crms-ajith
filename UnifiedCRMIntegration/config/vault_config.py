import hvac
import sys


class VaultClient:
    def __init__(self, addr: str, token: str):
        self.addr = addr
        self.token = token
        self.client = hvac.Client(url=self.addr, token=self.token)

        if not self.client.is_authenticated():
            print("❌ Failed to authenticate with Vault")
            sys.exit(1)

    def read_secret(self, path: str) -> dict:
        """
        Reads a secret from Vault at the given path using KV v1.
        """
        path_parts = path.strip("/").split("/", 1)
        mount_point = path_parts[0]
        relative_path = path_parts[1] if len(path_parts) > 1 else ""

        secret = self.client.secrets.kv.v1.read_secret(
            path=relative_path,
            mount_point=mount_point
        )
        return secret["data"]

def get_secrets(vault_addr, vault_token, secret_path):
    vault = VaultClient(vault_addr, vault_token)
    return vault.read_secret(secret_path)