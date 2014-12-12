import minimalmodbus
import httplib2
import time
import os

import usbdongle


global sn
global gatewayNo
global userKey
global enableSn
sn = ''
#change here
gatewayNo = '01'
#change here
userKey = 'not_fill_your_apikey_here,will_read_from_config_file'
enableSn = '0'

def hexShow(argv):  
    result = ''  
    hLen = len(argv)  
    for i in xrange(hLen):  
        hvol = ord(argv[i])
        hhex = '%02x'%hvol  
        result += hhex  
    print 'hexShow:',result
    return result

def hexToOct(argv):
    result = 0
    hLen = len(argv)
    for i in xrange(hLen):
        result = result*256+ ord(argv[i])
    return result

'''
get config from system config
run in linux only
'''
def getConfig():
    for line in open("/etc/config/sn"):
        paraDetail = line.split(' ')
        try:
            if(paraDetail[1]=="sn"):
                global sn
                sn = paraDetail[2][1:-2]
            elif(paraDetail[1]=="userkey"):
                global userKey
                userKey = paraDetail[2][1:-2]
            elif(paraDetail[1]=="gateway"):
                global gatewayNo
                gatewayNo= paraDetail[2][1:-2]
            elif(paraDetail[1]=="enableSn"):
                global enableSn
                enableSn= paraDetail[2][1:-2]
        except Exception,e:
            pass

def PostData(url,usrkey,data):
    """"Post the user_data to api_url with user_key"""
    http=httplib2.Http()
    headers={"userkey":usrkey}
    resp,content=http.request(url,'POST',headers=headers,body=data)
    return (resp,content)

        
def errDetect():
    errLog = open('/lewei50/error.txt')
    try:
        errTimes = errLog.readline()
        print 'error times:'
        print errTimes
        if(errTimes ==''):
            errTimes = '0'
        print errTimes
        print 'try to reset usb'
        os.system('echo 0 > /sys/devices/virtual/gpio/gpio8/value;sleep 2;echo 1 > /sys/devices/virtual/gpio/gpio8/value')
        print 'done'
        errLog = open('/lewei50/error.txt','w')
        if(int(errTimes) > 20) :
            errLog.write('0')
            time.sleep(5)
            os.system('reboot')
        errLog.write(str(int(errTimes)+1))
    except Exception,e:
        print e
    finally:
        errLog.close()
    #log(e.message)
    pass
    
try :
    getConfig()
except:
    pass



        
'''
select api address
'''
if(enableSn == '0'):
    apiUrl="http://open.lewei50.com/api/v1/gateway/updatesensors/"+gatewayNo
else:
    apiUrl="http://open.lewei50.com/api/v1/gateway/updatesensorsbysn/"+sn


try:
    rdir = "/dev/"
    for parent, dirnames, filenames in os.walk(rdir):
        for fn in filenames:
            if(fn.find("USB")>0):
                print "Communicating with:"+fn
                instrument = minimalmodbus.Instrument('/dev/'+fn, 1)
                # port name, slave address
                # use '/dev/ttyUSB0' in linux and number-1 in windows system,here is 36

                try:
                    deviceType = instrument.read_string(80,1)
                    hexShow(deviceType)
                    usbDongle = usbdongle.LeweiUsbDongle(deviceType)

                    
                    ## Read temperature (PV = ProcessValue)
                    ## \x9001 is 36865
                    dgData = instrument.read_string(hexToOct(usbDongle.dongleType),usbDongle.dongleDataLength)
                    # Registernumber, number of decimalsprint temperature

                    hexShow(dgData)
                        
                    userData = usbDongle.handleData(dgData)
                    try:
                        res=PostData(apiUrl,userKey,userData)
                        time.sleep(10)
                    except:
                        print "send fail,check your network"
                        pass
                except ValueError,e:
                    print Exception,":",e
                    pass

                
except Exception,e:   
    print Exception,":",e   
    print "found error"
    errDetect()
    pass
