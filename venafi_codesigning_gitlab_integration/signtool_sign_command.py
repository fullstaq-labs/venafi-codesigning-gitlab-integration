from dataclasses import dataclass
from typing import List
from venafi_codesigning_gitlab_integration import utils
import envparse
import tempfile
import logging
import sys

config_schema = dict(
    TPP_AUTH_URL=str,
    TPP_HSM_URL=str,
    TPP_USERNAME=str,
    TPP_PASSWORD=str,

    INPUT=str,
    CERTIFICATE_SUBJECT_NAME=dict(cast=str, default=None),
    CERTIFICATE_SHA1=dict(cast=str, default=None),
    TIMESTAMPING_SERVERS=dict(cast=list, subcast=str, default=()),

    SIGNATURE_DIGEST_ALGOS=dict(cast=list, subcast=str, default=('sha256')),
    APPEND_SIGNATURES=dict(cast=bool, default=False),
    EXTRA_CLI_ARGS=dict(cast=list, subcast=str, default=()),
    SIGNTOOL_PATH=dict(cast=str, default=None),
    VENAFI_CLIENT_TOOLS_DIR=dict(cast=str, default=None),
    MACHINE_CONFIGURATION=dict(cast=bool, default=False),
)


@dataclass
class SigntoolSignConfig:
    tpp_auth_url: str
    tpp_hsm_url: str
    tpp_username: str
    tpp_password: str

    input: str
    certificate_subject_name: str = None
    certificate_subject_sha1: str = None
    timestamping_servers: List[str] = ()

    signature_digest_algos: List[str] = ('sha256',)
    append_signatures: bool = False
    extra_cli_args: List[str] = ()
    signtool_path: str = None
    venafi_client_tools_dir: str
    machine_configuration: bool = False

    @classmethod
    def from_env(cls):
        return cls(utils.create_dataclass_inputs_from_env(config_schema))


class SigntoolSignCommand:
    def __init__(self, logger, config: SigntoolSignConfig):
        if config.certificate_subject_name is not None and \
           config.certificate_subject_sha1 is not None:
            raise envparse.ConfigurationError(
                "Only one of 'CERTIFICATE_SUBJECT_NAME' or "
                "'CERTIFICATE_SHA1' may be set, but not both")

        self.logger = logger
        self.config = config

    def run(self):
        self._create_temp_dir()
        try:
            pass
        finally:
            self._delete_temp_dir()

    def _create_temp_dir(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def _delete_temp_dir(self):
        if hasattr(self, 'temp_dir'):
            self.temp_dir.cleanup()


def main():
    try:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')
        config = SigntoolSignConfig.from_env()
        command = SigntoolSignCommand(logging.getLogger(), config)
    except envparse.ConfigurationError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    try:
        command.run()
    except utils.AbortException:
        sys.exit(1)


if __name__ == '__main__':
    main()