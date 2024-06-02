import bitflipping.models
import bitflipping.locator

import scipy
import tabulate
import random
import matplotlib.pyplot as plt


def count_ones (b):
    summ = 0
    for i in range(0,8):
        if (b & (1 << i)):
            summ+= 1
    return summ

def hamming(b1,b2):
    summ = 0
    for a,b in zip (b1,b2):
        summ += count_ones(a^b)
    return summ

def hamming_dist_build(b1,num):
    pat = [0]*len(b1)
    for i in range(0,num):
        done = False
        while not done:
            bit = random.randint(0,(len(b1)-1)*8)
            byte_n = int(bit / 8)
            bit_offset = bit % 8
            if not (pat[byte_n] & (1 << bit_offset)):
                done = True
        
        pat[byte_n] = pat[byte_n] | (1 << bit_offset)
    #print (num, pat)
    return bytes([a^b for a,b in zip(b1,pat)])



def build_rand_dist(b1):
    ll = list([b for b in b1])
    bytediff = secrets.token_bytes(len(b1))
    
    
    
    
    return bytes([a^b for a,b in zip (ll,bytediff)])


class Experiments:
    def __init__(self,uppaal,result_loc):
        self._uppaal = uppaal
        self._locator = result_loc.sublocator ("SUDO")
        
        
    def runTobias (self):
        loc = self._locator.sublocator ("Tobias")
        sudo = bitflipping.models.SUDO_Model()
        user_pass = "1245".encode('ascii')
        stored_pass = list([l.encode('ascii') for l in["2245","6789","2289","1367"]])
        rows = []
        with bitflipping.locator.Progresser() as prog:
            
            for stored in stored_pass:
                for flips in [1,2,3,4,5]:
                    prog.message (f"Tobias: {user_pass.decode('ascii')} - {stored.decode('ascii')} - {flips}")   
            
                    sudo.set_user_password (user_pass+b'\0')
                    sudo.set_stored_password (stored+b'\0')
                    sudo.set_max_flips (flips)
                    sudo.set_old_version ()

                    old_estim = self._uppaal.runVerification (sudo,"Pr[<=500;100000] (<> SUDO.Auth_Succ)")
                    sudo.set_fixed_version ()
                    new_estim = self._uppaal.runVerification (sudo,"Pr[<=500;100000] (<> SUDO.Auth_Succ)")

                    old_data = ([1]*old_estim.getSatisRuns())+([0]*old_estim.getNSatisRuns())
                    new_data = ([1]*new_estim.getSatisRuns())+([0]*new_estim.getNSatisRuns())

                    test = scipy.stats.ttest_ind(a=old_data,b=new_data,equal_var=False)

                    rows.append ([flips,user_pass,stored,hamming(user_pass,stored),old_estim.getSatisRuns(),new_estim.getSatisRuns (),test.pvalue])
            with loc.makeFile ("table.txt") as ff: 
                ff.write (tabulate.tabulate (rows,
                                             headers=["Max flips","User Password","Stored Pass","Hamming", "Old Succ","New Succ","PValue"])
                          )
            

    def runHammingDistFun(self):
        loc = self._locator.sublocator ("Hamming")
        sudo = bitflipping.models.SUDO_Model()
        user_pass = "1245".encode('ascii')
        rows = []

        stored_pass = [ hamming_dist_build (user_pass,hamm) for hamm in [2,4,8,10,12]]
                
        with bitflipping.locator.Progresser() as prog:
            for flips in range(0,6):
                x = []
                old = []
                new = []
                for i,stored in enumerate(stored_pass):
                    prog.message (f"HammingDist Fun: {flips} - {i} (flips - passwordnumber)")  
                    sudo.set_user_password (user_pass+b'\0')
                    sudo.set_stored_password (stored+b'\0')
                    sudo.set_max_flips (flips)

                    sudo.set_old_version ()
                    old_estim = self._uppaal.runVerification (sudo,"Pr[<=500;100000] (<> SUDO.Auth_Succ)")

                    sudo.set_fixed_version ()
                    new_estim = self._uppaal.runVerification (sudo,"Pr[<=500;100000] (<> SUDO.Auth_Succ)")

                    old_data = ([1]*old_estim.getSatisRuns())+([0]*old_estim.getNSatisRuns())
                    new_data = ([1]*new_estim.getSatisRuns())+([0]*new_estim.getNSatisRuns())

                    x.append (hamming(user_pass,stored))
                    old.append (old_estim.getSatisRuns ())
                    new.append (new_estim.getSatisRuns ())



                    test = scipy.stats.ttest_ind(a=old_data,b=new_data,equal_var=False)

                    rows.append ([flips,user_pass,stored,hamming(user_pass,stored),old_estim.getSatisRuns(),new_estim.getSatisRuns (),test.pvalue])

                fig = plt.figure ()
                ax = fig.subplots ()
                ax.plot (x,old,label='Old')
                ax.plot (x,new,label='Fixed')

                ax.set_xlabel ("Hamming")
                ax.set_ylabel ("Succesfull  Attacks")
                ax.legend ()
                fig.savefig (loc.makeFilePath (f"{flips}.png"))
            with loc.makeFile ("table.txt") as ff: 
                ff.write (tabulate.tabulate (rows,
                                             headers=["Max flips","User Password","Stored Pass","Hamming", "Old Succ","New Succ","PValue"])
                                  )
                
            
    def run (self):
        self.runTobias ()
        self.runHammingDistFun() 