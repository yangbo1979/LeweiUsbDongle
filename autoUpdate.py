import json
import httplib2
import base64
import ConfigParser
import time

def GetData(url,data):
    """"Post the user_data to api_url with user_key"""
    http=httplib2.Http()
    headers={"User-Agent":"PythonRobot"}
    resp,content=http.request(url,'GET',headers=headers,body=data)
    return (resp,content)

time.sleep(5)

cf = ConfigParser.ConfigParser()

cf.read("autoUpdate.conf")

server = cf.options("server")
files = cf.options("files")

if (cf.get("global","enable") == "0"):
    exit()

for fileId in files:
    fileName = cf.get("files",fileId)
    fileUrl = cf.get("server","host")+fileName
    print "checking:"+fileUrl

    userData=""
    try:
        
        res,content=GetData(fileUrl,userData)

        attrList = json.loads(content)
        sha = attrList['sha']
        try:
            currentSha = cf.get("version",fileName)
        except:
            currentSha = ""
        if(sha != currentSha):
            print 'updating...\n'
            code= attrList['content']
            fileContent = base64.decodestring(code)
            output = open(fileName, 'w')
            output.write(fileContent)
            cf.set("version",fileName, sha)
            cf.write(open("autoUpdate.conf", "w"))
            print "finished!"
        else:
            print "same version!\n"

    except:
        pass
