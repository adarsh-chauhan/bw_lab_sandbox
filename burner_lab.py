#!/usr/bin/env python3
# Developed and maintained by chaadars@
# Python 3.7.2

import boto3, os.path, botocore, json, threading, subprocess, time
from botocore import exceptions
from Json_Doc import Json_doc

class Lab():  
    if os.path.isfile(os.path.expanduser('~') + '/.aws/credentials'):
        file = open(os.path.expanduser('~') + '/.aws/credentials')
        list = file.read().splitlines()
        file.close()
        access_key_id = list[1].split('=')[1].strip()
        aws_secret_access_key = list[2].split('=')[1].strip()
    else:
        access_key_id = ""
        aws_secret_access_key = ""

    
    def __init__(self):        
        self.bucket = {'Name':'test','Data':{}}
        self.xacc_policy = {'Name':'Burner_Cross_Account_S3_Policy'}
        self.admin_user = {}
        self.ec2_role = {'Name':'Burner_EC2_Role'}
        self.instance_profile = {'Name':'Burner_EC2_InsProf'}
        self.stack = {'Name':'Bwlab'}
        self.json_doc = Json_doc()
        
        
    def execute(self):
        os.system('clear')
        Banner = """
###################################################
#       Broadwork Lab Builder Script v1.0         #
###################################################

The Script will create the following objects in your AWS account :

1) It will make a test request to validate the keys.
2) It will create a S3 bucket to store Broadwork's binaries.
3) It will create a cross account Policy and attach it to the user.
4) It will pull the binaries from remote S3 Bucket (lab.broadsoft).
5) It will create a role for EC2 to access binaries in S3 bucket and attach S3 admin permissions to it.
6) It will create Instance Profile and attach the role to it.
7) It will create keypair for you. 
8) It will finally create stack with the help of cloudformation template. \n


Press Enter to continue ...
        """
        print(Banner)
        stop = input() 
        if self.get_creds():
            if self.bucket_repo():
                if self.xaccount_policy():
                    self.t1 = threading.Thread(target=self.copy_binaries)
                    self.t1.start() 
                    self.createrole()
                    self.createinstanceprofile()
                    self.createkeys()
                    self.createstack()
            

    def get_creds(self):
        '''
        Checks for correct keys in ~/.aws/credentials otherwise prompts
        Returns AWS keys as dictionary
        '''
        print("\nSTEP 1 : Started : Validate AWS Keys")
        try:

            self.session = boto3.session.Session(aws_access_key_id = Lab.access_key_id, aws_secret_access_key = Lab.aws_secret_access_key)  
        
            self.s3_client = self.session.client('s3')
            self.iam_client = self.session.client('iam')
            self.cfn_client = self.session.client('cloudformation')
            self.ec2_client = self.session.client('ec2')

            res = self.iam_client.get_user()
            self.admin_user['Name'] = res['User']['UserName']
            self.admin_user['Arn'] = res['User']['Arn']
            self.admin_user['Data'] = res
            print('STEP 1 : Successful : Validate AWS Keys')
 
            return {'aws_access_key_id': Lab.access_key_id, 'aws_secret_access_key' : Lab.aws_secret_access_key}
        except (exceptions.NoCredentialsError, exceptions.ClientError):
            Lab.access_key_id = ""
            Lab.aws_secret_access_key = ""
            print('STEP 1 : INFO : Wrong or No Credentials/Keys Found')
            
            while Lab.access_key_id == "":
                Lab.access_key_id = input('STEP 1 : PROMPT : Enter the access_key_id : ')

            while Lab.aws_secret_access_key == "":
                Lab.aws_secret_access_key = input('STEP 1 : PROMPT : Enter the aws_secret_access_key : ')

            usr_dir = os.path.expanduser('~')
            file = open('{}/.aws/credentials'.format(usr_dir), 'w+')
            data='[default]\naws_access_key_id = {}\naws_secret_access_key = {}'.format(Lab.access_key_id,Lab.aws_secret_access_key)
            file.write(data)
            file.close()

            file = open('{}/.aws/config'.format(usr_dir), 'w+')
            data='[default]\nregion = us-east-1'
            file.write(data)
            file.close()
            
            return self.get_creds()

    
                
    def bucket_repo(self):
        '''
        Makes a bucket to store broadsoft binaries
        Returns Bucket Details as a dictionary
        '''
        print("STEP 2 : Started : Create bucket")
        try:
            if len(self.bucket['Name']) > 15:
                self.bucket['Name'] = input("STEP 2 : PROMPT : bucket_repo : Could not find a unique name for the bucket, please create a bucket and enter it's name here : ")
                
            arg = {'Bucket':self.bucket['Name']}
            res = self.s3_client.create_bucket(**arg)
            print("STEP 2 : Successful : Bucket [{}] Created".format(self.bucket['Name']))
            return self.bucket
        except self.s3_client.exceptions.BucketAlreadyExists:
            print('STEP 2 : INFO : bucket_repo : Bucket [{}] already exist, Trying Another name.... '.format(self.bucket['Name']))
            self.bucket['Name'] +=str(1)
            return self.bucket_repo()
        except self.s3_client.exceptions.ClientError as err:
            print('STEP 2 : ERROR : ', err.response['Error']['Message'])
            return self.bucket_repo()


    def xaccount_policy(self):
        '''
        Creates a policy for user to sync with external bucket(arn:aws:s3:::lab.broadsoft) present in lab account accessible through isengard
        and attaches the policy to the User
        Returns cross account policy details as a dictionary
        '''
        print("STEP 3 : Started : Create Cross Account Policy")
        try:
            arg = {}
            arg['PolicyDocument'] = json.dumps(self.json_doc.get_s3_xaccount(self.bucket['Name']))
            arg['PolicyName'] = self.xacc_policy['Name']
            res = self.iam_client.create_policy(**arg)
            self.xacc_policy['Name'] = res['Policy']['PolicyName']
            self.xacc_policy['Arn'] = res['Policy']['Arn']
            self.xacc_policy['Data'] = res
            print('STEP 3 : INFO : S3 Cross Account [{}] Policy Created '.format(arg['PolicyName']))
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            print('STEP 3 : INFO : xaccount_policy : S3 Cross Account Policy Already Exist : [{}]'.format(arg['PolicyName']))
            self.xacc_policy['Arn'] = self.iam_client.list_policies()['Policies'][0]['Arn']
            return self.xacc_policy
        finally:
            arg1 = {'UserName':self.admin_user['Name'],'PolicyArn':self.iam_client.list_policies()['Policies'][0]['Arn']}
            res1 = self.iam_client.attach_user_policy(**arg1)
            if res1['ResponseMetadata']['HTTPStatusCode'] == 200:
                print('STEP 3 : Successful : Cross account Policy [{}] Created & attached to User [{}]'.format(arg1['PolicyArn'],arg1['UserName']))
                return self.xacc_policy


    def copy_binaries(self):
        '''
        Copies binaries from isengard lab account to burner account bucket
        return the list of files as dictionary
        '''  
        try:
            res = self.s3_client.list_objects(Bucket = self.bucket['Name'], Prefix = 'R21/')
            if res.get('Contents') == None or len(res.get('Contents')) < 8:
                print("STEP 4 : Started : Copy Binaries")
                cmd = 'aws s3 cp s3://lab.test s3://{} --recursive'.format(self.bucket['Name'])
                res = subprocess.run(cmd, shell = True, check = True, stdout=subprocess.PIPE)
                if res.returncode == 0 and self.s3_client.list_objects(Bucket = self.bucket['Name'], Prefix = 'R21/')['Contents'] == 8:
                    print('STEP 4 : Successful : Binaries Copied to {}'.format(self.bucket['Name']))
                    return self.s3_client.list_objects(Bucket = self.bucket['Name'], Prefix = 'R21/')['Contents']
            else:
                print("STEP 4 : SKIP : Binaries already Present")
        except subprocess.CalledProcessError as e:
            print('STEP 4 : ERROR : Binaries could not be copied to [{}] due to following error {}'.format(self.bucket['Name'],e['Message']))
            return False


    def createrole(self):
        '''
        Creates a role assumable for EC2 and attaches S3 permissions to it
        '''
        try:
            print("STEP 5 : Started : Create Role : ")
            arg={'RoleName':self.ec2_role['Name'],'AssumeRolePolicyDocument':json.dumps({'Statement':{'Effect':'Allow','Action':['sts:AssumeRole'],'Principal':{'Service':['ec2.amazonaws.com']}}})}
            res = self.iam_client.create_role(**arg)
            self.ec2_role['Name'] = res['Role']['RoleName']
            self.ec2_role['Arn'] = res['Role']['Arn']
            self.ec2_role['Data'] = res
            print('STEP 5 : INFO : EC2 assumable Role Created : [' + self.ec2_role['Name'] + ']' )
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            print('STEP 5 : INFO : createrole : Role Already Exist')
        finally:
            arg2 = {'RoleName': self.ec2_role['Name'], 'PolicyArn': 'arn:aws:iam::aws:policy/AmazonS3FullAccess'}
            res1 = self.iam_client.attach_role_policy(**arg2)
            print('STEP 5 : Successful : Created Role [{}] and attached [AmazonS3FullAccess] Policy to it'.format(self.ec2_role['Name'], ))


    def createinstanceprofile(self):
        '''
        Creates Instance Profile and attaches the EC2 Role to it which has permissions to access S3
        '''
        print("STEP 6 : Started : Create Intance Profile")
        try:
            res = self.iam_client.create_instance_profile(InstanceProfileName = self.instance_profile['Name'])
            self.instance_profile['Arn'] = res['InstanceProfile']['Arn']
            self.instance_profile['Data'] = res
            arg = {'InstanceProfileName': self.instance_profile['Name'],'RoleName': self.ec2_role['Name']}
            self.iam_client.add_role_to_instance_profile(**arg)
            print('STEP 6 : Successful : Intance Profile [{}] created and attached Role [{}] to it'.format(self.instance_profile['Name'],self.ec2_role['Name']))
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            print('STEP 6 : Successful : Intance Profile [{}] Already Exist'.format(self.instance_profile['Name']))


    def createkeys(self):
        print("STEP 7 : Started : Create Key Pairs")
        try:
            res = self.ec2_client.create_key_pair(KeyName='labaccess')
            usr_dir = os.path.expanduser('~')
            file = open(usr_dir + '/labaccess.pem','w+')
            file.write(res['KeyMaterial'])
            file.close()
            print("STEP 7 : Successful : Key Pairs [labaccess.pem] Created in {}".format(usr_dir))
        except self.ec2_client.exceptions.ClientError as err:
            if err.response['Error']['Code'] == 'InvalidKeyPair.Duplicate':
                print("STEP 7 : INFO : Duplicate keypairs ")
                print("STEP 7 : DELETE : Delete existing Key Pairs")
                self.ec2_client.delete_key_pair(KeyName='labaccess')
                return self.createkeys()
            
                 

    def createstack(self):
        '''
        Create the stack using the cloudformation template        
        '''
        print("STEP 8 : Started : Create Stack : ")
        try: 
            template = self.json_doc.get_cfn_template_r21(self.bucket['Name'])
            res = self.cfn_client.create_stack(StackName=self.stack['Name'],TemplateBody=json.dumps(template))
            status = True
            while status == True:
                for i in self.cfn_client.describe_stack_events(StackName = self.stack['Name'])['StackEvents']:
                    if i['LogicalResourceId'] == self.stack['Name'] and i['ResourceStatus'] == 'CREATE_COMPLETE':
                        print('STEP 7 : Successful : Stack [{}] Created \n\n'.format(self.stack['Name']))
                        status == False
                        exit()
                    if i['LogicalResourceId'] == self.stack['Name'] and i['ResourceStatus'] == 'ROLLBACK_COMPLETE':
                        print('STEP 7 : FAILED : Stack [{}] Create \n\n'.format(self.stack['Name']))
                        status == False
                        exit()
                    else:
                        print(i['StackName'], ':',  i['LogicalResourceId'], ':' , i['ResourceStatus'])
                        status = True
                        time.sleep(5)
                        
        except self.cfn_client.exceptions.AlreadyExistsException:
            status = True
            stop = input('\n** INFO ** : Press Enter to Delete Existing Stack {} : '.format(self.stack['Name']))
            self.cfn_client.delete_stack(StackName = self.stack['Name'])
            try:
                while status == True:
                    for i in self.cfn_client.describe_stack_events(StackName = self.stack['Name'])['StackEvents']:
                        if i['LogicalResourceId'] == self.stack['Name'] and i['ResourceStatus'] == 'DELETE_COMPLETE':
                            print(i['StackName'],self.stack['Name'], ':',  i['LogicalResourceId'], ':' , i['ResourceStatus'])
                            status == False
                        else:
                            print(i['StackName'], ':',  i['LogicalResourceId'], ':' , i['ResourceStatus'])
                            status = True
                            time.sleep(5)
            except exceptions.ClientError as err:
                if err.response['Error']['Code'] == 'ValidationError':
                    print('STEP 8 : DELETE : Stack [{}] DELETED \n\n'.format(self.stack['Name']))
            return self.createstack()
            
        
                
if __name__ == '__main__':
    burner = Lab()
    burner.execute()
