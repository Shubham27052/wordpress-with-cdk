#!/bin/bash -xe
            sudo apt-get update -y
            sudo apt-get -y install python3-pip
            mkdir -p /opt/aws/
            sudo pip3 install https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-py3-latest.tar.gz
            sudo ln -s /usr/local/init/ubuntu/cfn-hup /etc/init.d/cfn-hup
            /usr/local/bin/cfn-init -v --stack ${AWS::StackName} --resource WEBSERVERINSTANCE --configsets ec2_setup --region ${AWS::Region}
            /usr/local/bin/cfn-signal -e $? --stack ${AWS::StackName} --resource WEBSERVERINSTANCE --region ${AWS::Region}