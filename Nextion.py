import serial
import serial.tools.list_ports
import time

interaction = {'None': 0,
               'SuccessOnly': 1,
               'FailOnly': 2,
               'Always': 3}

COLORS = {'RED': 63488,
          'BLUE': 31,
          'GRAY': 33840,
          'BLACK': 0,
          'WHITE': 65535,
          'GREEN': 2016,
          'BROWN': 48192,
          'YELLOW': 65504}

SUPPORT_BAUD_RATES = [2400, 4800,
                      9600, 19200,
                      38400, 57600,
                      115200]

RESPONSE = {0x00 : 'Invalid Instruction',
            0x01 : 'Successful Execution',
            0x03 : 'Page ID Invalid',
            0x04 : 'Picture ID Invalid',
            0x05 : 'Font ID Invalid',
            0x11 : 'Baud Rate Setting Invalid',
            0x12 : 'Curve Control Invalid',
            0x1A : 'Variable Name Invalid',
            0x1B : 'Variable Operation Invalid',
            0x1C : 'Failed to Assign',
            0x1D : 'PERFROM Failed',
            0x1E : 'Invalid Parameter Quantity',
            0x1F : 'IO Operation Failed'}

TERMINATOR = bytearray([0xFF, 0xFF, 0xFF])

def serialInit(baud):
    s = serial.Serial()
    s.port = 'COM5'
    s.baudrate = baud
    s.open()
    return s

class NextionUI(list):
    def __init__(self, port, pages, bkcmd = False):
        self.port = port
        self.port.timeout = 0.100
        self.pages = pages
        for p in self.pages:
            p.port = self.port
            for c in p.controls:
                c.port = self.port

        if(bkcmd == True or bkcmd == False):
            self.bkcmd = bkcmd
            self.port.write('bkcmd=' + str(3*int(bkcmd)))
            self.port.write(TERMINATOR)

    def checkResponse(self):
        if(bkcmd == False):
            return True
        response = self.port.read(4)
        if(response[0] != 0x01):
            return False
        else:
            return True

    def addPage(self, page):
        self.pages.append(page)
        self.page.port = self.port
        return True
    
    def setBaud(self, baud):
        if baud not in SUPPORTED_BAUD_RATES:
            return
        self.port.write('baud=' + str(baud))
        self.port.write(TERMINATOR)

    def setDefaultBaud(self, defBaud):
        self.port.write('bauds=' + str(defBaud))
        self.port.write(TERMINATOR)
        
    def setBrightness(self, value):
        self.port.write('dim=' + str(value))
        self.port.write(TERMINATOR)

    def setDefaultBrightness(self, value):
        self.port.write('dims=' + str(value))
        self.port.write(TERMINATOR)

    def setHorizontalSpacing(self, value):
        self.port.write('spax=' + str(value))
        self.port.write(TERMINATOR)

    def setVeritcalSpacing(self, value):
        self.port.write('spay=' + str(value))
        self.port.write(TERMINATOR)

    def setTouchDrawingColor(self, color):
        if(COLORS.get(color, False) != False):
            self.port.write('thc=' + str(colors[color]))
            self.port.write(TERMINATOR)

    def setTouchDrawingEnable(self, state):
        if(state == True or state == False):
            self.port.write('thdra=' + str(int(state)))
            self.port.write(TERMINATOR)

    def setTouchCoordinateEnable(self, state):
        if(state == True or state == False):
            self.port.write('sendxy=' + str(int(state)))
            self.port.write(TERMINATOR)

    def doDelay(self, milliseconds):
        if(milliseconds < 65536):
            self.port.write('Delay=' + str(milliseconds))
            self.port.write(TERMINATOR)

    def setSleep(self, state):
        if(state == True or state == False):
            self.port.write('sleep=' + str(int(state)))
            self.port.write(TERMINATOR)

    def setInteractive(self, interactive):
        self.port.write('bkcmd=' + str(interaction.get(interactive, 0)))
        self.port.write(TERMINATOR)

    def setPage(self, page):
        self.port.write('page ' + str(page))
        self.port.write(TERMINATOR)

    def getCurrentPage(self):
        self.port.write('sendme')
        self.port.write(TERMINATOR)
        response = bytearray(self.port.read(5))
        if(response[0] != 0x66):
            return False
        else:
            return response[1]

    def calibrateTouch(self):
        self.port.write('touch_j')
        self.port.write(TERMINATOR)

    def setRefresh(self, state):
        if(state == False):
            self.port.write('ref_stop')
            self.port.write(TERMINATOR)
        elif(state == True):
            self.port.write('ref_star')
            self.port.write(TERMINATOR)

    def setCommandExecution(state):
        if(state == False):
            self.port.write('com_stop')
            self.port.write(TERMINATOR)
        elif(state == True):
            self.port.write('com_star')
            self.port.write(TERMINATOR)

    def clearCommandBuffer(self):
        self.port.write('code_c')
        self.port.write(TERMINATOR)

    def reset(self):
        self.port.write('rest')
        self.port.write(TERMINATOR)
        

class NextionPage(list):
    def __init__(self, ID, controls):
        self.port = None
        self.id = ID
        self.controls = []
        for c in controls:
            self.controls.append(c)

    def setPort(self, port):
        self.port = port
        return True

    def addControl(self, control):
        self.controls.append(control)
        control.port = self.port
        return True

    
class NextionControl(object):
    def __init__(self, name, ID):
        self.port = None
        self.name = name
        self.id = ID

    def setPort(self, port):
        self.port = port
        return True

    def refresh(self):
        self.port.write('ref ' + self.name)
        self.port.write(TERMINATOR)

    def setVisible(self, state):
        if(state == True or state == False):
            self.port.write('vis ' + self.name + ',' + str(int(state)))
            self.port.write(TERMINATOR)
            
    def performTouchPress(self):
        self.port.write('click ' + self.name + ',0')
        self.port.write(TERMINATOR)
        
    def performTouchRelease(self):
        self.port.write('click ' + self.name + ',1')
        self.port.write(TERMINATOR)

    def setTouchEnable(self, state):
        if(state == True or state == False):
            self.port.write('tsw ' + self.name + ',' + str(int(state)))
            self.port.write(TERMINATOR)

    def getParameter(self):
        stx = self.port.read(1)
        if(stx != chr(0x71) and stx != chr(0x70)):
            return []
        count = 0
        response = []
        while(count < 3):
            rxdata = ord(self.port.read(1))
            response.append(rxdata)
            if(rxdata == 0xFF):
                count = count + 1
            else:
                count = 0
        response = response[0:len(response)-3]
        return response

    def getTxt(self):
        self.port.reset_input_buffer()
        self.port.write('get ' + self.name + '.txt')
        self.port.write(TERMINATOR)
        response = self.getParameter()
        txt = ''
        for c in response:
            txt += chr(c)
        return txt
    
    def getVal(self):
        self.port.reset_input_buffer()
        self.port.write('get ' + self.name + '.val')
        self.port.write(TERMINATOR)
        response = self.getParameter()
        response.reverse()
        val = 0
        for i in response:
            val = val << 8
            val = val | i
        return val

    def getFontColor(self):
        self.port.reset_input_buffer()
        self.port.write('get ' + self.name + '.pco')
        self.port.write(TERMINATOR)
        response = self.getParameter()
        response.reverse()
        color = 0
        for i in response:
            color = color << 8
            color = color | i
        return color

    def getBacgroundColor(self):
        self.port.reset_input_buffer()
        self.port.write('get ' + self.name + '.bco')
        self.port.write(TERMINATOR)
        response = self.getParameter()
        response.reverse()
        color = 0
        for i in response:
            color = color << 8
            color = color | i
        return color

    def getPic(self):
        self.port.reset_input_buffer()
        self.port.write('get ' + self.name + '.pic')
        self.port.write(TERMINATOR)
        response = self.getParameter()
        response.reverse()
        pic = 0
        for i in response:
            pic = pic << 8
            pic = pic | i
        return pic

    def setTxt(self, txt):
        self.port.write(self.name + '.txt=\"' + txt + '\"')
        self.port.write(TERMINATOR)

    def setVal(self, val):
        self.port.write(self.name + '.val=' + str(val))
        self.port.write(TERMINATOR)

    def setFontColor(self, color):
        if(COLORS.get(color, False) != False):
            self.port.write(self.name + '.pco=' + str(COLORS[color]))
            self.port.write(TERMINATOR)

    def setBackgroundColor(self, color):
        if(COLORS.get(color, False) != False):
            self.port.write(self.name + '.bco=' + str(COLORS[color]))
            self.port.write(TERMINATOR)

    def setPic(self, picID):
        self.port.write(self.name + '.pic=' + str(picID))
        self.port.write(TERMINATOR)

class customGauge(NextionControl):
    def __init__(self, name, ID):
        self.port = None
        self.name = name
        self.id = ID
        
        self.offset = 0
        self.total = 10
        self.min_val = 0
        self.max_val = 100

        self.label = None

    def setValue(self, value):
        picID = int((value)/((self.max_val-self.min_val)/(self.total))) + self.offset
        if(picID > self.offset + self.total-1):
            picID = self.offset + self.total-1
        self.setPic(picID)
        self.setTxt(str(value))

    def addLabel(self, label):
        self.label = label
        self.label.port = self.port

    def setLabel(self, name):
        if(self.label != None):
            self.label.setTxt(name)

##g0 = customGauge('g0', 1)
##g0.total = 20
##g0.setPort(serialInit(1))
##gl0 = NextionControl('gl0', 4);
##g0.addLabel(gl0)
