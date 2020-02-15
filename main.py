# EARLgrey
# Easily Accessible Routine Language

import math, random, string
from cmu_112_graphics import *
from tkinter import *
from tkinter import simpledialog
import functools

commandLines = []
VarLibrary = {}
originals = {"add","sub","mul","div","pow","mod","log","sin","cos","tan","less","equal","greater",
"abs","round","uni","chr","upper","lower","concat","size","split","branch","or","and","not",
"link","get","slice","inside","count","subset","range","join","index","map","keep","merge",
"sort","min","max","def"}

def getEARLgreyFiles(): # Searches through the current directory tto find Kimchi files
    return list(filter(lambda x: x[-7:] == '.eg.txt',os.listdir(os.getcwd())))

def wipeVarLibrary():
    for name in list(VarLibrary.keys()):
        if name not in originals:
            del VarLibrary[name]

def formatTypes(argsList):
    out = []
    for arg in argsList:
        if arg == Number: out.append('N')
        if arg == Vocab: out.append('V')
        if arg == Union: out.append('U')
        if arg == Logic: out.append('L')
        if arg == Transform: out.append('T')
        if arg == None: out.append('?')
    return ",".join(out)

class MainScreen(Mode): # The main interface
    def modeActivated(self): # When activated, discard the graphics-file canvas
        self.app._canvas.pack_forget()
        self.canvas = Canvas(self.app._root,width=1000,height=800)
        self.canvas.pack()
        self.cursorIndex = 0
        self.adjustText()

    def appStarted(self):
        self.terminalWidth = 620
        self.fontSize = 20
        self.scrollY = 20
        self.displayLines = []
        self.consoleLog = []

    def keyPressed(self,event):
        global commandLines
        if event.key == 'Escape': return
        elif event.key == "Delete":
            if len(commandLines) == 0: return
            if len(commandLines) > 1 and commandLines[self.cursorIndex-1] == ' ':
                while commandLines[self.cursorIndex-1] == ' ':
                    commandLines.pop(self.cursorIndex-1)
                    self.cursorIndex -= 1
            else:
                commandLines.pop(self.cursorIndex-1)
                self.cursorIndex -= 1
        elif event.key == "Left": self.cursorIndex -= 1
        elif event.key == "Right": self.cursorIndex += 1
        elif event.key == "Up": self.cursorIndex -= int(2 * self.terminalWidth / self.fontSize - 5)
        elif event.key == "Down": self.cursorIndex += int(2 * self.terminalWidth / self.fontSize - 5)
        else:
            if event.key == "Space": 
                commandLines.insert(self.cursorIndex,' ')
                self.cursorIndex += 1
            elif event.key == "Tab": 
                for i in range(3):
                    commandLines.insert(self.cursorIndex,' ')
                self.cursorIndex += 3
            elif event.key == "Enter": 
                commandLines.insert(self.cursorIndex,' ')
                self.cursorIndex += 1
                while len(commandLines) % int(2 * self.terminalWidth / self.fontSize - 5) != 0:
                    commandLines.insert(self.cursorIndex,' ')
                    self.cursorIndex += 1
                commandLines.pop()
                self.cursorIndex -= 1
            else: 
                commandLines = commandLines[:self.cursorIndex] + [event.key] + commandLines[self.cursorIndex:]
                self.cursorIndex += 1
        self.cursorIndex = max(min(self.cursorIndex,(len(commandLines))),0)
        self.adjustText()

    def adjustText(self):
        displayText = []
        modified = commandLines[:self.cursorIndex] + ['|'] + commandLines[self.cursorIndex:]
        rowLen = int(2 * self.terminalWidth / self.fontSize - 5)
        row = []
        for i in range(len(modified)):
            char = modified[i]
            row.append(char)
            if len(row) >= rowLen - 1 or i == len(modified)-1:
                displayText.append(row)
                row = []
        self.displayLines = displayText
        
    def modeDeactivated(self): # When deactivated, re-impose the graphics-file canvas
        self.canvas.pack_forget()
        self.app._canvas.pack()

    def checkSyntax(self,code):
        pars = 0
        try:
            for char in code:
                if char == '(': pars += 1
                elif char == ')': pars -= 1
                if char == ';' and pars != 0: raise SyntaxError("Unbalanced parenthesis")
                if pars < 0: raise SyntaxError("Unbalanced parenthesis")
            if ''.join(code).strip()[-1:] != ';': raise SyntaxError("Must end all lines with infix operator ;")
            return True
        except SyntaxError as e:
            self.consoleLog.insert(0,f"SyntaxError: {e}")
            return False

    def getLines(self):
        return [line.strip() for line in ''.join(commandLines).split(';')]

    def isNumber(self,line):
        if line.count('.') > 1: return False
        if line[0] == '-': return set(line[1:]) & set('0.123456789') == set(line[1:])
        return set(line) & set('0.123456789') == set(line)

    def isTransform(self,line):
        for var in VarLibrary:
            if type(VarLibrary[var]) == Transform:
                if line[:line.find('(')] == var:
                    return True

    def genesisString(self,line):
        left = line.find('=>')
        if left < 1: raise SyntaxError("Must have arguments before => operator")
        if line.count('=>') > 1: raise SyntaxError("Must have exactly 1 => operator in a definition")
        args = line[:left].strip()
        post = line[left+2:].strip()
        for var in VarLibrary:
            post = post.replace(var,f'VarLibrary["{var}"]')
        if '(' in post:
            post = post[:post.find('(')+1]+','.join(self.grabInputs(post,True,True))+')'
        function = eval(f'lambda {args}: {post}')
        return Transform(None,function,[None]*len(args.split(',')))

    def isUnion(self,line):
        if line[0] != '<' or line[-1] != '>': return False
        if '<' in line[1:-1] or '>' in line[1:-1]: raise SyntaxError("Unions may not contain unions (yet)")
        brackets = 0
        for char in line:
            if char == '<': brackets += 1
            elif char == '>': brackets -= 1
            if brackets < 0: raise SyntaxError("Unbalanced brackets")
        if brackets != 0: raise SyntaxError("Unbalanced brackets")
        return True

    def unionParse(self,line):
        out = []
        for item in line[1:-1].split(','):
            elem = item.strip()
            out += self.grabInputs(elem)
        print(Union(*out))
        return Union(*out)

    def typeVersion(self,line):
        out = []
        for i in line:
            if type(i) == Number: out.append(f'Number({i.value})')
            elif type(i) == Vocab: out.append(f'Vocab({i.value})')
            elif type(i) == Logic: out.append(f'Logic({i.value})')
            elif type(i) == Union: 
                Ustring = repr(i.values)
                out.append(f'Union({Ustring[1:-1]})')
            else: out.append(i)
        print('---->',out)
        return out

    def grabInputs(self,line,functionMode=True,ignoreMisc=False):
        out = []
        if functionMode:
            first = line.find('(')+1
            last = len(line)-line[::-1].find(')')-1
            operands = line[first:last].strip('(').strip(')').split(',')
        else: operands = [line]
        print(operands)
        for operand in operands:
            if operand in VarLibrary: out.append(VarLibrary[operand])
            elif self.isNumber(operand): out.append(Number(float(operand)))
            elif operand[0] == '"' and operand[-1] == '"': out.append(Vocab(operand))
            elif operand == 'TRUE': out.append(Logic(True))
            elif operand == 'FALSE': out.append(Logic(False))
            elif self.isTransform(operand): 
                print('>>',operand)
                inputs = self.grabInputs(operand)
                out.append(VarLibrary[operand[:operand.find('(')]](*inputs))
            elif self.isUnion(operand): out.append(self.unionParse(operand))
            elif not ignoreMisc: 
                raise SyntaxError(f"Unrecognized operand '{operand}'")
            else:
                out.append(operand)
        print(out)
        if ignoreMisc: 
            print(out)
            print(self.typeVersion(out))
            return self.typeVersion(out)
        return out

    def execute(self,line,i):
        try:
            if ':=' not in line and '$=' not in line: 
                raise SyntaxError("Must invoke assignment operators := or $= on each line")
            if line.count(':=') + line.count('$=') > 1: raise SyntaxError("Can only invoke assignment operator := once per line")
            functionDef = False if ':=' in line else True
            left, right = line.replace('$=',':=').split(':=')
            left = left.strip()
            if not left[:1].isalpha(): raise NameError(f"Variable names must start with a letter")
            if sum([left.count(i) for i in ' ,():=$']) != 0:
                raise NameError(f"[{i}] Variable names must be single words")
            right = right.strip()
            if left in VarLibrary: raise NameError(f"Name '{left}' already found")
            value = right
            if functionDef: VarLibrary[left] = self.genesisString(right)
            elif self.isNumber(right): VarLibrary[left] = Number(float(right))
            elif right in VarLibrary: VarLibrary[left] = VarLibrary[right]
            elif right[0] == '"' and right[-1] == '"': VarLibrary[left] = Vocab(right)
            elif right == "TRUE": VarLibrary[left] = Logic(True)
            elif right == "False": VarLibrary[left] = Logic(False)
            elif self.isTransform(right): 
                print('>>',left,right)
                inputs = self.grabInputs(right)
                function = VarLibrary[right[:right.find('(')]]
                VarLibrary[left] = function(*inputs)
            elif self.isUnion(right):
                VarLibrary[left] = self.unionParse(right)
            else: VarLibrary[left] = right
            self.consoleLog.insert(0,f'{left} := {VarLibrary[left]}')
            return True 
        except SyntaxError as e: self.consoleLog.insert(0,f"[{i}] SyntaxError: {e}")
        except TypeError as e: self.consoleLog.insert(0,f"[{i}] TypeError: {e}")
        except Exception as e: self.consoleLog.insert(0,f"[{i}] Error: {e}")
        return False

    def mousePressed(self,event):
        global commandLines
        if event.x > self.terminalWidth:
            if event.y < 30:
                wipeVarLibrary()
                syntax = self.checkSyntax(commandLines)
                if syntax:
                    parsed = self.getLines()
                    for i in range(len(parsed)):
                        if parsed[i] == '': continue
                        success = self.execute(parsed[i],i)
                        if not success: 
                            print("ERROR >> TERMINATION OF CODE")
                            return
            elif event.y < 60:
                EARLgrey.newSave()
            elif event.y < 90:
                self.consoleLog = []
                commandLines = []
            elif event.y > self.height-30:
                self.app.setActiveMode(self.app.home)
        self.adjustText()

    def drawTerminal(self,canvas):
        canvas.create_rectangle(20,0,self.terminalWidth,800,fill="Black")
        for i in range(len(self.displayLines)):
            canvas.create_text(30,self.scrollY+i*self.fontSize*1.1,text=''.join(self.displayLines[i]),fill="White",font=f'Futura {self.fontSize}',anchor='nw')

    def drawExecution(self,canvas):
        canvas.create_rectangle(self.terminalWidth+4,0,self.width,30,width=0,fill="#66dd99")
        canvas.create_text(self.terminalWidth/2+self.width/2,16,text="• RUN •",fill="White",font="Futura 20 bold")

    def drawSave(self,canvas):
        canvas.create_rectangle(self.terminalWidth+4,30,self.width,60,width=0,fill="#dd6666")
        canvas.create_text(self.terminalWidth/2+self.width/2,46,text="• SAVE •",fill="White",font="Futura 20 bold")

    def drawConsole(self,canvas):
        canvas.create_rectangle(self.terminalWidth+4,60,self.width,90,width=0,fill="#6699dd")
        canvas.create_text(self.terminalWidth/2+self.width/2,75,text="• CLEAR •",fill="White",font="Futura 20 bold")
        canvas.create_text(self.terminalWidth+5,95,text='\n'.join(self.consoleLog),font="Futura 12 bold",anchor='nw')

    def drawHome(self,canvas):
        canvas.create_rectangle(self.terminalWidth+4,self.height,self.width,self.height-32,width=0,fill="#996699")
        canvas.create_text(self.terminalWidth/2+self.width/2,self.height-17,text="• HOME •",fill="White",font="Futura 20 bold")

    def redrawAll(self,canvas):
        self.canvas.delete(ALL)
        self.drawTerminal(self.canvas)
        self.drawExecution(self.canvas)
        self.drawSave(self.canvas)
        self.drawConsole(self.canvas)
        self.drawHome(self.canvas)

class HomeScreen(Mode): # The colorful splash screen mode
    def modeActivated(self): # When activated, discard the graphics-file canvas
        self.app._canvas.pack_forget()
        self.canvas = Canvas(self.app._root,width=1000,height=800)
        self.canvas.pack()
        self.mX, self.mY = 0,0

    def appStarted(self):
        self.hoverColor = 'White'
        self.spin = 0
        self.timerDelay = 5
        
    def modeDeactivated(self): # When deactivated, re-impose the graphics-file canvas
        self.canvas.pack_forget()
        self.app._canvas.pack()    

    def mouseMoved(self,event): # Used to detect hovering over buttons
        self.mX, self.mY = event.x, event.y

    def mousePressed(self,event): # Is a buttton currently being pressed
        if event.x > 421 and event.x < 579:
            if event.y > 606 and event.y < 644: self.app.setActiveMode(self.app.main)
            elif event.y > 656 and event.y < 694: self.app.setActiveMode(self.app.load)
            #elif event.y > 706 and event.y < 744: self.app.setActiveMode(self.app.tutorialMode)

    def timerFired(self): # Increment the animation
        self.spin += 2.5
        red = int(85 * math.sin(2*math.pi*(5*self.spin/360)) + 170)
        green = int(85 * math.sin(2*math.pi*((5*self.spin+120)/360)) + 170)
        blue = int(85 * math.sin(2*math.pi*((5*self.spin+240)/360)) + 170)
        self.hoverColor = '#' + hex(red)[2:] + hex(green)[2:] + hex(blue)[2:]

    def buttonCords(self,x,y,w,h): # Return coordinates for an oval-rectangle hybrid (bc smooth polygons are TOO oval-like)
        x0, y0 = x - w, y + h
        x1, y1 = x + w, y + h
        x2, y2 = x + w, y - h
        x3, y3 = x - w, y - h
        return (x0-5,y0-5),(x0,y0),(x0+5,y0+5),(x1-5,y1+5),(x1,y1),(x1+5,y1-5),(x2+5,y2+5),(x2,y2),(x2-5,y2-5),(x3+5,y3-5),(x3,y3),(x3-5,y3+5)

    def drawButtons(self,canvas): # Does exactly what it sounds like
        if self.mX > 421 and self.mX < 579:
            if self.mY > 606 and self.mY < 644: colors = [self.hoverColor,'White','White',]
            elif self.mY > 656 and self.mY < 694: colors = ['White',self.hoverColor,'White']
            elif self.mY > 706 and self.mY < 744: colors = ['White','White',self.hoverColor]
            else: colors = ['White','White','White']
        else: colors = ['White','White','White']
        canvas.create_polygon(*self.buttonCords(500,625,75,15),fill=colors[0],width=3,outline="black")
        canvas.create_text(500,625,text='Enter',fill='black',font='Times 26 bold')
        canvas.create_polygon(*self.buttonCords(500,675,75,15),fill=colors[1],width=3,outline="black")
        canvas.create_text(500,675,text='Load',fill='black',font='Times 26 bold')
        canvas.create_polygon(*self.buttonCords(500,725,75,15),fill=colors[2],width=3,outline="black")
        canvas.create_text(500,725,text='Tutorial',fill='black',font='Times 26 bold')

    def drawSpiral(self,canvas):
        spiralCords = [] # Cordinates used to draw a spiral
        for t in range(70,700,5):
            spiralCords.append(500+t*math.cos(t+self.spin/20)*1.1)
            spiralCords.append(400+t*math.sin(t+self.spin/20)*1.1)
        t = int(self.spin/3) % 16
        redStr = '3456789aa9876543'
        greStr = 'abcdeffedcba9889'
        bluStr = '56789abccba98765'
        canvas.create_line(*spiralCords,fill=f"#{2*redStr[t]}{2*greStr[t]}{2*bluStr[t]}",width=5,smooth=True)

    def drawLogo(self,canvas):
        self.canvas.create_polygon(400,400,500,300,600,400,500,500,width=5,fill="White",outline="Black")
        canvas.create_text(500,390,text="EARL",font="Futura 35 bold")
        canvas.create_text(500,415,text="grey",font="Futura 20 bold")

    def redrawAll(self,canvas): # Clear canvas with each tick & draw all squares
        self.canvas.delete(ALL)
        self.drawSpiral(self.canvas)
        self.drawLogo(self.canvas)
        self.drawButtons(self.canvas)

class LoadScreen(Mode):
    def modeActivated(self): # When activated, discard the graphics-file canvas
        self.app._canvas.pack_forget()
        self.canvas = Canvas(self.app._root,width=1000,height=800)
        self.canvas.pack()
        self.allFiles = getEARLgreyFiles()
        self.carousel = 0
        self.spin = 0
        self.kF = []
        self.popMax = 10
        loadSet = []
        for i in self.allFiles:
            loadSet.append(i)
            if len(loadSet) == self.popMax or i == self.allFiles[-1]:
                self.kF.append(loadSet)
                loadSet = []
        self.hovering = -1
        self.clicked = -1

    def appStarted(self):
        self.hoverColor = 'White'
        self.time = 0
        self.timerDelay = 5

    def modeDeactivated(self): # When deactivated, re-impose the graphics-file canvas
        self.canvas.pack_forget()
        self.app._canvas.pack()

    def mouseMoved(self,event): # Detects if an buttton is being hovered over
        if event.x < 200 or event.x > 600 or event.y < 200 or event.y > 600 or len(self.kF) == 0:
            self.hovering = -1
            return
        for i in range(len(self.kF[self.carousel])):
            if event.y > 200+(i*400/self.popMax) and event.y < 200+((i+1)*400/self.popMax):
                self.hovering = i
                return
        self.hovering = -1

    def mousePressed(self,event): # Detects if an option is being selected or a button is being pressed
        if event.x > 600 and event.x < 650 and event.y > 560 and event.y < 600:
            self.carousel += 1
            self.carousel %= len(self.kF)
        elif event.y > 600 and event.y < 650:
            if event.x > 200 and event.x < 350:
                self.app.setActiveMode(self.app.home)
            elif event.x > 400 and event.x < 550 and self.clicked != -1:
                EARLgrey.loadFile(self.kF[self.carousel][self.clicked])
                self.app.setActiveMode(self.app.main)
        elif event.x < 200 or event.x > 600 or event.y < 200 or event.y > 600:
            self.clicked = -1
            return
        else:
            if len(self.kF) == 0: return
            for i in range(len(self.kF[self.carousel])):
                if event.y > 200+(i*400/self.popMax) and event.y < 200+((i+1)*400/self.popMax):
                    self.clicked = i
                    return
        self.clicked = -1

    def timerFired(self): # Increment the animation
        self.spin += 2.5
        red = int(55 * math.sin(2*math.pi*(5*self.time/360)) + 200)
        green = int(55 * math.sin(2*math.pi*((5*self.time+120)/360)) + 200)
        blue = int(55 * math.sin(2*math.pi*((5*self.time+240)/360)) + 200)
        self.hoverColor = '#' + hex(red)[2:] + hex(green)[2:] + hex(blue)[2:]

    def redrawAll(self,canvas):
        self.canvas.create_rectangle(0,0,self.width,self.height,fill='#888888')
        self.canvas.create_rectangle(200,200,600,self.height-200,fill='#efefef')
        self.canvas.create_rectangle(200,150,500,200,fill='#343434')       
        self.canvas.create_text(210,175,font='Times 26 bold',text='Saved EARLgrey Files:',anchor='w',fill='#efefef')
        if self.kF == []: self.canvas.create_text(400,250,font='Times 20 bold',text='There are no EARLgrey Files to load')
        else:
            for i in range(len(self.kF[self.carousel])):
                if i == self.clicked: c = '#efefef'
                elif i == self.hovering: c = self.hoverColor
                else: c = None
                self.canvas.create_rectangle(200,200+(i*400/self.popMax),600,200+((i+1)*400/self.popMax),fill=c)
                self.canvas.create_text(210,200+((i+0.5)*400/self.popMax),text=self.kF[self.carousel][i],font='Times 26 bold',anchor='w')
        self.canvas.create_rectangle(200,600,350,650,fill='#efabab')
        self.canvas.create_text(275,625,font='Times 20 bold',text='Return Home')
        if self.clicked != -1:
            self.canvas.create_rectangle(375,600,525,650,fill='#abefab')
            self.canvas.create_text(450,625,font='Times 20 bold',text='Load File')
        if len(self.kF) > 1:
            self.canvas.create_rectangle(600,560,650,600,fill='#ababef')
            self.canvas.create_text(625,580,font='Times 20 bold',text='->')

def popupBox(question): # My own implementation of getUserInput
    return simpledialog.askstring('', question)

class EARLgrey(ModalApp):
    def appStarted(self):
        self.home = HomeScreen()
        self.load = LoadScreen()
        self.main = MainScreen()
        self.setActiveMode(self.home)

    @staticmethod
    def newSave(): # Saves a new EARLgrey File
        sName = popupBox('What do you want to save the file as?')
        if sName != None:
            if '.' in sName:
                nextStep = popupBox(f'"{sName}" is not a valid name.\nPress ok else to try again.')
                if nextStep != None: KIMCHI.newSave()
            elif sName in getEARLgreyFiles():
                nextStep = popupBox(f'"{sName}" is already a file name')
            else:
                f = open(f"{sName}.eg.txt","w+")
                f.write(''.join(commandLines))
                f.close()

    @staticmethod
    def loadFile(name): # Loads an EARLgrey File
        global commandLines
        try:
            f = open(f"{name}","r")
            r = f.read()
            commandLines = list(r)
            f.close()
        except Exception as e:
            pass

class Number(object):
    def __init__(self,value):
        self.value = value

    def __bool__(self):
        return self != Number(0)

    def __add__(self,other):
        if type(other) != Number:
            raise TypeError(f"Cannot add {type(self)} and {type(other)}")
        return Number(self.value+other.value)

    def __neg__(self):
        return Number(0) - self

    def __sub__(self,other):
        if type(other) != Number:
            raise TypeError(f"Cannot subtract {type(self)} and {type(other)}")
        return Number(self.value-other.value)

    def __mul__(self,other):
        if type(other) != Number:
            raise TypeError(f"Cannot multiply {type(self)} and {type(other)}")
        return Number(self.value*other.value)

    def __pow__(self,other):
        if type(other) != Number:
            raise TypeError(f"Cannot exponentiate {type(self)} and {type(other)}")
        return Number(self.value**other.value)

    def __truediv__(self,other):
        if type(other) != Number:
            raise TypeError(f"Cannot divide {type(self)} and {type(other)}")
        if other.value == 0:
            raise ZeroDivisionError("Cannot divide {type(self)} by 0")
        return Number(self.value//other.value)

    def __mod__(self,other):
        if type(other) != Number:
            raise TypeError(f"Cannot mod {type(self)} and {type(other)}")
        if other.value == 0:
            raise ZeroDivisionError("Cannot divide {type(self)} by 0")
        return Number(self.value%other.value)

    def log(self,other):
        if type(other) != Number:
            raise TypeError(f"Cannot log {type(self)} and {type(other)}")
        if other.value <= 0:
            raise ZeroDivisionError(f"Cannot log {type(self)} by {other.value}")
        return Number(math.log(self.value,other.value))

    def __round__(self,n=0):
        if n == 0: return Number(int(self.value))
        return Number(round(self.value,n))

    def __abs__(self):
        return Number(abs(self.value))

    def __eq__(self,other):
        return Logic(type(self) == type(other) and self.value == other.value)

    def __le__(self,other):
        if type(other) != Number: raise TypeError(f"Cannot compare {type(self)} and {type(other)}")
        return Logic(self.value <= other.value)

    def __lt__(self,other):
        if type(other) != Number: raise TypeError(f"Cannot compare {type(self)} and {type(other)}")
        return Logic(self.value < other.value)

    def __gt__(self,other):
        if type(other) != Number: raise TypeError(f"Cannot compare {type(self)} and {type(other)}")
        return Logic(self.value > other.value)

    def __ge__(self,other):
        if type(other) != Number: raise TypeError(f"Cannot compare {type(self)} and {type(other)}")
        return Logic(self.value >= other.value)

    def sin(self):
        return Number(math.sin(self.value))

    def cos(self):
        return Number(math.cos(self.value))

    def tan(self):
        return Number(math.tan(self.value))

    @staticmethod
    def random(a,b):
        return (Number(random.random())*(b-a))+a

    def chr(self):
        return Vocab(repr(chr(int(abs(self.value)))))

    def __repr__(self):
        if round(self) == self: return f'{round(self.value)}'
        s0 = f'%0.1f' % self.value
        for i in range(8):
            s1 = f'%0.{i+1}f' % self.value
            if s1[-1] != '0': s0 = s1
        return s0

class Vocab(object):
    def __init__(self,value):
        self.value = value[1:-1]

    def __bool__(self):
        return self != Vocab("")

    def __eq__(self,other):
        return Logic(type(self) == type(other) and self.value == other.value)

    def __iter__(self):
        return iter(self.value)

    def __getitem__(self,key):
        return self.value[key]

    def uni(self):
        return Number(ord(self[0]))

    def __len__(self):
        return len(self.value)

    def __add__(self,other):
        if type(other) != Vocab: raise TypeError(f"Cannot compare {type(self)} and {type(other)}")
        return Vocab(repr(self.value+other.value))

    def __repr__(self):
        return repr(self.value)

    def split(self):
        return Union(*list(self.value))

class Union(object):
    def __init__(self,*values):
        self.values = values

    def __bool__(self):
        return self != Union()

    def __getitem__(self,key):
        if type(key) == slice:
            return Union(*self.values[key])
        return self.values[key]

    def __eq__(self,other):
        return Logic(type(self) == type(other) and self.values == other.values)

    def count(self,item):
        return Number(self.values.count(item))

    def index(self,item):
        for i in range(len(self)):
            if self[i] == item: return Number(i)
        return Number(-1)

    def subset(self,other):
        if type(other) != Union: raise TypeError(f"Cannot check subsets of {type(other)}")
        for i in self:
            if other.count(i) < self.count(i): return Logic(False)
        return Logic(True)

    def __add__(self,other):
        if type(other) != Union: raise TypeError(f"Cannot link {type(self)} and {type(other)}")
        return Union(*(self.values+other.values))

    def __iter__(self):
        return iter(self.values)

    def __len__(self):
        return len(self.values)

    def __repr__(self):
        return '<' + str(self.values)[1:-1] + '>'

class Logic(object):
    def __init__(self,value):
        self.value = bool(value)

    def __bool__(self):
        return self.value

    def __repr__(self):
        return str(self.value).upper()

class Transform(object):

    def __init__(self,name,function,argsList,varArgs=False):
        if name != None and name in VarLibrary:
            raise NameError(f"Name {name} already found")
        self.name = name
        self.function = function
        self.argsList = argsList
        self.varArgs = varArgs
        if name != None: VarLibrary[self.name] = self
    
    def __repr__(self):
        return chr(955) + f'({"*" if self.varArgs else ""}{formatTypes(self.argsList)})'

    def __eq__(self,other):
        return type(other) == Transform and self.function == other.function and self.argsList == other.argsList and self.varArgs == other.varArgs

    def __call__(self,*operands):
        if len(operands) < len(self.argsList):
            raise TypeError(f"{self.name} requires at least {len(self.argsList)} arguments")
        if len(operands) > len(self.argsList) and not self.varArgs:
            raise TypeError(f"{self.name} accepts no more than {len(self.argsList)} arguments")
        for i in range(len(operands)):
            if ((self.varArgs and self.argsList[0] != None and type(operands[i]) != self.argsList[0]) or 
                (self.argsList[i] != None and type(operands[i]) != self.argsList[i])):
                raise TypeError(f"Argument {i+1} of {self.name} must be a {self.argsList[i]} (recieved {type(operands[i])})")
            return self.function(*operands)

ADD = Transform("add",lambda *x: functools.reduce(lambda y,z: y+z, x),[Number],True)
SUB = Transform("sub",lambda *x: x[0] - functools.reduce(lambda y,z: y+z, x[1:]) if len(x) > 1 else x[0],[Number],True)
MUL = Transform("mul",lambda *x: functools.reduce(lambda y,z: y*z, x),[Number],True)
DIV = Transform("div",lambda *x: x[0] / functools.reduce(lambda y,z: y*z, x[1:]) if len(x) > 1 else x[0],[Number],True)
POW = Transform("pow",lambda x,y: x**y, [Number,Number])
MOD = Transform("mod",lambda x,y: x%y, [Number,Number])
LOG = Transform("log",lambda x,y: x.log(y), [Number,Number])
SIN = Transform("sin",lambda x: x.sin(), [Number])
COS = Transform("cos",lambda x: x.cos(), [Number])
TAN = Transform("tan",lambda x: x.tan(), [Number])
LESS = Transform("less",lambda x,y: x < y, [None,None])
EQUAL = Transform("equal",lambda x,y: x == y, [None,None])
GREATER = Transform("greater",lambda x,y: x > y, [None,None])
ABS = Transform("abs",lambda x: abs(x), [Number])
ROUND = Transform("round",lambda x: round(x), [Number])
RANDOM = Transform("random",lambda x,y: Number.random(x,y), [Number,Number])
UNI = Transform("uni",lambda x: x.uni(),[Vocab])
CHR = Transform("chr",lambda x: x.chr(),[Number])
UPPER = Transform("upper",lambda x: Vocab(x.value.upper()),[Vocab])
LOWER = Transform("lower",lambda x: Vocab(x.value.lower()),[Vocab])
CONCAT = Transform("concat",lambda *x: functools.reduce(lambda y,z: y+z, x),[Vocab],True)
SIZE = Transform("size",lambda x: Number(len(x)),[Vocab])
SPLIT = Transform("split",lambda x: x.split(),[Vocab])
BRANCH = Transform("branch", lambda x, y, z: y if x else z,[None,None,None])
OR = Transform("or",lambda *x: Logic(any(x)),[None],True)
AND = Transform("and",lambda *x: Logic(all(x)),[None],True)
NOT = Transform("not",lambda x: Logic(not(bool(x))),[None])
LINK = Transform("link",lambda *x: functools.reduce(lambda y,z: y+z, x),[Union],True)
GET = Transform("get",lambda x,y: x[round(y).value], [Union,Number])
SLICE = Transform("slice",lambda x,y,z,a: x[round(y).value:round(z).value:round(a).value], [Union,Number,Number,Number])
INSIDE = Transform("inside",lambda x,y: Logic(x in y), [None,Union])
COUNT = Transform("count",lambda x,y: y.count(x), [None,Union])
SUBSET = Transform("subset",lambda x,y: x.subset(y), [Union, Union])
RANGE = Transform("range",lambda x,y,z: Union(*range(round(x).value,round(y).value,round(z).value)),[Number, Number, Number])
JOIN = Transform("join",lambda x: ''.join([str(i) for i in x]),[Union])
INDEX = Transform("index", lambda x, y: y.index(x), [None,Union])
MAP = Transform("map", lambda x: Transform(None,lambda y: Union(*map(lambda z: x(z), y)), [Union]),[Transform])
KEEP = Transform("keep", lambda x: Transform(None,lambda y: Union(*filter(lambda z: x(z), y)), [Union]),[Transform])
MERGE = Transform("merge", lambda x: Transform(None,lambda y: functools.reduce(lambda z,a: x(z,a), y), [Union]),[Transform])
SORT = Transform("sort", lambda x: Transform(None,lambda y: Union(*sorted(y,key=x)),[Union]),[Transform])
MIN = Transform("min", lambda x: Transform(None,lambda y: min(y,key=x),[Union]),[Transform])
MAX = Transform("max", lambda x: Transform(None,lambda y: max(y,key=x),[Union]),[Transform])

EARLgrey(width=1000,height=800)
