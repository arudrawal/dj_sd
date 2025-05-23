#!/bin/bash
# sudo yum install git
sudo yum update -y
sudo yum install curl
# Amazon Linux 2
# sudo amazon-linux-extras install docker
# Amazon Linux 2023
sudo yum install -y docker
sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo service docker start
# this will be effective on new login
sudo usermod -a -G docker ec2-user
