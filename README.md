# **Using AWS CDK to build infrastructure for Wordpress and NGINX Reverse Proxy**

The project uses Infrastructure as Code through AWS Cloud Development Kit to create the following architecture:

1. Wordpress to deploy a sample website
2. NGINX to serve the webpage and create a Reverse Proxy to protect it.



![cdk](https://user-images.githubusercontent.com/68993711/233850449-e246f25c-4b23-497f-a59e-d28ff3094478.png)



## CDK Code Structure

The cdk_stack.py file contains the entire template in pyhton for the wordpress and nginx setup. 
It can be broken down into 2 main sections: 
- Parameters
- Resources

**Parameters**
1. *InstanceType* input taken to choose the type of instance such as t2.micro, t2.small etc.
2. *DBUser, DBPassword, DBName and DBRootPassword* for the MySQL database, which is required for the wordpress website to work.
3. The CfnParameter construct is used for the same and is imported as 'parameter'.

**Resources**
- Unlike CloudFormation, nested stacks have no application in cdk hence each resorce was created individually.
- All resources were created with ec2 constructs and appropritae parameters added to them.


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
<br />
For a cleaner code, the content for the files section of each config was added into a seperate file (checkout /wordpress-with-cdk/cdk/metadata) and was later read in cdk_stack.py using the open() and read() function.
<br />
<br />
<br />
<br />
<br />
<br />

I have also built the same infrastructure using Cloudformation. Check it out here: 
