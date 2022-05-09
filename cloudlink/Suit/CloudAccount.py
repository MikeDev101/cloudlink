import cloudlink
import os
from pathlib import Path
import bcrypt
import json
from functools import wraps

class CloudAccount():
	"""
	CloudAccount a Cloudlink Extention
		A basic Account System for Cloudlink servers
	
	"""
	
	def __init__(self,_cloudlink:cloudlink.CloudLink):
		self._cloudlink = _cloudlink
		
		#injecting Error Codes
		
		self._cloudlink.codes["CA_AuthError"] = "%CA% E: 1 | Error With Auth"
		self._cloudlink.codes["CA_SignInError"] = "%CA% E: 2 | Problom With Signing in"
		self._cloudlink.codes["CA_AccountCreatonError"] = "%CA% E: 3 | Error With Makeing account"
	
	
	def server(self):
		"""

		Initiate Server Mode For CloudAccount!
		
		"""
		self._file = CA_FILESYS(self._cloudlink)
		self.mode = "SERVER"
		self.authed_users = {}


		
		#makeig Callbacks
		self.callbacks = {}
		self._cloudlink.callback("on_packet",self._CA_PKT_HDL)
		
	def callback(self, callback_id, function): # Add user-friendly callbacks for CloudLink to be useful as a module
		if callback_id in ["on_login","on_acc_creation","on_acc_deletion","on_logout"]:
			self.callbacks[callback_id] = function
		elif not callback_id in ["on_packet"]:	
	   		self._cloudlink.callback(callback_id,function)
		else:
		   self.callbacks[callback_id] = function
			
	def _CA_PKT_HDL(self,cmd:dict):
		"""
		CloudAccount Packet Handler
		"""
		#{"cmd": msg["val"]["cmd"], "val": msg["val"]["val"], "id": origin}

		cmd1 = cmd["cmd"]
		val = cmd["val"]
		_username = cmd["id"]
		user = self._cloudlink._get_obj_of_username(_username)
		if cmd1.startswith("CA_"):
			if cmd1 == "CA_CREATE":
				self._file.create_acct(_username,val.encode())
			elif cmd1 == "CA_SIGNIN":
				hashed,username= self._file.get_user_data(_username)

				if bcrypt.checkpw(val.encode(),hashed):
					self.authed_users[_username] = user
				
			
				raise NotImplementedError
		
		
		elif self.callbacks.get("on_packet"):
			self.callbacks["on_packet"](cmd)
	def create_account(self,pswd,username):
		return self._cloudlink.sendPacket({
			"cmd": "CA_CREATE",
		 	"val": pswd,
		 	"id": username
		})
	def AuthRequired(self,function):
		@wraps(function)
		def inner(user,*args,**kwargs):
			if self._cloudlink._get_username_of_obj(user) in self.authed_users.keys():
				function(*args,**kwargs)
			else:
				return
		return inner
				
class CA_FILESYS():
	def __init__(self,cl):
		self.base_dir = f"{os.getcwd()}/CloudData/"
		self._cl = cl
		
		
		base_dir_path = Path(self.base_dir)
		base_dir_path.mkdir(parents=True, exist_ok=True)

		
	def create_acct(self,_username,val):
		"""
		creates an accnt for a user
		"""
		user_path = f"{self.base_dir}/user_{_username}_done/"
		Path(user_path).mkdir(parents=True, exist_ok=True)

		user_accnt = Path(f'{user_path}/account.json')
		user_accnt.touch(exist_ok=False)


		hashed = bcrypt.hashpw(val,bcrypt.gensalt())

		
		user_data = {
			"HashedPw":str(hashed),
			"username":_username
		}

		with user_accnt.open(mode="w") as f:
			json.dump(user_data,f)

	def get_user_data(self,_username):
		with Path(f"{self.base_dir}/user_{_username}_done/account.json").open() as f:
			tmp = json.load(f)

		return tmp["HashedPw"],tmp["username"]

if __name__ == "__main__":
	import cloudlink

	cl = cloudlink.CloudLink(debug=True)

	CA = CloudAccount(cl)

	def callback(cmd_dict:dict):
		return

	CA.callback("on_packet",callback)
	

	CA._CA_PKT_HDL(
		{
		 "cmd": "CA_CREATE",
		 "val": 'password', 
		 "id": ''
		}
	)
	