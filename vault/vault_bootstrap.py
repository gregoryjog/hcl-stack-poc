#!/usr/bin/env python3

"""
A utility for bootstrapping Vault with AWS integration as well as adding dynamic functionality to the roles.
Sets up IAM roles, Vault authentication, and user configurations.

Author: Gregory
Created: 2024
License: MIT
Copyright (c) 2025 Gregory Gerulat
"""

import os
import boto3
import hvac
import json
import time
import getpass
import argparse

# TODO Add more error handling, move hardcoded values to a configuration file, maybe add type safety.


class VaultBootstrap:
    """
    A class to handle Vault bootstrapping with AWS integration.

    Attributes:
        aws_access_key (str): AWS access key
        aws_secret_key (str): AWS secret key
        aws_region (str): AWS region
        vault_token (str): Vault authentication token
        vault_url (str): URL of the Vault server
        account_id (str): AWS account ID
        environments (List[str]): List of supported environments
        role_arns (Dict[str, str]): Mapping of roles to their ARNs
    """
    def __init__(
            self,
            aws_access_key: str = None,
            aws_secret_key: str = None,
            aws_region: str = None,
            vault_token: str = None,
            vault_url: str = None
    ) -> None:
        """
        Initialize VaultBootstrap with AWS and Vault credentials.

        Args:
            aws_access_key: AWS access key
            aws_secret_key: AWS secret key
            aws_region: AWS region
            vault_token: Vault authentication token
            vault_url: Vault server URL
        """
        self.aws_access_key = aws_access_key if aws_access_key is not None else os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = aws_secret_key if aws_secret_key is not None else os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.aws_region = aws_region if aws_region is not None else os.environ.get('AWS_REGION', 'us-west-2')
        self.vault_token = vault_token if vault_token is not None else os.environ.get('VAULT_TOKEN')
        self.vault_url = vault_url if vault_url is not None else os.environ.get('VAULT_ADDR', 'http://127.0.0.1:8200')
        if not all([
            self.aws_access_key,
            self.aws_secret_key,
            self.vault_token
        ]):
            print("Error: Required parameters not set.")
            exit(1)
        self.iam = boto3.client(
            'iam',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.aws_region
        )
        self.sts = boto3.client(
            'sts',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.aws_region
        )
        self.ssm = boto3.client(
            'ssm',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.aws_region
        )
        self.account_id = self.sts.get_caller_identity()['Account']
        self.environments = ["dev", "qa", "stage", "prod"]
        self.vault_client = hvac.Client(url=self.vault_url, token=self.vault_token)
        self.role_arns = {}

    def role_config(self, roles: str | list[str]) -> None:
        """
        Configure IAM roles in AWS for Vault integration.

        Args:
            roles: Single role or list of roles to configure
        """
        if not isinstance(roles, list):
            roles = [roles]

        print("Step 1: Creating IAM role(s) in AWS...")

        try:
            with open('policies/sys/trust-policy.aws.json', 'r') as f:
                content = f.read()
                trust_policy = content.replace('account_id', self.account_id)

            for group in roles:
                role_name = f"vault-terraform-{group}-role-{int(time.time())}"
                role = self.iam.create_role(
                    RoleName=role_name,
                    AssumeRolePolicyDocument=trust_policy,
                    Description="Role for Vault to assume for Terraform operations"
                )

                role_arn = role['Role']['Arn']
                print(f"Created role: {role_arn}")

                self.role_arns[group] = role_arn

                with open(f"policies/sts/{group}-policy.aws.json", "r") as f:
                    policy_document = f.read()

                policy_name = f"{role_name}-policy"
                self.iam.put_role_policy(
                    RoleName=role_name,
                    PolicyName=policy_name,
                    PolicyDocument=policy_document
                )
                print(f"Attached policy {policy_name} to role")

        except Exception as e:
            print(f"Error creating IAM role: {e}")
            exit(1)

    def parameter_fetch(self, parameter_store_name: str) -> dict[str, any]:
        """
        Fetch and parse parameters from AWS Parameter Store.
        This is just my poor-man's OIDC substitute.
        I have the values stored in ParameterStore as a json format, 'users'>'name':['role']

        Args:
            parameter_store_name: Name of the parameter in Parameter Store

        Returns:
            Dict containing the parsed parameter value
        """
        identity_data = self.ssm.get_parameter(
            Name=parameter_store_name,
            WithDecryption=False
        )['Parameter']['Value']
        try:
            identity_data = json.loads(identity_data)
        except Exception as e:
            print(f"Error loading value from Parameter Store: {e}")
            exit(1)

        return identity_data

    def vault_config(self, environment: str) -> None:
        """
        Configure Vault with AWS secrets engine and roles.

        Args:
            environment: Target environment for configuration
        """
        print("\nStep 2: Configuring Vault...")
        try:
            environment = environment.lower()
            if environment not in self.environments:
                print("Error: Environment not supported.")
                exit(1)

            if 'aws/' not in self.vault_client.sys.list_mounted_secrets_engines()['data']:
                self.vault_client.sys.enable_secrets_engine(
                    backend_type='aws',
                    path=f'aws/{environment}'
                )
                print("Enabled AWS secrets engine")

            self.vault_client.secrets.aws.configure_root_iam_credentials(
                access_key=self.aws_access_key,
                secret_key=self.aws_secret_key,
                region=self.aws_region,
                iam_endpoint="https://iam.amazonaws.com",
                sts_endpoint="https://sts.amazonaws.com",
                mount_point=f"/aws/{environment}"
            )
            print("Configured AWS credentials in Vault")

            for role, role_arn in self.role_arns.items():
                self.vault_client.secrets.aws.create_or_update_role(
                    name=f'terraform-{role}-role',
                    credential_type='assumed_role',
                    role_arns=[role_arn],
                    default_sts_ttl='1h',
                    max_sts_ttl='4h',
                    mount_point=f"/aws/{environment}"
                )

                print(f"Created Vault role: 'terraform-{role}-role'")
        except Exception as e:
            print(f"Error configuring Vault: {e}")
            exit(1)

    def user_config(self,
                    username: str = None,
                    password: str = None,
                    role: str = None,
                    identity_source: str = "ParameterStore",
                    parameter_store_name: str = "/terraform/users/dev"
                    ) -> None:
        """
        Configure Vault users and their permissions.

        Args:
            username: Vault username
            password: User's password
            role: User's role
            identity_source: Source of identity information
            parameter_store_name: Parameter Store path for user data
        """
        try:

            if "userpass/" not in self.vault_client.sys.list_auth_methods()['data']:
                self.vault_client.sys.enable_auth_method(
                    method_type='userpass'
                )

            if identity_source == "ParameterStore":
                userpool = self.parameter_fetch(parameter_store_name)['users']
            else:
                userpool = {}  # Or some other source, LDAP, OIDC, etc.

            if not username:
                username = input("Enter a login username: \n")
            if not password:
                password = getpass.getpass("Enter a password: ")
                secondpass = getpass.getpass("Re-enter the password: ")
                while password != secondpass or not password or not secondpass:
                    print("Passwords do not match or are blank. Please try again")
                    password = getpass.getpass("Enter a password: ")
                    secondpass = getpass.getpass("Re-enter the password: ")

            if username not in list(userpool.keys()):
                print("Username not found in identity source. Please input a correct username.")
                exit(1)

            if role is None and userpool[username][0] in self.role_arns.keys():
                role = userpool[username][0]
            else:
                print("Missing or invalid user role.")
                exit(1)

            self.vault_client.sys.create_or_update_policy(
                name=f'terraform-{role}-policy',
                policy=open(f'policies/user/{role}-policy.vault.hcl', 'r').read()
            )

            self.vault_client.auth.userpass.create_or_update_user(
                username=username,
                password=password,
                policies=[f'terraform-{role}-policy'],
                token_ttl="1h",
                token_max_ttl="4h"
            )

            print(f"Created Vault Terraform User '{username}' successfully.")

        except Exception as e:
            print(f"Error setting up user: {e}")
            exit(1)


def main() -> None:
    """
    Main function to handle command line arguments and execute the bootstrap process.
    """
    parser = argparse.ArgumentParser(description='Vault Bootstrap Configuration')
    parser.add_argument('--aws-access-key', help='AWS Access Key', default=None)
    parser.add_argument('--aws-secret-key', help='AWS Secret Key', default=None)
    parser.add_argument('--aws-region', help='AWS Region', default=None)
    parser.add_argument('--vault-token', help='Vault Token', default=None)
    parser.add_argument('--identity-source', help='Identity Source', default=None)
    parser.add_argument('--user', help='Username', default=None)
    parser.add_argument('--vault-url', help='Vault URL', default=None)
    parser.add_argument('--environment', help='Environment', default=None)

    args = parser.parse_args()
    try:
        vault_bootstrap = VaultBootstrap(
            aws_access_key=args.aws_access_key,
            aws_secret_key=args.aws_secret_key,
            aws_region=args.aws_region,
            vault_token=args.vault_token,
            vault_url=args.vault_url,
        )
        vault_bootstrap.role_config(["admin", "poweruser", "user"])
        vault_bootstrap.vault_config(environment=args.environment)
        vault_bootstrap.user_config(
            username=args.user
            )
    except Exception as e:
        print(f"Error running bootstrap: {e}")
        exit(1)
    print("Vault server and AWS roles setup successfully.")


if __name__ == "__main__":
    main()



