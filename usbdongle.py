import json

class LeweiUsbDongle(object):

    dongleName = "UNKNOWN"
    dongleType = None
    dongleDataLength = 16

    def __init__(self, dataAddress):
        self.dongleType = dataAddress
        if(self.dongleType == '\x90\x01'):
            self.dongleName = "HT DEVICE"
            self.dongleDataLength = 2
        
    def hexShow(self,argv):  
        result = ''  
        hLen = len(argv)  
        for i in xrange(hLen):  
            hvol = ord(argv[i])
            hhex = '%02x'%hvol  
            result += hhex  
        print 'hexShow:',result
        return result


    def hexToOct(self,argv):
        result = 0
        hLen = len(argv)
        for i in xrange(hLen):
            result = result*256+ ord(argv[i])
        return result
    
    def dealHT(self,framedata):
        #print "Get datavalues from frame"
        humidityVal = (ord(framedata[0])*256+ord(framedata[1]))*0.1
        print humidityVal
        temperatureVal = (ord(framedata[2])*256+ord(framedata[3]))*0.1
        print temperatureVal

        #define 'temperature,humidity' as name in Lewei50.com
        if(humidityVal > 0):
            sensor1={"Name":"temperature","Value":str(temperatureVal)}
            sensor2={"Name":"humidity","Value":str(humidityVal)}
            lst_data=[]
            lst_data.append(sensor1)
            lst_data.append(sensor2)
            userData=json.dumps(lst_data)
            #print (api_url)
            #res=PostData(apiUrl,userKey,usrData)
            return userData
            
    def handleData(self,framedata):
        data = ""
        if(self.dongleType == '\x90\x01'):
            data = self.dealHT(framedata)
        print 'finished processing for device:'+self.dongleName
        return data

