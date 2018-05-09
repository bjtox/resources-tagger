import boto3
class instlist:
	def __init__(self, service, profile,region):
		self.session = boto3.Session(profile_name=profile)
		self.region = region
		self.client = self.session.client(service,region_name=region)

	def getInstancesBySg(self, sg):
		response = self.client.describe_instances(
		    Filters=[
		        {
		            'Name': 'instance.group-id',
		            'Values': [
		                sg,
		            ]
		        },
		    ]
		)
		return response

	def getGroups(self):
		return self.client.describe_security_groups()

	def getBalancersv2(self):
		alb = self.session.client('elbv2',region_name=self.region)
		response = alb.describe_load_balancers()
		return response

	def getBalancers(self):
		elb = self.session.client('elb',region_name=self.region)
		response = elb.describe_load_balancers()
		return response

	def getRDS(self):
		rds = self.session.client('rds',region_name=self.region)
		response = rds.describe_db_instances()
		return response


	def printPermissions(self, ipPermissions):	
		print "| From        | To           | Source  |"
		print "| ------------- |:-------------:| -----:|"
		for permission in ipPermissions:
			fromPort = "null"
			outPort = "null"
			if 'FromPort' in permission:
				fromPort = permission['FromPort']

			if 'ToPort' in permission:
				outPort = permission['ToPort']
			if permission['IpRanges']:
				for ip in permission['IpRanges']:
					print "| "+str(fromPort)+"        | "+str(outPort)+"           | "+ip['CidrIp']+"  |"
			if permission['UserIdGroupPairs']:
				for sg in permission['UserIdGroupPairs']:
					print "| "+str(fromPort)+"        | "+str(outPort)+"           | "+sg['GroupId']+"  |"
		

	def printInstances(self, instances):
		print "| Instance ID        | Instance NAme           | Status  |"
		print "| ------------- |:-------------:| -----:|"
		if instances['Reservations']:
			for reservation in instances['Reservations']:
				for instance in reservation['Instances']:
					Name = 'Unamed'
					for tag in instance['Tags']:
						if tag['Key']=='Name':
							Name = tag['Value']
					print "| "+ instance['InstanceId'] + "        | "+ Name + "           | "+ instance['State']['Name']+"  |"

	def printRDSs(self, RDSs, groupId):
		print "| DBInstanceIdentifier       | Status  |"
		print "| ------------- |:-------------:|"
		for rds in RDSs['DBInstances']:
			for sg in rds['VpcSecurityGroups']:
				if sg['VpcSecurityGroupId'] == groupId:
					print "| "+ rds['DBInstanceIdentifier']+"        |  "+rds['DBInstanceStatus']+"  |"
				

	def printALBs(self, ALBs, groupId):
		print "| ALB Arn        | Alb Name           | Status  |"
		print "| ------------- |:-------------:| -----:|"
		for alb in ALBs['LoadBalancers']:
			if groupId in alb['SecurityGroups']:
				print "| "+alb['LoadBalancerArn']+"        | "+alb['LoadBalancerName']+"           | "+alb['State']['Code']+"  |"

	def printELBs(self, ELBs, groupId):
		print "| ELB NAme        | DNS  |"
		print "| ------------- |:-------------:| "

		for elb in ELBs['LoadBalancerDescriptions']:
			if groupId in elb['SecurityGroups']:
				print "| "+elb['LoadBalancerName']+"        | "+elb['DNSName']+"  |"


	def printCombination(self):
		ALBs = self.getBalancersv2()
		ELBs = self.getBalancers()
		RDSs = self.getRDS()

		for group in self.getGroups()['SecurityGroups']:
			print "### Group Id: " + group['GroupId'] + "\nGroup Name: " + group['GroupName']
			print "#### Port"
			self.printPermissions(group['IpPermissions'])
			print "\n"
			instances = self.getInstancesBySg(group['GroupId'])
			print "#### Instances"
			self.printInstances(instances)
			print "\n"
			print "#### ALB"
			self.printALBs(ALBs,group['GroupId'])
			print "\n"
			print "#### ELB"
			self.printELBs(ELBs,group['GroupId'])
			print "\n"
			print "#### RDS"
			self.printRDSs(RDSs,group['GroupId'])
			print "\n"
			print "------"


lister = instlist('ec2', '<aws cli username>', '<region>')
print lister.printCombination()
#lister.printRDSs()