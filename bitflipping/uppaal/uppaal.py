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
        
        
