import minimalmodbus
import httplib2
import time
import os
import re
import json
import serial

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
            errLog.close()
            time.sleep(10)
            os.system('reboot')
        else :
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
    apiUrlUploadData="http://rs.api.lewei50.com/api/v1/gateway/updatesensors/"+gatewayNo
    apiUrlUploadLog = "http://rs.api.lewei50.com/api/V1/gateway/updatelog/"+gatewayNo
else:
    apiUrlUploadData="http://rs.api.lewei50.com/api/v1/gateway/updatesensorsbysn/"+sn
    apiUrlUploadLog = "http://rs.api.lewei50.com/api/V1/gateway/updatelogbysn/"+sn
'''
set default api
'''
apiUrl = apiUrlUploadData

'''
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
                    try :
                        usbDongle = usbdongle.LeweiUsbDongle("UNKNOWN")
                        result = usbDongle.detectType(fn)
                    except:   
                        print "found error"
                        errDetect()
                        pass
                    if(result):
                        print "detected:"+usbDongle.dongleName
                        if (usbDongle.dongleName == "MCLoger"):
                            apiUrl = apiUrlUploadLog
                        else :
                            apiUrl = apiUrlUploadData
                        try:
                            res=PostData(apiUrl,userKey,result)
                            time.sleep(10)
                        except:
                            print "send fail,check your network"
                            pass
                    
                    pass

                
except Exception,e:   
    print Exception,":",e
    pass
'''
    
def dealframe(framedata):
    framedata = framedata.replace("\x0a","")
    """Get datavalues from frame"""
    hexShow(framedata)
    result = False
    pattern = re.compile(r'(.*)\x00')
    match = pattern.match(framedata)
    if match:
        try:
            result = match.group()
            print "found log data :"+result
            sensor1={"Message":str(result.decode('gbk').encode('utf-8')).replace("\x00","")}
            userData=json.dumps(sensor1)
            print userData
            result = userData
            if(result):
                apiUrl = apiUrlUploadLog
                print "try to send to "+apiUrl
                try:
                    res=PostData(apiUrl,userKey,result)
                except:
                    print "send fail,check your network"
                print "send ok"
                pass
        except:
            print "something wrong with dealing data"

def run(svr_status):
    """run forever"""
    ser=None
    serial_port="/dev/ttyUSB0"
    #serial_port=24
    serial_timeout=3
    #cmds="\xf0\x80\x80"


    while 1:
        #time.sleep(1)
        #log(json.dumps(svr_status))
        ##if service is stopped then break to stop
        try :
            if ser is None:
                ser=serial.Serial(port=serial_port, baudrate=9600, bytesize=8, parity="N", stopbits=1, xonxoff=0)
                ser.setTimeout(serial_timeout)
            #n = ser.inWaiting()
            #if n: 
            #    ser.read(n)
            #ser.write(cmds)
            #read the frame which is sended by self
            #ser.read(len(cmds))
            time.sleep(3) 
            n = ser.inWaiting()
            #recive the response from device
            recv=""
            if (n > 0):
                print "buffer: " + str(n)
                recv=ser.read(n)
                #ser.flushInput()
                ser.close()
                dealframe(recv)
                try :
                    ser.close()
                    #break
                except Exception,ex:
                    #print ex
                    #log(ex.message)
                    pass
                    
                ser=None
            #dealframe(framedata)
        except serial.serialutil.SerialException,e:
            #print "serial->",e
            #log(e.message)
            if 1:
                try :
                    #ser.flushInput()
                    ser.close()
                except Exception,ex:
                    #print ex
                    #log(ex.message)
                    pass
                    
                ser=None
            pass
        except Exception,e:
            #print e
            #log(e.message)
            pass

if __name__ == "__main__":
    print "starting monitor"
    run(0)
