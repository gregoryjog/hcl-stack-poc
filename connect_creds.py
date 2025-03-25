#!/usr/bin/env python3

"""
A client-side utility for managing AWS credentials through Vault (setup using bootstrap) authentication.
The credentials are dynamically populated within the ~/.aws/credentials file for easier use with Terraform.

Author: Gregory Gerulat
Created: 2025
License: MIT
Copyright (c) 2025 Gregory Gerulat
"""

import argparse
import os
import configparser
import getpass
import hvac
from datetime import datetime, timedelta


class ConnectCreds:
    """
    A class to handle Vault authentication and AWS credential generation.

    Attributes:
        session_file_path (str): Path to the session file
        credentials_path (str): Path to AWS credentials file
        session_file_exists (bool): Flag indicating if session file exists
        username (str): Vault username
        password (str): Vault password
        vault_url (str): URL of the Vault server
        vault_client (hvac.Client): Vault client instance
        config (configparser.ConfigParser): Config parser for AWS credentials
        aws_region (str): AWS region
        environment (str): Environment name
        role (str): Role name
    """
    def __init__(self,
                 username: str = None,
                 password: str = None,
                 vault_url: str = None,
                 role: str = None,
                 environment: str = None,
                 ) -> None:
        """
            Initialize ConnectCreds with optional parameters.

            Args:
                username: Vault username
                password: Vault password
                vault_url: URL of the Vault server
                role: Role name
                environment: Environment name
         """
        self.session_file_path = f"{os.path.expanduser('~')}/.connectcreds.json"
        self.credentials_path = f"{os.path.expanduser('~')}/.aws/credentials"
        self.session_file_exists = False
        self.username = username if username is not None else input("Enter your username: \n")
        self.password = password if password is not None else getpass.getpass("Enter your password: \n")
        self.vault_url = vault_url if vault_url is not None else os.environ.get('VAULT_ADDR', 'http://127.0.0.1:8200')
        self.vault_client = hvac.Client(url=self.vault_url)
        self.config = configparser.ConfigParser()
        self.aws_region = "us-west-2"
        self.environment = environment
        self.role = role

    def login(self) -> bool:
        """
        Authenticate with Vault using userpass authentication.

        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            self.vault_client.auth.userpass.login(
                username=self.username,
                password=self.password
            )

            print("Login successful.")
            return True
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def generate_aws_credentials(self) -> bool:
        """
        Generate AWS credentials using Vault and save them to credentials file.

        Returns:
            bool: True if credentials were generated successfully, False otherwise
        """
        try:
            aws_creds = self.vault_client.read(f"aws/{self.environment}/sts/terraform-{self.role}-role")['data']
            self.config.read(self.credentials_path)
            if 'default' not in self.config:
                self.config['default'] = {}

            self.config['default'].update(
                {
                    'aws_access_key_id': aws_creds['access_key'],
                    'aws_secret_access_key': aws_creds['secret_key'],
                    'aws_session_token': aws_creds['security_token'],
                    'region': self.aws_region,
                    'generated_at': datetime.now().isoformat(),
                    'environment': self.environment
                }
            )

            os.makedirs(os.path.dirname(self.credentials_path), exist_ok=True)

            with open(self.credentials_path, 'w+') as file:
                self.config.write(file)

            print("AWS credentials successfully generated and updated.")
            return True

        except Exception as e:
            print(f"Failed to generate credentials: {str(e)}")
            return False


def main() -> None:
    """
    Main function to handle command line arguments and execute the credential generation process.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", help="Username")
    parser.add_argument("--password", help="Password")
    parser.add_argument("--vault_url", help="Vault URL")
    parser.add_argument("-r", "--role", help="Role")
    parser.add_argument("-e", "--environment", help="Environment")
    args = parser.parse_args()
    connectcreds = ConnectCreds(
        username=args.username,
        password=args.password,
        vault_url=args.vault_url,
        role=args.role,
        environment=args.environment
    )

    if connectcreds.login():
        connectcreds.generate_aws_credentials()
        print(f"Successfully connected to \"{args.environment.lower()}\".")
        print(f"Token will expire at {datetime.now() + timedelta(hours=1)}.")


if __name__ == "__main__":
    main()



