from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    CfnParameter as parameter,
    aws_ec2 as ec2,
    CfnResource as resource,
    Fn as function,
    
)

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        #------------------PARAMETERS----------------------
        instance_type=parameter(self,'INSTANCE_TYPE',
                                 default='t2.micro', type='String',allowed_values=['t2.micro', 't2.small', 't2.medium', 't2.large'])
        
        DBName=parameter(self,'DBName',default='exampledb',
                         type='String',min_length=1,max_length=64, allowed_pattern="[a-zA-Z][a-zA-Z0-9]*")
        
        DBUser=parameter(self,'DBUser',default='exampleuser',
                         type='String',min_length=1,max_length=16, allowed_pattern="[a-zA-Z][a-zA-Z0-9]*")
        
        DBPassword=parameter(self,'DBPassword',
                             default='examplepw',type='String',min_length=8,max_length=41, allowed_pattern="[a-zA-Z0-9]*")

        DBRootPassword=parameter(self,'DBRootPassword',
                                 default='examplerpw',type='String',min_length=8,max_length=41, allowed_pattern="[a-zA-Z0-9]*")
        
        #---------VPC and IGW-------------------
        vpc=ec2.CfnVPC(self,'VPC',cidr_block="10.0.0.0/16")
        igw=ec2.CfnInternetGateway(self,'IGW')
        gateway_attachment=ec2.CfnVPCGatewayAttachment(self,'GATEWAY_ATTACHMENT',vpc_id=vpc.ref,internet_gateway_id=igw.ref)

        #---------NACL-------------------------
        nacl=ec2.CfnNetworkAcl(self,'NACL',vpc_id=vpc.ref)
        nacl_entry_inboundhttp=ec2.CfnNetworkAclEntry(self,'INBOUND_HTTP',
                                                    network_acl_id=nacl.ref,
                                                    rule_number=100,
                                                    protocol=6,
                                                    rule_action='allow',
                                                    egress=False,
                                                    cidr_block="0.0.0.0/0", 
                                                    port_range=ec2.CfnNetworkAclEntry.PortRangeProperty(from_=80,to=80))
        
        nacl_entry_inboundssh=ec2.CfnNetworkAclEntry(self,'INBOUND_SSH',
                                                    network_acl_id=nacl.ref,
                                                    rule_number=101,
                                                    protocol=6,
                                                    rule_action='allow',
                                                    egress=False,
                                                    cidr_block="0.0.0.0/0", 
                                                    port_range=ec2.CfnNetworkAclEntry.PortRangeProperty(from_=22,to=22))
        
        nacl_entry_inboundresponse=ec2.CfnNetworkAclEntry(self,'INBOUND_RESPONSE',
                                                    network_acl_id=nacl.ref,
                                                    rule_number=102,
                                                    protocol=6,
                                                    rule_action='allow',
                                                    egress=False,
                                                    cidr_block="0.0.0.0/0", 
                                                    port_range=ec2.CfnNetworkAclEntry.PortRangeProperty(from_=1024,to=65535))
        
        nacl_entry_outboundhttp=ec2.CfnNetworkAclEntry(self,'OUTBOUND_HTTP',
                                                    network_acl_id=nacl.ref,
                                                    rule_number=100,
                                                    protocol=6,
                                                    rule_action='allow',
                                                    egress=True,
                                                    cidr_block="0.0.0.0/0", 
                                                    port_range=ec2.CfnNetworkAclEntry.PortRangeProperty(from_=80,to=80))
        
        nacl_entry_outboundhttps=ec2.CfnNetworkAclEntry(self,'OUTBOUND_HTTPS',
                                                    network_acl_id=nacl.ref,
                                                    rule_number=101,
                                                    protocol=6,
                                                    rule_action='allow',
                                                    egress=True,
                                                    cidr_block="0.0.0.0/0", 
                                                    port_range=ec2.CfnNetworkAclEntry.PortRangeProperty(from_=443,to=443))
        
        nacl_entry_outboundresponse=ec2.CfnNetworkAclEntry(self,'OUTBOUND_RESPONSE',
                                                    network_acl_id=nacl.ref,
                                                    rule_number=102,
                                                    protocol=6,
                                                    rule_action='allow',
                                                    egress=True,
                                                    cidr_block="0.0.0.0/0", 
                                                    port_range=ec2.CfnNetworkAclEntry.PortRangeProperty(from_=1024,to=65535))
        
        #--------------Subnet----------------------------------------------------
        subnet=ec2.CfnSubnet(self,'SUBNET', cidr_block="10.0.0.0/24",vpc_id=vpc.ref )

        route_table=ec2.CfnRouteTable(self,"ROUTE_TABLE",vpc_id=vpc.ref)

        route=ec2.CfnRoute(self,"ROUTE",route_table_id=route_table.ref,gateway_id=igw.ref,destination_cidr_block="0.0.0.0/0")

        route_table_association=ec2.CfnSubnetRouteTableAssociation(self,'ROUTE_TABLE_ASSOCIATION',route_table_id=route_table.ref,subnet_id=subnet.ref)

        #---------------Subnet and NACL Association----------------------
        subnet_nacl_association=ec2.CfnSubnetNetworkAclAssociation(self,"SUBNET_NACL_ASSOCIATION",network_acl_id=nacl.ref,subnet_id=subnet.ref)

        subnet_nacl_association.add_depends_on(subnet)
        subnet_nacl_association.add_depends_on(nacl)

        #--------------Security Group----------------------------
        security_group=ec2.CfnSecurityGroup(self,'SECURITY_GROUP',vpc_id=vpc.ref, group_description="security group for the web instance",
                                            
                                            security_group_ingress=[ec2.CfnSecurityGroup.IngressProperty(ip_protocol="tcp",cidr_ip="0.0.0.0/0", from_port=22, to_port=22), ec2.CfnSecurityGroup.IngressProperty(ip_protocol="tcp",cidr_ip="0.0.0.0/0", from_port=80, to_port=80) ]
                                            )
        security_group.add_dependency(vpc)

       # security_group_ingress_1=ec2.CfnSecurityGroup.IngressProperty(ip_protocol="tcp",cidr_ip="0.0.0.0/0", from_port=22, to_port=22,source_security_group_name="security_group")

      #  security_group_ingress_2=ec2.CfnSecurityGroup.IngressProperty(ip_protocol="tcp",cidr_ip="0.0.0.0/0", from_port=80, to_port=80,source_security_group_name="security_group")


        #----------WebServer Instance and EIP----------

        #EIP-----
        eip=ec2.CfnEIP(self,'IPAddress')

        #Read file content for UserData-----
        with open(r'cdk\user_data\user_data.sh' , mode = 'r') as file:
            userData=file.read()


        #-----------------Metadata-----------------
        with open(r'cdk\metadata\config_wordpress.txt' , mode = 'r') as file:
            wordpress_config_content=file.read()

        with open(r'cdk\metadata\setup_mysql.txt' , mode = 'r') as file:
            setup_mysql_content=file.read()

        with open(r'cdk\metadata\create_wp_config.txt' , mode = 'r') as file:
            create_wp_config_content=file.read()

        with open(r'cdk\metadata\reverse_proxy.txt' , mode = 'r') as file:
            reverse_proxy_content=file.read()

        #Defining the WeServer-----
        webserver_instance=ec2.CfnInstance(self,"WEBSERVERINSTANCE",
                                           image_id="ami-00eeedc4036573771",
                                            instance_type=instance_type.value_as_string,
                                            network_interfaces=[
                                                ec2.CfnInstance.NetworkInterfaceProperty(associate_public_ip_address=True, group_set=[security_group.ref],device_index="0",delete_on_termination=True,subnet_id=subnet.ref)
                                            ], user_data= function.base64(function.sub(userData)))

        webserver_instance.add_metadata('AWS::CloudFormation::Init',
        {
                    "configSets":{
                        "ec2_setup": ["config_cfn", "install_packages","config_wordpress","create_database","config_reverse_proxy"]
                        },
                    "config_cfn": {
                        "files": {
                            "/etc/cfn/cfn-hup.conf": {
                                "content": function.sub("[main]\n stack=${AWS::StackId}\n region=${AWS::Region}"),
                                "mode": "000400",
                                "owner": "root",
                                "group": "root"
                            },
                            "/etc/cfn/hooks.d/cfn-auto-reloader.conf": {
                                "content": function.sub("[cfn-auto-reloader-hook]\n triggers=post.update\n path=Resources.WebServerInstance.Metadata.AWS::CloudFormation::Init\n action=/opt/aws/bin/cfn-init -v --stack !Ref 'AWS::StackName' --resource WebServerInstance --configsets InstallAndRun --region !Ref 'AWS::Region'\n runas=root"),
                                "mode": "000400",
                                "owner": "root",
                                "group": "root"
                            },
                            "/lib/systemd/system/cfn-hup.service": {
                                "content": function.sub("[Unit]\n Description=cfn-hup daemon\n\n [Service]\n Type=simple\n ExecStart=/usr/local/bin/cfn-hup\n Restart=always\n\n [Install]\n WantedBy=multi-user.target")
                            }
                        },
                        "commands": {
                            "01enable_cfn_hup": {
                                "command": "systemctl enable cfn-hup.service"
                            },
                            "02start_cfn_hup": {
                                "command": "systemctl start cfn-hup.service"
                            }
                        }
                    },
                    "install_packages": {
                        "commands": {
                            "01_install_nginx_and_phpsql": {
                                "command": "sudo apt install nginx mariadb-server php-fpm php-mysql -y"
                            },
                            "02a_mkdir_var_www": {
                                "command": "mkdir -p /var/www/"
                            },
                            "02b_download_wordpress": {
                                "cwd": "/var/www/",
                                "command": "wget https://wordpress.org/latest.tar.gz"
                            },
                            "03_unzip_wordpress_file": {
                                "cwd": "/var/www/",
                                "command": "sudo tar -xzvf latest.tar.gz"
                            },
                            "04_remove_tarfile": {
                                "cwd": "/var/www/",
                                "command": "rm latest.tar.gz"
                            },
                            "05_chown_wordpress": {
                                "cwd": "/var/www/",
                                "command": "sudo chown -R www-data:www-data wordpress/"
                            },
                            "06_chmod_wordpress": {
                                "cwd": "/var/www/",
                                "command": "sudo chmod 755 wordpress/*"
                            },
                            "07_mkdir_nginx_sites_available": {
                                "command": "mkdir -p /etc/nginx/sites-available"
                            },
                            "08_mkdir_nginx_sites_enabled": {
                                "command": "mkdir -p /etc/nginx/sites-enabled"
                            },
                            "09_makefile_nginx_sites_available_wordpress": {
                                "command": "touch /etc/nginx/sites-available/wordpress.conf"
                            }
                        }
                    },
                    "config_wordpress": {
                        "files": {
                            "/etc/nginx/sites-available/wordpress.conf": {
                                "content": function.sub(wordpress_config_content)
                            }
                        },
                        "commands": {
                            "00_soft_link": {
                                "command": "sudo ln -s /etc/nginx/sites-available/wordpress.conf /etc/nginx/sites-enabled/"
                            },
                            "03_create_setup_mysql": {
                                "command": "touch /tmp/setup.mysql"
                            },
                            "04_create_wp_config": {
                                "command": "touch /tmp/create-wp-config"
                            },
                            "make_setup_mysql_executable": {
                                "command": "chmod 777 /tmp/setup.mysql"
                            },
                            "make_create_wp_config_executable": {
                                "command": "chmod 755 /tmp/create-wp-config"
                            }
                        }
                    },
                    "create_database": {
                        "files": {
                            "/tmp/setup.mysql": {
                                "content": function.sub(setup_mysql_content)
                            },
                            "/tmp/create-wp-config": {
                                "content": function.sub(create_wp_config_content)
                            }
                        },
                        "commands": {
                            "00_set_root_password": {
                                "command": {
                                    "Fn::Sub": "sudo mysqladmin -u root password ${DBRootPassword}\n"
                                }
                            },
                            "01_create_database": {
                                "command": {
                                    "Fn::Sub": "sudo mysql -u root --password=${DBRootPassword} < /tmp/setup.mysql\n"
                                }
                            },
                            "02_configure_wordpress": {
                                "command": "sudo /tmp/create-wp-config",
                                "cwd": "/var/www/wordpress"
                            }
                        }
                    },
                    "config_reverse_proxy": {
                        "files": {
                            "/etc/nginx/nginx.conf": {
                                "content":function.sub(reverse_proxy_content)
                            }
                        },
                        "commands": {
                            "00_remove_default": {
                                "command": "sudo rm /etc/nginx/sites-enabled/default"
                            },
                            "01_start_nginx": {
                                "command": "systemctl restart nginx"
                            },
                            "02_start_mariadb": {
                                "command": "systemctl restart mariadb"
                            }
                        }
                    }
            }
        )
        webserver_instance.add_deletion_override('Metadata.aws:cdk:path')
        
        #EIP and WebServer Association-----
        ec2_eip_association=ec2.CfnEIPAssociation(self,"EC2_EIP_ASSOCIATION", eip=eip.ref, instance_id=webserver_instance.ref)
