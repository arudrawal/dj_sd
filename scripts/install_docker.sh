#!/bin/bash
# sudo yum install git
sudo yum update -y
# Amazon Linux 2
# sudo amazon-linux-extras install docker
# Amazon Linux 2023
sudo yum install -y docker
sudo service docker start
# this will be effective on new login
sudo usermod -a -G docker ec2-user
