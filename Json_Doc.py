
class Json_doc():
    def __init__(self):
        pass

    def get_s3_xaccount(self,buk_name):
        dict_ret = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:ListBucket",
                        "s3:GetObject"
                    ],
                    "Resource": ['arn:aws:s3:::','arn:aws:s3:::']
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:ListBucket",
                        "s3:PutObject",
                        "s3:PutObjectAcl"
                    ],
                    "Resource": [
                        "arn:aws:s3:::lab.broadsoft",
                        "arn:aws:s3:::lab.broadsoft/*"
                    ]
                }
            ]
        }
        dict_ret['Statement'][0]['Resource'][0] = ('arn:aws:s3:::' + buk_name)
        dict_ret['Statement'][0]['Resource'][1] = ('arn:aws:s3:::' + buk_name + '/*')
        
        return dict_ret


    def get_cfn_template_r23(self,buk_name):
        '''
        Should be used for Centos7/RHEL7 and version R23 of Broadworks
        '''
        template = {
              "Resources": {
                "BSLaunchTemplate": {
                  "Type": "AWS::EC2::LaunchTemplate",
                  "Properties": {
                    "LaunchTemplateName": "BroadSoftLaunchTemplate1",
                    "LaunchTemplateData": {
                      "KeyName": "haystackaccess",
                      "ImageId": "ami-02e98f78",
                      "InstanceType": "t2.medium"
                    }
                  },
                  "Metadata": {
                    "AWS::CloudFormation::Init": {
                      "configSets": {
                        "ns": [
                          "base",
                          "network_server"
                        ],
                        "as": [
                          "base",
                          "application_server"
                        ],
                        "xsp": [
                          "base",
                          "xsp_server"
                        ],
                        "ps": [
                          "base",
                          "profile_server"
                        ]
                      },
                      "base": {
                        "packages": {
                          "yum": {
                            "sed": [],
                            "firewalld": [],
                            "bash.x86_64": [],
                            "bind-utils.x86_64": [],
                            "compat-libstdc++-33.x86_64": [],
                            "expect.x86_64": [],
                            "libaio.i686": [],
                            "libaio.x86_64": [],
                            "logrotate.x86_64": [],
                            "lsof.x86_64": [],
                            "gawk.x86_64": [],
                            "net-snmp.x86_64": [],
                            "net-tools.x86_64": [],
                            "nss-pam-ldapd.x86_64": [],
                            "ntp.x86_64": [],
                            "gdb.x86_64": [],
                            "openssh.x86_64": [],
                            "perl.x86_64": [],
                            "procps-ng.x86_64": [],
                            "openssl.x86_64": [],
                            "sssd.x86_64": [],
                            "sudo.x86_64": [],
                            "rsync.x86_64": [],
                            "sysstat.x86_64": [],
                            "tcp_wrappers.x86_64": [],
                            "unzip.x86_64": [],
                            "xinetd.x86_64": [],
                            "yum-utils.noarch": [],
                            "nss.x86_64": [],
                            "awscli.noarch": []
                          }
                        },
                        "commands": {
                          "E1": {
                            "command": "timedatectl set-timezone Asia/Kolkata"
                          },
                          "E2": {
                            "command": "sed -i.bak -e 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config"
                          },
                          "E3": {
                            "command": "sed -i.bak -e '/127.0.0.1/ c\\127.0.0.1 \t localhost'  /etc/hosts"
                          },
                          "E4": {
                            "command": "echo `hostname -I` `hostname` loghost | sed -e 's/\\(*\\) \\(*\\) loghost/ \\1 \\t \\2/' >> /etc/hosts"
                          },
                          "E5": {
                            "command": "sed -i.bak -e '/HOSTNAME/ d' /etc/sysconfig/network ; echo \HOSTNAME=`hostname`\ >> /etc/sysconfig/network"
                          },
                          "E6": {
                            "command": "systemctl start firewalld"
                          },
                          "E7": {
                            "command": "systemctl enable firewalld"
                          },
                          "E8_bug1": {
                            "command": "systemctl restart dbus"
                          },
                          "E8_bug2": {
                            "command": "systemctl restart firewalld"
                          },
                          "E9": {
                            "command": "firewall-cmd --set-default-zone=trusted"
                          },
                          "E10": {
                            "command": "sed -i.bak -e '/PasswordAuthentication no/ c PasswordAuthentication yes' /etc/ssh/sshd_config"
                          },
                          "R1": {
                            "command": "firewall-cmd --reload"
                          }
                        }
                      },
                      "network_server": {
                        "commands": {
                          "ns_c1": {
                            "command": "cd ~"
                          },
                          "ns_c2": {
                            "command": "mkdir -p bw/install/"
                          },
                          "ns_c3": {
                            "command": "cd ~/bw/install"
                          },
                          "ns_c4": {
                            "command": ""
                          }
                        }
                      }
                    }
                  }
                },
                "NetworkServer": {
                  "Type": "AWS::EC2::Instance",
                  "Properties": {
                    "LaunchTemplate": {
                      "LaunchTemplateId": {
                        "Ref": "BSLaunchTemplate"
                      },
                      "Version": "1"
                    },
                    "Tags": [
                      {
                        "Key": "Name",
                        "Value": "NetworkServer"
                      }
                    ],
                    "UserData": {
                      "Fn::Base64": {
                        "Fn::Join": [
                          "",
                          [
                            "#!/bin/bash \n",
                            "yum update -y \n",
                            "yum install epel-release -y \n",
                            "yum install python-pip -y \n",
                            "pip install --upgrade pip \n",
                            "pip install pystache argparse python-daemon requests \n",
                            "yum install -y https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-latest.amzn1.noarch.rpm \n",
                            "ln -s /usr/local/lib/python2.7/site-packages/cfnbootstrap /usr/lib/python2.7/site-packages/cfnbootstrap \n",
                            "/opt/aws/bin/cfn-init -v ",
                            "--stack ",
                            {
                              "Ref": "AWS::StackName"
                            },
                            " --resource BSLaunchTemplate",
                            " --configsets ns \n"
                          ]
                        ]
                      }
                    }
                  }
                }
              }
            }

        template['Resources']['BSLaunchTemplate']['Metadata']['AWS::CloudFormation::Init']['network_server']['commands']['ns_c4'] = 'aws s3 cp s3://{}/R23/NS/ ./ --recursive'.format(buk_name)
        
        return template



    def get_cfn_template_r21(self,buk_name):
        '''
        Should be used for Centos6/RHEL6 and version R21 of Broadworks
        '''
        template = {
              "Resources": {
                "BSLaunchTemplate": {
                  "Type": "AWS::EC2::LaunchTemplate",
                  "Properties": {
                    "LaunchTemplateName": "BroadSoftLaunchTemplate",
                    "LaunchTemplateData": {
                      "KeyName": "haystackaccess",
                      "ImageId": "ami-e3fdd999",
                      "InstanceType": "t2.medium",
                      "IamInstanceProfile":{"Name":"Burner_EC2_InsProf"},
                      "BlockDeviceMappings":[{"DeviceName":"/dev/sda1","Ebs":{"DeleteOnTermination":True}}],
                      "KeyName":'labaccess'
                      
                    }
                  },
                  "Metadata": {
                    "AWS::CloudFormation::Init": {
                      "configSets": {
                        "ns": [
                          "base",
                          "network_server"
                          ],
                          "as": [
                            "base",
                            "application_server"
                          ],
                          "xsp": [
                            "base",
                            "xsp_server"
                          ],
                          "ps": [
                            "base",
                            "ps_server"
                          ]
                      },
                      "base": {
                        "packages": {
                          "yum": {
                            "sed": [],
                            "bash.x86_64": [],
                            "bind-utils.x86_64": [],
                            "compat-libstdc++-33.x86_64": [],
                            "expect.x86_64": [],
                            "ksh.x86_64":[],
                            "libaio.i686": [],
                            "libaio.x86_64": [],
                            "lm_sensors.x86_64":[],
                            "logrotate.x86_64": [],
                            "lsof.x86_64": [],
                            "gawk.x86_64": [],
                            "net-snmp.x86_64": [],
                            "net-tools.x86_64": [],
                            "nss-pam-ldapd.x86_64": [],
                            "ntp.x86_64": [],
                            "gdb.x86_64": [],
                            "openssh.x86_64": [],
                            "perl.x86_64": [],
                            "procps.x86_64": [],
                            "openssl.x86_64": [],
                            "sssd.x86_64": [],
                            "redhat-lsb.x86_64":[],
                            "sudo.x86_64": [],
                            "rsync.x86_64": [],
                            "sysstat.x86_64": [],
                            "tcp_wrappers.x86_64": [],
                            "unzip.x86_64": [],
                            "xinetd.x86_64": [],
                            "yum-utils.noarch": [],
                            "nss.x86_64": [],        
                          }
                        },
                        "commands": {
                          "E1": {
                            "command": "ln -fs /usr/share/zoneinfo/Asia/Kolkata /etc/localtime"
                          },
                          "E2": {
                            "command": "sed -i.bak -e 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config"
                          },
                          "E3": {
                            "command": "sed -i.bak -e '/127.0.0.1/ c\\127.0.0.1 \t localhost'  /etc/hosts"
                          },
                          "E4": {
                            "command": "echo `hostname -I` `hostname` loghost | sed -e 's/\\(*\\) \\(*\\) loghost/ \\1 \t \\2/' >> /etc/hosts"
                          },
                          "E5": {
                            "command": "sed -i.bak -e '/HOSTNAME/ d' /etc/sysconfig/network ; echo \HOSTNAME=`hostname`\ >> /etc/sysconfig/network"
                          },
                          "E6": {
                            "command": "mv /etc/sysconfig/iptables /etc/sysconfig/iptables.bwBak"
                          },
                          "E7": {
                            "command": "mv /etc/sysconfig/ip6tables /etc/sysconfig/ip6tables.bwBak"
                          },
                          "E8": {
                            "command": "sed -i.bak -e '/PasswordAuthentication no/ c PasswordAuthentication yes' /etc/ssh/sshd_config"
                          },
                          "E9":{
                            "command":"mkdir -p /bw/install/"
                          },
                          "E91":{
                            "command":"cd /bw/install"
                          }
                        }
                      },
                      "network_server": {
                        "commands": {
                          "ns_c1": {
                            "command": ""
                          },
                          "ns_c2":{
                            "command":"chmod 654 /bw/install/*"
                          }
                        }
                      },
                      "application_server": {
                        "commands": {
                          "as_c1": {
                            "command": ""
                          },
                          "as_c2":{
                            "command":"chmod 654 /bw/install/*"
                          }
                        }
                      },
                      "xsp_server": {
                        "commands": {
                          "xsp_c1": {
                            "command": ""
                          },
                          "xsp_c2":{
                            "command":"chmod 654 /bw/install/*"
                          }
                        }
                      },
                      "ps_server": {
                        "commands": {
                          "ps_c1": {
                            "command": ""
                          },
                          "ps_c2":{
                            "command":"chmod 654 /bw/install/*"
                          }
                        }
                      }
                    }
                  }
                },
                "NetworkServer": {
                  "Type": "AWS::EC2::Instance",
                  "Properties": {
                    "LaunchTemplate": {
                      "LaunchTemplateId": {
                        "Ref": "BSLaunchTemplate"
                      },
                      "Version": "1"
                    },
                    "Tags": [
                      {
                        "Key": "Name",
                        "Value": "NetworkServer"
                      }
                    ],
                    "UserData": {
                      "Fn::Base64": {
                        "Fn::Join": [
                          "",
                          [
                            "#!/bin/bash \n",
                            "yum update -y \n",
                            "curl https://bootstrap.pypa.io/2.6/get-pip.py | python \n",
                            "yum install epel-release -y \n",
                            "pip install pystache argparse python-daemon requests awscli\n",
                            "yum install -y https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-latest.amzn1.noarch.rpm \n",
                            "ln -s /usr/local/lib/python2.7/site-packages/cfnbootstrap /usr/lib/python2.6/site-packages/cfnbootstrap \n",
                            "/opt/aws/bin/cfn-init -v ",
                            "--stack ",
                            {
                              "Ref": "AWS::StackName"
                            },
                            " --resource BSLaunchTemplate",
                            " --configsets ns \n"
                          ]
                        ]
                      }
                    }
                  }
                },
                "ApplicationServer": {
                  "Type": "AWS::EC2::Instance",
                  "Properties": {
                    "LaunchTemplate": {
                      "LaunchTemplateId": {
                        "Ref": "BSLaunchTemplate"
                      },
                      "Version": "1"
                    },
                    "Tags": [
                      {
                        "Key": "Name",
                        "Value": "ApplicationServer"
                      }
                    ],
                    "UserData": {
                      "Fn::Base64": {
                        "Fn::Join": [
                          "",
                          [
                            "#!/bin/bash \n",
                            "yum update -y \n",
                            "curl https://bootstrap.pypa.io/2.6/get-pip.py | python \n",
                            "yum install epel-release -y \n",
                            "pip install pystache argparse python-daemon requests awscli\n",
                            "yum install -y https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-latest.amzn1.noarch.rpm \n",
                            "ln -s /usr/local/lib/python2.7/site-packages/cfnbootstrap /usr/lib/python2.6/site-packages/cfnbootstrap \n",
                            "/opt/aws/bin/cfn-init -v ",
                            "--stack ",
                            {
                              "Ref": "AWS::StackName"
                            },
                            " --resource BSLaunchTemplate",
                            " --configsets as \n"
                          ]
                        ]
                      }
                    }
                  }
                },
                "XSPServer": {
                  "Type": "AWS::EC2::Instance",
                  "Properties": {
                    "LaunchTemplate": {
                      "LaunchTemplateId": {
                        "Ref": "BSLaunchTemplate"
                      },
                      "Version": "1"
                    },
                    "Tags": [
                      {
                        "Key": "Name",
                        "Value": "XSPServer"
                      }
                    ],
                    "UserData": {
                      "Fn::Base64": {
                        "Fn::Join": [
                          "",
                          [
                            "#!/bin/bash \n",
                            "yum update -y \n",
                            "curl https://bootstrap.pypa.io/2.6/get-pip.py | python \n",
                            "yum install epel-release -y \n",
                            "pip install pystache argparse python-daemon requests awscli\n",
                            "yum install -y https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-latest.amzn1.noarch.rpm \n",
                            "ln -s /usr/local/lib/python2.7/site-packages/cfnbootstrap /usr/lib/python2.6/site-packages/cfnbootstrap \n",
                            "/opt/aws/bin/cfn-init -v ",
                            "--stack ",
                            {
                              "Ref": "AWS::StackName"
                            },
                            " --resource BSLaunchTemplate",
                            " --configsets xsp \n"
                          ]
                        ]
                      }
                    }
                  }
                },
                "ProfileServer": {
                  "Type": "AWS::EC2::Instance",
                  "Properties": {
                    "LaunchTemplate": {
                      "LaunchTemplateId": {
                        "Ref": "BSLaunchTemplate"
                      },
                      "Version": "1"
                    },
                    "Tags": [
                      {
                        "Key": "Name",
                        "Value": "ProfileServer"
                      }
                    ],
                    "UserData": {
                      "Fn::Base64": {
                        "Fn::Join": [
                          "",
                          [
                            "#!/bin/bash \n",
                            "yum update -y \n",
                            "curl https://bootstrap.pypa.io/2.6/get-pip.py | python \n",
                            "yum install epel-release -y \n",
                            "pip install pystache argparse python-daemon requests awscli\n",
                            "yum install -y https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-latest.amzn1.noarch.rpm \n",
                            "ln -s /usr/local/lib/python2.7/site-packages/cfnbootstrap /usr/lib/python2.6/site-packages/cfnbootstrap \n",
                            "/opt/aws/bin/cfn-init -v ",
                            "--stack ",
                            {
                              "Ref": "AWS::StackName"
                            },
                            " --resource BSLaunchTemplate",
                            " --configsets ps \n"
                          ]
                        ]
                      }
                    }
                  }
                },
                "OracleSBC": {
                  "Type": "AWS::EC2::Instance",
                  "Properties": {
                    "InstanceType":"t2.medium",
                    "ImageId":"ami-0d5478770768d267c",
                    "KeyName" : "labaccess",
                    "Tags": [
                      {
                        "Key": "Name",
                        "Value": "TrunkingSBC "
                      }
                    ]
                  }
                }                
              }
            }

        template['Resources']['BSLaunchTemplate']['Metadata']['AWS::CloudFormation::Init']['network_server']['commands']['ns_c1']['command'] = 'aws s3 cp s3://{}/R21/NS/ /bw/install --recursive'.format(buk_name)
        template['Resources']['BSLaunchTemplate']['Metadata']['AWS::CloudFormation::Init']['application_server']['commands']['as_c1']['command'] = 'aws s3 cp s3://{}/R21/AS/ /bw/install --recursive'.format(buk_name)
        template['Resources']['BSLaunchTemplate']['Metadata']['AWS::CloudFormation::Init']['xsp_server']['commands']['xsp_c1']['command'] = 'aws s3 cp s3://{}/R21/XSP/ /bw/install --recursive'.format(buk_name)
        template['Resources']['BSLaunchTemplate']['Metadata']['AWS::CloudFormation::Init']['ps_server']['commands']['ps_c1']['command'] = 'aws s3 cp s3://{}/R21/PS/ /bw/install --recursive'.format(buk_name)

        return template
