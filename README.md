This is my proof-of-concept automation suite with AWS as the cloud provider.

For security and secrets (since I'm just one person and not a company) I decided to utilize Vault, creating a bootstrap
script in Python that helps set up the roles/environments. Ideally, it would be tied to an OIDC or LDAP of some type,
but for this example I just made a dict of users and stored it in AWS SSM ParameterStore. 

The `connect_creds.py` script is the client-side login script to fetch those leased credentials and to set which
environment you're working on, which is then picked up by Terragrunt (wrapper for Terraform) in its configuration to 
allow automatic .tfvar file selection as well as backend creation. 

As a slightly related component, I included a Packer configuration to upload customized images to the AWS account, which 
is referenced by the Terraform AMI child module.

Within Terraform, I also included a simplified solution to quickly deploy security groups, aiming to keep calls to it 
DRY and concise as possible. 

All in all this is a generic example solution suite and would be much better flushed out and implemented if the 
company/business requirements were provided. 