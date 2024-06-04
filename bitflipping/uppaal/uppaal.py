import os
import tempfile
import shutil
import subprocess
import os
import sys
import multiprocessing
import pyparsing as pp



        

    
    
class EstimResult:
    def __init__ (self,
                  prob,
                  confidence,
                  satisruns,
                  totalruns):
        self._probability = prob
        self._confidence = confidence,
        self._runs = totalruns
        self._satisruns = satisruns
        assert(self._runs >= self._satisruns)

    def getProbability (self):
        return self._probability

    def getConfidence (self):
        return self._confidence

    def getTotalRuns (self):
        return self._runs

    def getSatisRuns (self):
        return self._satisruns

    def getNSatisRuns (self):
        return self.getTotalRuns()-self._satisruns
    
    
    def getHistogram (self):
        return self._histogram


class Node:
    def __init__(self,name,reads,writes,succ):
        self._name = name
        self._reads = reads
        self._writes = writes
        self._succ = succ
        self._pred = []
        self._live = set()

        
def calc_live_register ():
    I9 = Node ("I9",{"a0"},set(),[])
    L7 = Node ("L7",set(),{"a5","a0"},[I9])
    L6 = Node ("L6",set(),{"a5"},[L7])
    I8 = Node ("I8",set(),{"a5"},[L7])
    I7 = Node ("I7",{"a5"},set(),[L6,I8])
    L5 = Node ("L5",set(),{"a5","a0"},[I9,I7])
    I6 = Node ("I6",set(),{"a5","a4"},[L5])
    I5 = Node ("I5",{"a5"},set(),[L5,I6])
    L3 = Node ("L3",set(),{"a5"},[I5])
    I2 = Node ("I2",{"a4","a5"},set(),[L3])
    
    I4 = Node ("I4",set(),set(),[L3])
    I3 = Node ("I3",{"a5"},set(),[I4])
    L4 = Node ("L4",set(),{"a5","a4"},[I3])
    I2._succ.append(L4)
    L2 = Node ("L2",set(),{"a5","a3","a4"},[I2])
    I3._succ.append(L2)
    I1 = Node ("I1",set(),{"a5"},[L2])
    

    #Reverse Edges
    waiting = [I1]
    passed = set()
    while len (waiting) > 0:
        cur = waiting.pop ()
        for s in cur._succ:
            if s not in passed:
                passed.add (s)
                waiting.append(s)
                s._pred.append (cur)

    all = [I9,L7,L6,I8,I7,L5,I6,I5,L3,I2,I4,I3,L4,I2,L2,I3,I1]
    waiting = all.copy ()
    while len(waiting) > 0:
        cur = waiting.pop()
        incoming = set()
        incoming = incoming.union (*[c._live for c in cur._succ])
        incoming = (incoming - cur._writes) | cur._reads
        print (incoming)
        
        if incoming  != cur._live:
            cur._live = incoming
            for s in cur._pred:
                print (s._name)
                waiting.append(s)
    return {c._name : c._live for c in all}

live_registers = calc_live_register ()

def relevant (loc,reg):
    return reg in live_registers.get(loc,set())


class FlipData:
    def __init__(self,locs = []):
        self._locs = locs

    def res_data (self):
        data = {}
        for res in self._locs:
            x =  ",".join([x for x in res if relevant(*x.split (";"))])
            data[x] = data.get(x,0)+1
        return data 
    
def parsePlot (line):
    interval = (pp.Literal ("[") + pp.pyparsing_common.number + pp.Literal (",") + pp.pyparsing_common.number + pp.Literal ("]")).setParseAction ( lambda s,l,t: (t[1],t[3]))
    valuesIN = (pp.Literal ("Values in") + interval).setParseAction (lambda s,l,t: t[1])
    mean = (pp.Literal ("mean=")+pp.pyparsing_common.number ()).setParseAction (lambda s,l,t: t[1])
    steps = (pp.Literal ("steps=")+pp.pyparsing_common.number ()).setParseAction (lambda s,l,t: t[1])
    values = (pp.Literal (":")+pp.OneOrMore (pp.pyparsing_common.number ())).setParseAction (lambda s,l,t: t[1:])
    parser = valuesIN+mean+steps+values
    res = parser.parseString (line)
    ran,mean,steps,counts = res[0],res[1],res[2],res[3:]
    return Histogram([(ran[0]+i*steps,ran[0]+(i+1)*steps,val) for i,val in enumerate (counts)])


def parseProbStd (line):
    parser = (pp.Literal ("(")+pp.pyparsing_common.number+pp.Literal ("/") + pp.pyparsing_common.number + pp.Literal ("runs)")+pp.Literal (f"Pr(<> …) in [")+pp.pyparsing_common.number ()+pp.Literal (",")+pp.pyparsing_common.number ()+pp.Literal("] (")+pp.pyparsing_common.number()+pp.Literal("% CI)")).setParseAction (lambda s,l,t:
                                                                                                                                                                                                             (t[1],t[3],t[6],t[8],t[10]))
    return parser.parseString (line)[0]


def parseEstim (tmpdir,stdout):
    lines = [r for r in stdout.decode().split('\n') if r != ""]
    if "Formula is satisfied" in stdout.decode ():
        resline = lines[1]
        probline = lines[2]
        #plot = lines[3]
        #histres = parsePlot (plot)
        
        prob = parseProbStd (probline)
        
        return EstimResult ((prob[2],prob[3]),prob[4],prob[0],prob[1])
    
    else:
        return EstimResult ((0,0),0,0,0,None)
    
def FlipAndEstim (tmpdir,stdout):
    estim  = parseEstim (tmpdir,stdout)
    with open(os.path.join (tmpdir,"flip_log"),'r') as ff:
        lines = ff.read ()
        return estim,FlipData(list ([line.split(',')[:-1] for line in lines.split('\n')]))

    
def justPrint  (tmpdir,stdout):
    print (stdout)


class Uppaal:
    def __init__ (self,uppaalinst):
        self._uppaalpath = os.path.abspath (uppaalinst)
        
    def __setupDirectory (self,tmpdir,modeltext):
        modelexec = os.path.join (tmpdir,"model.xml")
        #shutil.copy (self._xmlpath,modelexec)
        with open(modelexec,'w') as ff:
            ff.write (modeltext)
            ff.flush ()
        return modelexec
                    

            
    def runVerification (self,model,query,postprocess = None,discretisation = 1.0,alpha = 0.95,epsilon = 0.05):
        pp = postprocess or parseEstim
        with tempfile.TemporaryDirectory() as tmpdir:

            querypath = os.path.join (tmpdir,"queery.q")
            with open (querypath,'w') as ff:
                ff.write (query)
                ff.flush ()
            modelpath = self.__setupDirectory (tmpdir,model.model_text())
            binarypath = os.path.join (self._uppaalpath,"bin","verifyta")
            params = [binarypath,"-s","-q", modelpath,querypath]
            res = subprocess.run (params,cwd = tmpdir,capture_output=True)
            return pp (tmpdir,res.stdout)
        
        
    def openGUI (self,model,postprocess = None):
        pp = postprocess or parseEstim
        
        with tempfile.TemporaryDirectory() as tmpdir:
            modelpath = self.__setupDirectory (tmpdir,model.model_text())
            binarypath = os.path.join (self._uppaalpath,"uppaal")
            params = [binarypath,modelpath]
            res = subprocess.run (params,cwd = tmpdir)
            return pp (tmpdir,res.stdout)
        
        
