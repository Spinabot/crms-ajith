import hvac
import os
import logging
from typing import Dict, List, Optional, Any
from app.config import Config

logger = logging.getLogger(__name__)

class VaultService:
    """Service class for HashiCorp Vault operations (KV v1)"""

    def __init__(self):
        self.client = None
        self.vault_url = os.getenv('VAULT_URL', 'http://localhost:8200')
        self.vault_token = os.getenv('VAULT_TOKEN')
        self.vault_namespace = os.getenv('VAULT_NAMESPACE')
        self.secret_path = os.getenv('VAULT_SECRET_PATH', 'crm-integration')
        self.mount_point = os.getenv('VAULT_MOUNT_POINT', 'kv')
        self._initialize_client()

    def _initialize_client(self):
        try:
            self.client = hvac.Client(
                url=self.vault_url,
                token=self.vault_token,
                namespace=self.vault_namespace
            )
            if not self.client.is_authenticated():
                logger.error("Failed to authenticate with Vault")
                raise Exception("Vault authentication failed")
            logger.info("Successfully connected to Vault")
        except Exception as e:
            logger.error(f"Failed to initialize Vault client: {e}")
            raise Exception(f"Vault initialization failed: {str(e)}")

    def get_secret(self, secret_path: str) -> Dict[str, Any]:
        if not self.client:
            raise Exception("Vault client not initialized")
        try:
            response = self.client.secrets.kv.v1.read_secret(
                path=secret_path,
                mount_point=self.mount_point
            )
            if response and 'data' in response:
                return response['data']
            else:
                raise Exception("Invalid response format from Vault")
        except Exception as e:
            logger.error(f"Failed to get secret from {secret_path}: {e}")
            raise Exception(f"Failed to retrieve secret: {str(e)}")

    def get_all_crm_secrets(self) -> Dict[str, str]:
        if not self.client:
            raise Exception("Vault client not initialized")
        try:
            secrets = self.get_secret(self.secret_path)
            crm_secrets = {
                'BUILDER_PRIME_API_KEY': secrets.get('BUILDER_PRIME_API_KEY'),
                'HUBSPOT_API_TOKEN': secrets.get('HUBSPOT_API_TOKEN'),
                'JOBBER_CLIENT_ID': secrets.get('JOBBER_CLIENT_ID'),
                'JOBBER_CLIENT_SECRET': secrets.get('JOBBER_CLIENT_SECRET'),
                'JOBBER_API_URL': secrets.get('JOBBER_API_URL'),
                'JOBNIMBUS_API_KEY': secrets.get('JOBNIMBUS_API_KEY'),
                'ZOHO_CLIENT_ID': secrets.get('ZOHO_CLIENT_ID'),
                'ZOHO_CLIENT_SECRET': secrets.get('ZOHO_CLIENT_SECRET')
            }
            return {k: v for k, v in crm_secrets.items() if v is not None}
        except Exception as e:
            logger.error(f"Failed to get CRM secrets: {e}")
            raise Exception(f"Failed to retrieve CRM secrets: {str(e)}")

    def create_or_update_secret(self, secret_path: str, secret_data: Dict[str, Any]) -> bool:
        if not self.client:
            raise Exception("Vault client not initialized")
        try:
            response = self.client.secrets.kv.v1.create_or_update_secret(
                path=secret_path,
                secret=secret_data,
                mount_point=self.mount_point
            )
            # v1 does not return a version, just check for no exception
            logger.info(f"Successfully created/updated secret at {secret_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create/update secret at {secret_path}: {e}")
            raise Exception(f"Failed to create/update secret: {str(e)}")

    def delete_secret(self, secret_path: str) -> bool:
        if not self.client:
            raise Exception("Vault client not initialized")
        try:
            self.client.secrets.kv.v1.delete_secret(
                path=secret_path,
                mount_point=self.mount_point
            )
            logger.info(f"Successfully deleted secret at {secret_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete secret at {secret_path}: {e}")
            raise Exception(f"Failed to delete secret: {str(e)}")

    def list_secrets(self, path: str = "") -> List[str]:
        if not self.client:
            return []
        try:
            response = self.client.secrets.kv.v1.list_secrets(
                path=path,
                mount_point=self.mount_point
            )
            if response and 'data' in response and 'keys' in response['data']:
                return response['data']['keys']
            else:
                return []
        except Exception as e:
            logger.error(f"Failed to list secrets at {path}: {e}")
            return []

    def get_vault_status(self) -> Dict[str, Any]:
        if not self.client:
            return {
                'error': 'Vault client not initialized',
                'initialized': False,
                'sealed': True
            }
        try:
            health = self.client.sys.read_health_status()
            return {
                'initialized': health.get('initialized', False),
                'sealed': health.get('sealed', True),
                'standby': health.get('standby', False),
                'performance_standby': health.get('performance_standby', False),
                'replication_performance_mode': health.get('replication_performance_mode', ''),
                'replication_dr_mode': health.get('replication_dr_mode', ''),
                'server_time_utc': health.get('server_time_utc', 0),
                'version': health.get('version', ''),
                'cluster_name': health.get('cluster_name', ''),
                'cluster_id': health.get('cluster_id', '')
            }
        except Exception as e:
            logger.error(f"Failed to get Vault status: {e}")
            return {
                'error': str(e),
                'initialized': False,
                'sealed': True
            }

    def test_connection(self) -> Dict[str, Any]:
        if not self.client:
            return {
                'connected': False,
                'authenticated': False,
                'can_read_secrets': False,
                'error': 'Vault client not initialized',
                'vault_url': self.vault_url,
                'namespace': self.vault_namespace,
                'secret_path': self.secret_path
            }
        try:
            is_authenticated = self.client.is_authenticated()
            can_read = False
            try:
                self.get_secret(self.secret_path)
                can_read = True
            except:
                pass
            return {
                'connected': True,
                'authenticated': is_authenticated,
                'can_read_secrets': can_read,
                'vault_url': self.vault_url,
                'namespace': self.vault_namespace,
                'secret_path': self.secret_path
            }
        except Exception as e:
            return {
                'connected': False,
                'authenticated': False,
                'can_read_secrets': False,
                'error': str(e),
                'vault_url': self.vault_url,
                'namespace': self.vault_namespace,
                'secret_path': self.secret_path
            }