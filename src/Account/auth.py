import random
import string
from time import sleep
import requests

def createCode(size: int) -> str:
	return "".join(random.SystemRandom().choices(string.digits, k = size))

def verifyCode(username: str, code: str, projectid: int, limit: int) -> bool:
  try:
    cloudData = requests.get("https://clouddata.scratch.mit.edu/logs", params = {"projectid": projectid, "limit": limit, "offset": 0}).json()

    for entry in cloudData:
      if (entry["verb"] == "set_var" and entry["name"] == "☁ AUTH" and entry["user"] == username):
        if entry['value'] == code: 
          return True
        else:
          return False
    return False
  except Exception as e:
    print("[ ! ] Authenticator error! ", str(e))
    return False

if __name__ == "__main__":
  uname = str(input("What is your username? "))
  vcode = createCode(6)
  print("Your code is:", str(vcode), "\nWaiting for you to enter the code in the CloudLink Authenticator (See https://www.scratch.mit.edu/projects/471271065/)...")
  done = False
  while not done:
    done = verifyCode(uname, vcode, 471271065, 1)
    if not done:
      sleep(0.5)
  print("You are verified!")
