#!/bin/bash

yum install MariaDB-server -y
systemctl start mysqld
systemctl enable mysqld

mysql -e "grant all privileges on *.* to king@'localhost' identified by 'zhaozhilong'"

openstack service delete king
openstack service create --name king charging
openstack endpoint create --region RegionOne king admin  http://10.0.200.43:9000/v1
openstack endpoint create --region RegionOne king public http://10.0.200.43:9000/v1
openstack endpoint create --region RegionOne king internal http://10.0.200.43:9000/v1
