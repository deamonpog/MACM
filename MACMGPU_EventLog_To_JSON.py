import pandas as pd
import random
import os
import numpy as np
import datetime
import json
import re
import configparser
import sys
#from collections import OrderedDict

# Common Options
_multi_run = False

_ScenarioNo = 2
_Sim_StartTime = '2018.07.23'
_Sim_EndTime = '2019.04.30'
_CurrentSprint = 15
_CommitSha = 'cef0303862b0014e0605f3f0fad55a7ab090dc32'
_output_directory_path = "/home/social-sim/MACMWorking/MACM/CP3Submissions/sc2/Ready_Fixed_noRnd"

#_nodelist_file = '/home/social-sim/MACMWorking/MACM/DryRun/Inputs/cp3_dry_run_s1_nodelist_updated.txt'
#_nodelist_file = '/home/social-sim/MACMWorking/MACM/DryRunCp3_Sc2/Inputs/Exo/WhiteHelmets/cp3_dry_run_s2_nodelist.txt'
#_nodelist_file = '/home/social-sim/MACMWorking/MACM/DryRun/Inputs/raw_exogenous/NVD/cp3_s1_nodelist.txt'
_nodelist_file = '/home/social-sim/MACMWorking/MACM/CP3Submissions/sc2/cp3_s2_nodelist.txt'

_GroupDesc = 'MACMGPUv2.30'
_RunBy = 'Chathika'
_RunNumber = 0

_mynote = 'QPI MMD30 Alpha0.3 Threshold10 For CP3 Submission SC2 noRnd Fixed'

# Multiple Files Optioins
_mr_csv_folder = '/home/social-sim/MACMWorking/MACM/CP3Submissions/sc1/Original'

# Single File Options
_file_csv_eventlog = '/home/social-sim/MACMWorking/MACM/CP3Submissions/sc2/original/MACM_MMD30_Alpha0.3_2020-01-23 11:39:56.281954.csv'
_file_csv_S3Location = 'null'
_Model_MemoryDepth = 30
_Model_OverloadFactor = 0.3
_IdentifierStr = 'MACMGPUxQPIRegular2-sp' + str(_CurrentSprint)
_RunGroup = 'cp3_sp' + str(_CurrentSprint) + '_MACMGPUxQPIRegular2'

# Following global variables are used by functions below.
nextNodeID = -13.0
nextUserID = -21.0
dfMainLog = pd.DataFrame()

class Parameters:
	def __init__(self, in_ParamFilePath):
		self.ParamsFilePath = in_ParamFilePath
		self.ReadParams()
	
	def ReadParams(self):
		config = configparser.ConfigParser()
		config.read(self.ParamsFilePath)
		# Common Options
		multi_run = config['DEFAULT']['multi_run']
		ScenarioNo = config['DEFAULT']['ScenarioNo']
		Sim_StartTime = config['DEFAULT']['Sim_StartTime']
		Sim_EndTime = config['DEFAULT']['Sim_EndTime']
		CurrentSprint = config['DEFAULT']['CurrentSprint']
		CommitSha = config['DEFAULT']['CommitSha']
		output_directory_path = config['DEFAULT']['output_directory_path']
		nodelist_file = config['DEFAULT']['nodelist_file']
		GroupDesc = config['DEFAULT']['GroupDesc']
		RunBy = config['DEFAULT']['RunBy']
		RunNumber = config['DEFAULT']['RunNumber']
		mynote = config['DEFAULT']['mynote']
		# Multiple Files Optioins
		mr_csv_folder = config['MultipleFiles']['mr_csv_folder']
		# Single File Options
		file_csv_eventlog = config['SingleFiles']['file_csv_eventlog']
		file_csv_S3Location = config['SingleFiles']['file_csv_S3Location']
		Model_MemoryDepth = config['SingleFiles']['Model_MemoryDepth']
		Model_OverloadFactor = config['SingleFiles']['Model_OverloadFactor']
		IdentifierStr = config['SingleFiles']['IdentifierStr']
		RunGroup = config['SingleFiles']['RunGroup']
		# Print Parameters:
		fileTypeKey = 'MultipleFiles' if eval(multi_run) else 'SingleFiles'
		print(fileTypeKey)
		for key in config[fileTypeKey]:
			print('Key: ' + key + '\n\t--> Value: ' + config[fileTypeKey][key] + '\n\t--> Eval: ' + str(eval(config[fileTypeKey][key])) + '\n\t--> EvalType: ' + str(type(eval(config[fileTypeKey][key]))))
		
		# Assign parameters:
		# Common Options
		self.multi_run = eval(multi_run)
		self.ScenarioNo = eval(ScenarioNo)
		self.Sim_StartTime = eval(Sim_StartTime)
		self.Sim_EndTime = eval(Sim_EndTime)
		self.CurrentSprint = eval(CurrentSprint)
		self.CommitSha = eval(CommitSha)
		self.output_directory_path = eval(output_directory_path)
		self.nodelist_file = eval(nodelist_file)
		self.GroupDesc = eval(GroupDesc)
		self.RunBy = eval(RunBy)
		self.RunNumber = eval(RunNumber)
		self.mynote = eval(mynote)
		# Multiple Files Optioins
		self.mr_csv_folder = eval(mr_csv_folder)
		# Single File Options
		self.file_csv_eventlog = eval(file_csv_eventlog)
		self.file_csv_S3Location = eval(file_csv_S3Location)
		self.Model_MemoryDepth = eval(Model_MemoryDepth)
		self.Model_OverloadFactor = eval(Model_OverloadFactor)
		self.IdentifierStr = eval(IdentifierStr)
		self.RunGroup = eval(RunGroup)
		
		# Done.

def MultiRun(in_Params):
	global nextNodeID
	global nextUserID
	global dfMainLog

	print("--Begining of Script--")
	dfMainLog = pd.DataFrame(columns=['filename', 'nodeTime_msc', 'nodeUserID_n1c', 'actionType_n1c', 'actionType_uec', 'nodeID_n1c', 'parentID_n1c', 'rootID_n1c', 'informationID_uidc', 'informationID_n1c', 'informationID_vmic', 'informationID_mic','informationID_uiidc','informationID_uiids', 'platform_n1c', 'platform_mpc', 'has_URL', 'links_to_external', 'domain_linked', 'eventlogjson','mynote'])
	#dfMainLog = dfMainLog.index.name = 'FileNumber'
	if not _multi_run:
		Run(_file_csv_eventlog, _nodelist_file, _file_csv_S3Location, _ScenarioNo, _Sim_StartTime, _Sim_EndTime, _Model_MemoryDepth, _Model_OverloadFactor, _IdentifierStr, _CurrentSprint, _CommitSha, _RunGroup, _GroupDesc, _RunBy, _RunNumber, _output_directory_path, _mynote)
	else:
		for f in os.listdir(_mr_csv_folder):
			print('-- Processing File :' + f + ' --')
			file_csv_eventlog = os.path.join(_mr_csv_folder,f)
			temp = re.search('MMD[0-9]*',f)
			Model_MemoryDepth = f[temp.span()[0] + 3 : temp.span()[1]]
			temp = re.search('Alpha[0-9.]*',f)
			Model_OverloadFactor = float(f[temp.span()[0] + 5 : temp.span()[1]])
			IdentifierStr = 'MACMGPUxRndInfoIDS1-sp' + str(_CurrentSprint)
			RunGroup = 'cp3_sp' + str(_CurrentSprint) + '_MACMGPUxRndInfoIDS1'
			#IdentifierStr = 'MACMGPUxQPI' + str(Model_MemoryDepth) + '_' + ( "%.2f" % Model_OverloadFactor ).replace('.','_')
			#RunGroup = 'cp3_sp' + str(_CurrentSprint) + '_' + IdentifierStr
			Run(file_csv_eventlog, _nodelist_file, _file_csv_S3Location, _ScenarioNo, _Sim_StartTime, _Sim_EndTime, Model_MemoryDepth, Model_OverloadFactor, IdentifierStr, _CurrentSprint, _CommitSha, RunGroup, _GroupDesc, _RunBy, _RunNumber, _output_directory_path, _mynote)
	
	logfilename = _output_directory_path + "/" + "log-" + datetime.datetime.now().strftime("%m-%d-%Y-%H-%M-%S-%f") + ".csv"
	dfMainLog.to_csv(logfilename, index_label='FileIndex')
	print("\nThe Script Log file at : " + logfilename)
	print("--End of Script--")

def Run(file_csv_eventlog, _nodelist_file, file_csv_S3Location, ScenarioNo, Sim_StartTime, Sim_EndTime, Model_MemoryDepth, Model_OverloadFactor, IdentifierStr, CurrentSprint, CommitSha, RunGroup, GroupDesc, RunBy, RunNumber, output_directory_path, mynote):
	global nextNodeID
	global nextUserID
	global dfMainLog

	thislog = {}
	thislog['filename'] = file_csv_eventlog

	if not os.path.exists(output_directory_path):
		print ("The Output directory path does not exist!")
		exit()

	thisDT = datetime.datetime.now()
	file_name_prefix = thisDT.strftime("%m-%d-%Y-%H-%M-%S-%f") + "-" + str(RunGroup) + "-" + str(RunNumber)
	file_eventLog = output_directory_path + "/" + file_name_prefix + "-MP-Sc" + str(ScenarioNo) + ".json"
	file_metadata = output_directory_path + "/" + file_name_prefix + "-xMetadata.json"

	print('\treading event log file...')
	print('\t\tFile Name: ' + file_csv_eventlog)
	originalData = pd.read_csv(file_csv_eventlog,dtype={'userID':str,'conversationID':str,'parentID':str,'nodeID':str, 'informationIDs':str},na_values=str, parse_dates=['time'])
	print('\trenaming columns...')
	originalData.rename(columns={'userID':'nodeUserID','action':'actionType','time':'nodeTime','conversationID':'rootID','informationIDs':'informationID'},inplace=True)
	print('\t\tShape is : ' + str(originalData.shape))
	print('\tcalculating next UserID and NodeID values...')
	nextUserID = np.nansum([originalData['nodeUserID'].apply(pd.to_numeric,errors='coerce').max(), 537])
	print('\t\tNext User ID : ' + str(nextUserID))
	nextNodeID = np.nansum([originalData['nodeID'].apply(pd.to_numeric,errors='coerce').max() , 213])
	print('\t\tNext Node ID : ' + str(nextNodeID))

	# -----------------------------------MAPPING OF EVENTS---------------------
	platformToEventTypeToEvent = {
		'twitter':{
					"creation": ["tweet"],
					"contribution": ["reply","quote"],
					"sharing": ["retweet"] 
				},
		'github':{
					"creation": ["CreateEvent"],
					"contribution": ['IssueCommentEvent', 'PullRequestEvent', 'PullRequestReviewCommentEvent', 'PushEvent','IssuesEvent', 'CommitCommentEvent',"DeleteEvent"],
					"sharing": ["ForkEvent","WatchEvent"]
				},
		'reddit':{
					"creation": ["post"],
					"contribution": ["comment"],
					"sharing": ['comment']
				},
		'telegram':{
					"creation": ['message'],
					"contribution": ["message"],
					"sharing": ['message']
				},
		'youtube':{
					"creation": ['video'],
					"contribution": ["comment"],
					"sharing": ['comment']
				}
	}

	def MapEventUniformlyRandom(record):
		temp = platformToEventTypeToEvent[record['platform']][record['actionType']]
		if len(temp) < 1:
			return 'UNKNOWN-EVENT'
		return random.choice(temp)

	def MapEventProbablyRandom(record):
		temp = platformToEventTypeToEvent[record['platform']][record['actionType']]
		if len(temp) < 1:
			return 'UNKNOWN-EVENT'
		if record['platform'] == 'twitter' and record['actionType'] == 'contribution':
			return 'reply' if random.random() < 0.6698681489736988 else 'quote'
		return random.choice(temp)

	#=====================================================================================

	def RemovePlatformFromUserIDAndResolveNegatives(record):
		global nextUserID
		nameAndID = record['nodeUserID'].split('_',1)
		if nameAndID[0] == 'github' or \
		nameAndID[0] == 'reddit' or \
		nameAndID[0] == 'twitter' or \
		nameAndID[0] == 'telegram' or \
		nameAndID[0] == 'youtube':
			return nameAndID[1]
		elif record['nodeUserID'] == '-1.0':
			nextUserID += 1
			return str(nextUserID)
		else:
			return record['nodeUserID']
	
	def RemovePlatformFromNodeID(record):
		global nextNodeID
		nameAndID = record['nodeID'].split('_',1)
		if nameAndID[0] == 'github' or \
		nameAndID[0] == 'reddit' or \
		nameAndID[0] == 'twitter' or \
		nameAndID[0] == 'telegram' or \
		nameAndID[0] == 'youtube':
			return nameAndID[1]
		else:
			return record['nodeID']

	def RemovePlatformFromParentID(record):
		global nextNodeID
		nameAndID = record['parentID'].split('_',1)
		if nameAndID[0] == 'github' or \
		nameAndID[0] == 'reddit' or \
		nameAndID[0] == 'twitter' or \
		nameAndID[0] == 'telegram' or \
		nameAndID[0] == 'youtube':
			return nameAndID[1]		
		else:
			return record['parentID']
	
	def RemovePlatformFromRootID(record):
		global nextNodeID
		nameAndID = record['rootID'].split('_',1)
		if nameAndID[0] == 'github' or \
		nameAndID[0] == 'reddit' or \
		nameAndID[0] == 'twitter' or \
		nameAndID[0] == 'telegram' or \
		nameAndID[0] == 'youtube':
			return nameAndID[1]
		else:
			return record['rootID']

	print('\tmapping platform...')
	originalData['platform'] = originalData.apply(lambda x: x['nodeUserID'].split('_')[0],axis = 1)

	print('\tresolving userid, nodeid, parentid, and rootid...')
	print("\t\tCurrent NextUserID value: " + str(nextUserID))
	print("\tresolving userid values...")
	originalData['nodeUserID'] = originalData.apply(lambda x: RemovePlatformFromUserIDAndResolveNegatives(x), axis = 1)	
	print("\t\tCurrent NextUserID value: " + str(nextUserID))
	print("\t\tCurrent NextNodeID value: " + str(nextNodeID))
	print('\tresolving nodeid values...')
	originalData['nodeID'] = originalData.apply(lambda x: RemovePlatformFromNodeID(x), axis = 1)
	print("\t\tCurrent NextNodeID value: " + str(nextNodeID))
	print('\tresolving parentid values...')
	originalData['parentID'] = originalData.apply(lambda x: RemovePlatformFromParentID(x), axis = 1)
	print("\t\tCurrent NextNodeID value: " + str(nextNodeID))
	print('\tresolving rootid values...')
	originalData['rootID'] = originalData.apply(lambda x: RemovePlatformFromRootID(x), axis = 1)
	print("\t\tCurrent NextNodeID value: " + str(nextNodeID))

	print('\t\t nodeID')
	temp = originalData.loc[originalData['nodeID'] == '-1.0'].shape[0]
	print('\t\t\t -1.0 Count : \t' + str(temp))


	#fix github nodeID

	#resolve github seperately
	nextNodeID += 1
	gitNegOneValue = nextNodeID
	nextNodeID += 1
	def ReplaceGitHubNegOneRoot(x):
		global nextNodeID
		if (x['platform'] == "github") and (x["rootID"] == "-1.0"):
			return gitNegOneValue
		return x['rootID']
	
	originalData["rootID"] = originalData.apply(lambda x: ReplaceGitHubNegOneRoot(x),axis=1)
	originalData["parentID"] = originalData.apply(lambda x: x["rootID"] if x["platform"]=="github" else x["parentID"],axis =1 )
	originalData["nodeID"] = originalData.apply(lambda x: x["rootID"] if x["platform"]=="github" else x["nodeID"],axis =1 )

	print('\t\t nodeID')
	temp = originalData.loc[originalData['nodeID'] == '-1.0'].shape[0]
	print('\t\t\t -1.0 Count : \t' + str(temp))

	print('\tmappinging actionType...')
	originalData['actionType'] = originalData.apply(lambda x: MapEventUniformlyRandom(x),axis=1)

	print('\tcreating node to platform map...')
	node_to_plat = originalData.set_index('rootID').to_dict()['platform']
	node_to_plat.update(originalData.set_index('parentID').to_dict()['platform'])
	node_to_plat.update(originalData.set_index('nodeID').to_dict()['platform'])

	PlatformLinkMap = {
		'twitter':'twitter.com',
		'github':'github.com',
		'reddit':'reddit.com',
		'telegram':'telegram.com',
		'youtube' : 'youtube.com'
	}

	def SetHasURL(record):
		if record['platform'] != node_to_plat[ record['parentID'] ] or record['platform'] != node_to_plat[ record['rootID'] ]:
			return 1
		else:
			return 0

	def SetLinksToExternal(record):
		if record['platform'] != node_to_plat[ record['parentID'] ] or record['platform'] != node_to_plat[ record['rootID'] ]:
			return 1
		else:
			return 0

	def SetDomainLinked(record):
		if record['platform'] != node_to_plat[ record['parentID'] ] or record['platform'] != node_to_plat[ record['rootID'] ]:
			thisUrlList = []
			if record['platform'] != node_to_plat[ record['parentID'] ] :
				thisUrlList.append(PlatformLinkMap[ node_to_plat[ record['parentID'] ] ])
			if record['platform'] != node_to_plat[ record['rootID'] ] :
				thisUrlList.append(PlatformLinkMap[ node_to_plat[ record['rootID'] ] ])
			return list(set(thisUrlList)) 
		else:
			return record['domain_linked']

	print('\tsetting default url parameters...')
	#originalData['urlDomain'] = np.empty((len(originalData),0)).tolist()
	originalData['has_URL'] = 0
	originalData['links_to_external'] = 0
	originalData['domain_linked'] = np.empty((len(originalData),0)).tolist()
	print('\tapplying url parameter calculations...')
	originalData['has_URL'] = originalData.apply(lambda x: SetHasURL(x), axis = 1)
	originalData['links_to_external'] = originalData.apply(lambda x: SetLinksToExternal(x), axis = 1)
	originalData['domain_linked'] = originalData.apply(lambda x: SetDomainLinked(x), axis = 1)

	# -- Process INFORMATION ID --
	print('\treading infoid list file...')
	print('\t\tFile Name: ' + _nodelist_file)
	nodeList = pd.read_csv(_nodelist_file)
	print('\tapplying random infoids to empty infoid values...')

	def PickRandomInfoIDIfEmpty(record):
		if record['informationID'] == '[]' or record['informationID'] == '-1.0' or record['informationID'] == '': #or type(record['informationID']) != str:
			return [ nodeList.sample(1).iloc[0][0] ]
		return record['informationID']
	originalData['informationID'] = originalData.apply(lambda x: PickRandomInfoIDIfEmpty(x), axis = 1)

	# def PickRandomInfoID(record):
	# 	return nodeList.sample(1).iloc[0][0]
	#originalData['informationID'] = originalData.apply(lambda x: PickRandomInfoID(x), axis = 1)

	print('\tcalculating node to infoid and node to parent hash maps...')
	node_to_info = originalData.set_index('nodeID').to_dict()['informationID']
	node_to_parent = originalData.set_index('nodeID').to_dict()['parentID']

	print('\tmapping infoids according to cascades...')

	def PickRootInfoID(record):
		infoids=list(set( eval(record['informationID']) ))
		retval = []
		for infoid in infoids:
			if infoid != -1.0 and infoid != '-1.0' and infoid != '[]':
				retval.append(infoid)
		if len(retval) < 1:
			if record['rootID'] in node_to_info.keys():
				retval = node_to_info[ record['rootID'] ]
			elif record['parentID'] in node_to_info.keys():
				currentParent = record['parentID']
				#print('\t\tsolving parent: ' + str(currentParent))
				while node_to_parent[currentParent] in node_to_info.keys():
					currentParent = node_to_parent[currentParent]
					#print('\t\t\tlooking for parent of : '+str(currentParent))
					if currentParent == node_to_parent[currentParent]:
						break
				#print('\t\t\tresolved to : ' + str(currentParent))
				retval = node_to_info[currentParent]
			else:
				retval.append(nodeList.sample(1).iloc[0][0])
		return retval if len(retval) > 0 else [nodeList.sample(1).iloc[0][0]]
	originalData['informationID'] = originalData.apply(lambda x: PickRootInfoID(x), axis = 1)

	# def PickRootInfoID(record):
	# 	if record['rootID'] in node_to_info.keys():
	# 		return node_to_info[ record['rootID'] ]
	# 	elif record['parentID'] in node_to_info.keys():
	# 		currentParent = record['parentID']
	# 		#print('\t\tsolving parent: ' + str(currentParent))
	# 		while node_to_parent[currentParent] in node_to_info.keys():
	# 			currentParent = node_to_parent[currentParent]
	# 			#print('\t\t\tlooking for parent of : '+str(currentParent))
	# 			if currentParent == node_to_parent[currentParent]:
	# 				break
	# 		#print('\t\t\tresolved to : ' + str(currentParent))
	# 		return node_to_info[currentParent]
	# 	else:
	# 		return record['informationID']
	# originalData['informationID'] = originalData.apply(lambda x: PickRootInfoID(x), axis = 1)
	
	print('\titerating the dataframe to multiplicate the multiple-infoid-valued rows...')
	print('infoids ' + str(originalData['informationID'].astype(str).unique().shape[0]))
	NewRows = []
	#RemoveRows = []
	setOfReqNodes = set(nodeList['nodevalues'])
	for index,row in originalData.iterrows():
		temp = str(row['informationID'])
		if temp[0] == '[' and temp != '[]':
			# check if the list is single token
			#RemoveRows.append(index)
			for iid in list(set(eval(temp))):
				if iid in setOfReqNodes:
					NewRows.append([ row['nodeTime'], row['nodeUserID'], row['actionType'], row['nodeID'], row['parentID'], row['rootID'], iid, row['platform'], row['has_URL'], row['links_to_external'], row['domain_linked'] ])
	
	originalData = pd.DataFrame(NewRows, columns=originalData.columns)
	print('infoids ' + str(originalData['informationID'].unique().shape[0]))
		
	# Verification
	print("\tVERIFICATION...")

	def ValidateTimeString(record):
		matchObj = re.fullmatch(r'^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}',str(record['nodeTime']))
		if matchObj == None:
			return 1
		else:
			return 0
	
	print('\t\t nodeTime')
	temp = originalData.apply(lambda x: ValidateTimeString(x), axis = 1).sum()
	print('\t\t\t Mismatching String Count : \t' + str(temp))
	thislog['nodeTime_msc'] = temp
	
	print('\t\t nodeUserID')
	temp = originalData.loc[originalData['nodeUserID'] == '-1.0'].shape[0]
	print('\t\t\t -1.0 Count : \t' + str(temp))
	thislog['nodeUserID_n1c'] = temp

	print('\t\t actionType')
	temp = originalData.loc[originalData['actionType'] == '-1.0'].shape[0]
	print('\t\t\t -1.0 Count : \t' + str(temp))
	thislog['actionType_n1c'] = temp
	temp = originalData.loc[originalData['actionType'] == 'UNKNOWN-EVENT'].shape[0]
	print('\t\t\t UNKNOWN-EVENT Count : ' + str(temp))
	thislog['actionType_uec'] = temp

	print('\t\t nodeID')
	temp = originalData.loc[originalData['nodeID'] == '-1.0'].shape[0]
	print('\t\t\t -1.0 Count : \t' + str(temp))
	thislog['nodeID_n1c'] = temp

	print('\t\t parentID')
	temp = originalData.loc[originalData['parentID'] == '-1.0'].shape[0]
	print('\t\t\t -1.0 Count : \t' + str(temp))
	thislog['parentID_n1c'] = temp

	print('\t\t rootID')
	temp = originalData.loc[originalData['rootID'] == '-1.0'].shape[0]
	print('\t\t\t -1.0 Count : \t' + str(temp))
	thislog['rootID_n1c'] = temp

	print('\t\t informationID')
	set_of_nodeids = nodeList[nodeList.columns[0]].unique()
	def VerifyInfoID(record):
		if type(record['informationID']) == str:
			if len(record['informationID']) > 0 and record['informationID'][0] == '[' :
				return 1
			else:
				return 0
		return 1
	
	unknownInfoIds = {}
	def ValidateInfoID(record):
		if type(record['informationID']) == str:
			if not (record['informationID'] in set_of_nodeids):
				unknownInfoIds[record['informationID']] = 1
				return 1
		return 0
	
	temp = originalData['informationID'].unique().shape[0]
	print('\t\t\t Unique InfoID count : \t' + str(temp))
	thislog['informationID_uidc'] = temp
	temp = originalData.loc[originalData['informationID'] == '-1.0'].shape[0]
	print('\t\t\t -1.0 Count : \t' + str(temp))
	thislog['informationID_n1c'] = temp
	temp = originalData.apply(lambda x: VerifyInfoID(x), axis = 1).sum()
	print('\t\t\t Verification Failed InfoID Count : \t' + str(temp))
	thislog['informationID_vmic'] = temp
	temp = originalData.apply(lambda x: ValidateInfoID(x), axis = 1).sum()
	print('\t\t\t Validation Failed InfoID Count : \t' + str(temp))
	print('\t\t\t Unknown InfoIDs : ' + str(len(unknownInfoIds.keys())))
	thislog['informationID_mic'] = temp
	thislog['informationID_uiidc'] = len(unknownInfoIds.keys())
	thislog['informationID_uiids'] = unknownInfoIds.keys()

	print('\t\t platform')
	temp = originalData.loc[originalData['platform'] == '-1.0'].shape[0]
	print('\t\t\t -1.0 Count : \t' + str(temp))
	thislog['platform_n1c'] = temp
	temp = originalData.loc[ (originalData['platform'] != 'github') & (originalData['platform'] != 'reddit') & (originalData['platform'] != 'twitter') & (originalData['platform'] != 'telegram') & (originalData['platform'] != 'youtube')].shape[0]
	print('\t\t\t Mismatch platform Count : \t' + str(temp) )
	thislog['platform_mpc'] = temp

	print('\t\t has_URL')
	temp = originalData.loc[(originalData['has_URL'] != 0) & (originalData['has_URL'] != 1)].shape[0]
	print('\t\t\t not 1 or 0 Count : \t' + str(temp))
	thislog['has_URL'] = temp

	print('\t\t links_to_external')
	temp = originalData.loc[(originalData['links_to_external'] != 0) & (originalData['links_to_external'] != 1)].shape[0]
	print('\t\t\t not 1 or 0 Count : \t' + str(temp))
	thislog['links_to_external'] = temp

	print('\t\t domain_linked')
	temp = originalData.loc[originalData['domain_linked'] == '-1.0'].shape[0]
	print('\t\t\t -1.0 Count : \t' + str(temp))
	thislog['domain_linked'] = temp

	print('\twriting output files...')
	# Write Weird 1st line !!!
	TheFirstLine = '{"identifier": "' + IdentifierStr + '", "team": "ucf-garibay", "scenario": "'+ str(ScenarioNo) + '" }\n'
	with open(file_eventLog,"w") as f:
		f.write(TheFirstLine)

	# Write The Events
	with open(file_eventLog,"a") as f: 
		originalData.to_json(f,orient='records',lines=True)

	#-----------------------
	x = { \
		'time_executed' : thisDT.strftime("%m/%d/%Y %H:%M:%S:%f"), \
		'variables' : [ \
			{\
				'name':'Scenario', \
				'value': str(ScenarioNo) \
			},
			{\
				'name':'commit.sha', \
				'value': str(CommitSha) \
			},
			{\
				'name':'start.time', \
				'value': str(Sim_StartTime) \
			},
			{\
				'name':'end.time', \
				'value': str(Sim_EndTime) \
			},
			{\
				'name':'group.description', \
				'value': str(GroupDesc) \
			},
			{\
				'name':'run.group', \
				'value': str(RunGroup) \
			},
			{\
				'name':'run.by', \
				'value': str(RunBy) \
			},
			{\
				'name':'run.number', \
				'value': str(RunNumber) \
			},
			{\
				'name':'run.type', \
				'value': 'single' # Options: 'single', 'bspace', 'bsearch', 'other' \
			},
			{\
				'name':'platform', \
				'value': 'python' \
			},
			{\
				'name':'model_name', \
				'value': IdentifierStr \
			},
			{\
				'name':'original_output_file', \
				'value': str(file_csv_eventlog) \
			},
			{\
				'name':'original_output_file_S3Loc', \
				'value': str(file_csv_S3Location) \
			},
			{\
				'name':'model_MemoryDepth', \
				'value': str(Model_MemoryDepth) \
			},
			{\
				'name':'model_OverloadFactor', \
				'value': str(Model_OverloadFactor) \
			},
		], \
		'model_name' : IdentifierStr \
		}

	with open(file_metadata,'w') as f:
		json.dump(x,f,indent=4)

	print("\nOutput Files:")
	print("\t" + file_eventLog)
	print("\t" + file_metadata)

	thislog['eventlogjson'] = file_eventLog
	thislog['mynote'] = mynote
	dfMainLog = dfMainLog.append(thislog, ignore_index=True)

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Please provide parameter file path as a command line argument.")
		sys.exit()
	params = Parameters(sys.argv[1])
	MultiRun(params)
