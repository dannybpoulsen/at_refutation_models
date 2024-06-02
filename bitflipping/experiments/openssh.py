import bitflipping.models
import bitflipping.locator

import scipy
import tabulate
import random
import matplotlib.pyplot as plt




class Experiments:
    def __init__(self,uppaal,result_loc):
        self._uppaal = uppaal
        self._locator = result_loc.sublocator ("SUDO")
        
        
    def runTobias (self):
        loc = self._locator.sublocator ("Tobias")
        openssh = bitflipping.models.OpenSSH_Model()
        rows = []
        with bitflipping.locator.Progresser() as prog:
            for flips in [1,2,3,4,5]:
                prog.message (f"Tobias: {flips}")   
            
                sudo.set_max_flips (flips)
                sudo.set_old_version ()

                old_estim = self._uppaal.runVerification (sudo,"Pr[<=500;100000] (<> SUDO.Auth_Succ)")
                sudo.set_fixed_version ()
                new_estim = self._uppaal.runVerification (sudo,"Pr[<=500;100000] (<> SUDO.Auth_Succ)")

                old_data = ([1]*old_estim.getSatisRuns())+([0]*old_estim.getNSatisRuns())
                new_data = ([1]*new_estim.getSatisRuns())+([0]*new_estim.getNSatisRuns())

                test = scipy.stats.ttest_ind(a=old_data,b=new_data,equal_var=False)
                
                rows.append ([flips,old_estim.getSatisRuns(),new_estim.getSatisRuns (),test.pvalue])
            with loc.makeFile ("table.txt") as ff: 
                ff.write (tabulate.tabulate (rows,
                                             headers=["Max flips","Old Succ","New Succ","PValue"])
                          )
            

                
            
    def run (self):
        self.runTobias ()
        self.runHammingDistFun() 
