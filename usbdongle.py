from __future__ import division
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
        if(self.dongleType == '\x90\x02'):
            self.dongleName = "DUST DETECT DEVICE"
            self.dongleDataLength = 4
        
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
        #print humidityVal
        temperatureVal = (ord(framedata[2])*256+ord(framedata[3]))*0.1
        #print temperatureVal

        #define 'temperature,humidity' as name in Lewei50.com
        if(humidityVal > 0):
            sensor1={"Name":"temperature","Value":str(temperatureVal)}
            sensor2={"Name":"humidity","Value":str(humidityVal)}            
            print "temperature:"+str(temperatureVal)
            print "humidity:"+str(humidityVal) 
            lst_data=[]
            lst_data.append(sensor1)
            lst_data.append(sensor2)
            userData=json.dumps(lst_data)
            #print (api_url)
            #res=PostData(apiUrl,userKey,usrData)
            return userData
        
    def dealDust(self,framedata):
        #print "Get datavalues from frame"
        humidityVal = (ord(framedata[0])*256+ord(framedata[1]))*0.1
        #print humidityVal
        temperatureVal = (ord(framedata[2])*256+ord(framedata[3]))*0.1
        if(temperatureVal >= 32768):
            temperatureVal = temperatureVal -65536
        #print temperatureVal
        vOut = (ord(framedata[4])*256+ord(framedata[5]))/1024*5
        K = 0.17*1000
        dustDensity = 0.56 * 1000
        if(vOut > 3.25):
            dustDensity = 0.56* 1000
            dustDensity = 0
        elif(vOut < 0):
            dustDensity = 0
        else :
            dustDensity = vOut * K
        dustDensity = int(dustDensity)
        #print "dustDensity:"+str(dustDensity)
        pressureVal = (ord(framedata[6])*256+ord(framedata[7]))*0.1
        #print pressureVal

        #define 'temperature,humidity' as name in Lewei50.com.
        lst_data=[]
        if(humidityVal > 0 and humidityVal != 200):
            sensor1={"Name":"temperature","Value":str(temperatureVal)}
            sensor2={"Name":"humidity","Value":str(humidityVal)}
            lst_data.append(sensor1)
            lst_data.append(sensor2)
            print "temperature:"+str(temperatureVal)
            print "humidity:"+str(humidityVal)            
        if(dustDensity > 0):
            sensor3={"Name":"dust","Value":str(dustDensity)}
            lst_data.append(sensor3)
            print "dust:"+str(dustDensity)
        if(pressureVal > 0):
            sensor4={"Name":"pressure","Value":str(pressureVal)}
            lst_data.append(sensor4)
            print "pressure:"+str(pressureVal)
            
        userData=json.dumps(lst_data)
            #print (api_url)
            #res=PostData(apiUrl,userKey,usrData)
            #return ""
        return userData
            
    def handleData(self,framedata):
        data = ""
        if(self.dongleType == '\x90\x01'):
            data = self.dealHT(framedata)
        if(self.dongleType == '\x90\x02'):
            data = self.dealDust(framedata)
        print 'finished processing for device:'+self.dongleName
        return data

