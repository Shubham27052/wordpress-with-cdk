# **Using AWS CDK to build infrastructure for Wordpress and NGINX Reverse Proxy**

The project uses Infrastructure as Code through AWS Cloud Development Kit to create the following architecture:

1. Wordpress to deploy a sample website
2. NGINX to serve the webpage and create a Reverse Proxy to protect it.



![cdk](https://user-images.githubusercontent.com/68993711/233850449-e246f25c-4b23-497f-a59e-d28ff3094478.png)



## CloudFromation Template Structure

The main.yaml file contains the entire template in YAML for the wordpress and nginx setup. 
It can be broken down into 3 main sections: 
- Parameters
- Resources
- Output

**Parameters**
1. *InstanceType* input taken to choose the type of instance such as t2.micro, t2.small etc.
2. *DBUser, DBPassword, DBName and DBRootPassword* for the MySQL database, which is required for the wordpress website to work.

**Resources**
- For a cleaner and more effecient template, Nested Stacks were used to create VPC, NACL and Subnet for the setup( nacl.json, subnet.json and vpc.json)
- Other resources created include: Security Groups, Elastic IP and EC2 Instance.

**Outputs**
- The stack outputs the url for the sample wordpress website by getting the public IP Adress of the instance using !GetAtt.


## Configuring EC2 Instance
NGINX and Wordpress need to be installed and configured for the architecture to work. This was done using the helper scripts (cfn-init) and user data of the instance.

**User Data**
User data was used to install python, aws-cfn-bootstrap and to setup cfn-init and cfn-signal

**Helper Script**
This helper script was used to install all the packages and configuring the entire wordpress and nginx setup. It consistf of an ec2_setup configSet with the following 5 configs:
1. *config_cfn*: for basic setup of cfn-hup and helper scripts.
2. *install_packages*: to install and setup wordpress, mysql and nginx. 
3. *config_wordpress*: to create a server on port 8080 to serve the wordpress index file.
4. *create_database*: to create and setup a database for the wordpress website.
5. *config_reverse_proxy*: to create proxy server usning NGINX listening on port 80 and directing the traffic to port 8080 where NGINX serves wordpress


I have also built the same infrastructure using Cloudformation. Check it out here: 
