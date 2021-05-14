#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import modules
import os
import boto3
import yaml
import time


# In[2]:


# Boto3 Resource Interface to use high-level services
ec2 = boto3.resource('ec2')


# In[7]:


# Generate Key-Pair file for accessing EC-2 Instance and store it locally
outfile = open('ec2-keypair1.pem', 'w')
key_pair = ec2.create_key_pair(KeyName='ec2-keypair1')
KeyPairOut = str(key_pair.key_material)

# Change the mode of file to read only 
with os.fdopen(os.open("ec2-keypair1.pem", os.O_WRONLY | os.O_CREAT, 0o400), "w+") as handle:
        handle.write(KeyPairOut)


# In[19]:


# Read the yaml file
with open("specs.yaml", "rt") as f:
    data = yaml.safe_load(f)


# In[5]:


# Creates Instance with required specifications
instance = ec2.create_instances(
    InstanceType = data["server"]["instance_type"],
    KeyName ="ec2-keypair1",
    ImageId = "ami-0d5eff06f840b45e9",
    MinCount=data["server"]["min_count"],
    MaxCount=data["server"]["max_count"],
    Placement={
        'AvailabilityZone': 'us-east-1a'
    }
    )


# In[6]:


# Create Volume 1
Volume1 = ec2.create_volume(AvailabilityZone="us-east-1a", Size=data["server"]["volumes"][0]["size_gb"], VolumeType=data["server"]["volumes"][0]["type"])


# In[ ]:


# Attach Volume 1 
ec2.Instance(instance[0].id).attach_volume(VolumeId = Volume1.id, Device=data["server"]["volumes"][0]["device"])


# In[8]:


# Create and Attach Volume 2
Volume2 = ec2.create_volume(AvailabilityZone="us-east-1a", Size=data["server"]["volumes"][1]["size_gb"], VolumeType=data["server"]["volumes"][1]["type"])

time.sleep(5)

ec2.Instance(instance[0].id).attach_volume(VolumeId = Volume2.id, Device=data["server"]["volumes"][1]["device"])


# In[14]:


# Create IAM Client
iam = boto3.client('iam')

# Create user 1
response_user1 = iam.create_user(
    UserName=data["server"]["users"][0]["login"]
)


# In[15]:


# Attach a policy to user 1
iam.attach_user_policy(
 UserName = data["server"]["users"][0]["login"], 
 PolicyArn='arn:aws:iam::aws:policy/AmazonEC2FullAccess'
)


# In[10]:


# Create user 2
response_user2 = iam.create_user(
    UserName=data["server"]["users"][1]["login"]
)


# In[11]:


# Attach a policy to user
iam.attach_user_policy(
 UserName = data["server"]["users"][0]["login"], 
 PolicyArn='arn:aws:iam::aws:policy/AmazonEC2FullAccess'
)


# In[23]:


# In[24]:
# A low-level Client representing AWS Identity and Access Management
client = boto3.client('iam')

# Uploads an SSH Public Key and associates it with a user1
response_client_1 = client.upload_ssh_public_key(
    UserName=data["server"]["users"][0]["login"],
    SSHPublicKeyBody=data["server"]["users"][0]["ssh_key"]
)


# In[ ]:


# Uploads an SSH Public Key and associates it with a user2
response_client_2 = client.upload_ssh_public_key(
    UserName=data["server"]["users"][1]["login"],
    SSHPublicKeyBody=data["server"]["users"][1]["ssh_key"]
)


# In[17]:


# A low-level client representing AWS EC2 Instance Connect 
ec2_client = boto3.client('ec2-instance-connect')


# In[20]:


# Pushes an SSH public key to the specificied EC2 instance for the use by User1 
response_of_user1 = ec2_client.send_ssh_public_key(
    InstanceId= instance[0].id,
    InstanceOSUser= data["server"]["users"][0]["login"],
    SSHPublicKey= data["server"]["users"][0]["ssh_key"],
    AvailabilityZone= 'us-east-1a'
)


# In[21]:


# Pushes an SSH public key to the specificied EC2 instance for the use by User2
response_of_user2 = ec2_client.send_ssh_public_key(
    InstanceId= instance[0].id,
    InstanceOSUser= data["server"]["users"][1]["login"],
    SSHPublicKey= data["server"]["users"][1]["ssh_key"],
    AvailabilityZone= 'us-east-1a'
)


# In[ ]:




