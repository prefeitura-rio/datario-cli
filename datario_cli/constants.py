"""
Constant values for edrio.
"""

from enum import Enum
from pathlib import Path


class Constants (Enum):
    """
    All constants for the edrio CLI tool.
    """
    DATARIO_VAULT_EXTERNAL_ADDRESS = "http://vault-datario.vault.svc.cluster.local:8200/"
    EDRIO_BASE_DIRECTORY = Path.home() / ".edrio"
    EDRIO_ENVIRONMENTS_FILE = EDRIO_BASE_DIRECTORY / "envs.json"
    EDRIO_ENVIRONMENTS_LIST = {
        "BASEDOSDADOS_CREDENTIALS_PROD_PATH":
            "Caminho absoluto para o arquivo de credenciais do ambiente prod da BD+",
        "BASEDOSDADOS_CREDENTIALS_STAGING_PATH":
            "Caminho absoluto para o arquivo de credenciais do ambiente staging da BD+",
        "GOOGLE_APPLICATION_CREDENTIALS": "Caminho absoluto para o arquivo de credenciais da GCP",
        "TF_VAR_bucket_name": "Nome do bucket da GCP para armazenamento do estado do Terraform",
        "TF_VAR_project_id": "ID do projeto da GCP",
        "VAULT_TOKEN": "Token de acesso ao Vault do Escritório Municipal de Dados",
    }
    EMOJIS = {
        "error": [
            "😱",
            "😵",
            "😡",
            "😭",
            "😰",
            "😢",
            "😞",
            "😟",
            "😫",
            "😩",
            ":no_entry:",
        ],
        "nerd": [
            ":nerd_face:",
        ],
        "success": [
            ":hundred_points:",
            ":thumbs_up:",
            ":clapping_hands:",
            ":raising_hands:",
            ":trophy:",
            ":check_mark_button:",
            ":rocket:",
        ],
        "technology": [
            ":desktop_computer:",
            ":laptop:",
            ":keyboard:",
            ":man_technologist:",
            ":woman_technologist:",
            "💽",
        ],
    }
    IAC_DIRECTORY = EDRIO_BASE_DIRECTORY / "iac-public"
    IAC_GIT_REPOSITORY = "https://git.apps.rio.gov.br/escritorio-dados/escritorio-dados/iac-temp.git/"
    IAC_PREFECT_BD_CONFIG_BASE_PATH = IAC_DIRECTORY / \
        "prefect-agent" / "basedosdados" / "config.toml"
    IAC_PREFECT_SECRETS_BASE_PATH = IAC_DIRECTORY / \
        "prefect-agent" / "manifests" / "secrets.yaml"
    IAC_PREFECT_SECRETS_PATH = IAC_DIRECTORY / "secrets.yaml"
    IAC_PREFECT_VALUES_BASE_PATH = IAC_DIRECTORY / "prefect-agent" / "values.yaml"
    IAC_PREFECT_VALUES_PATH = IAC_DIRECTORY / "values.yaml"
