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
        user_passs = "1245".encode('ascii')
        stored_pass = list([l.encode('ascii') for l in["2245","6789","2289","1367"]])
        rows = []
        with bitflipping.locator.Progresser() as prog:
            for user_pass in [user_passs]:
                for stored in stored_pass:
                    for flips in range(1,6):
                        prog.message (f"Tobias: {user_pass.decode('ascii')} - {stored.decode('ascii')} - {flips}")   

                        sudo.set_user_password (user_pass)
                        sudo.set_stored_password (stored)
                        sudo.set_max_flips (flips)
                        sudo.set_old_version ()

                        old_estim = self._uppaal.runVerification (sudo,"Pr[<=500;1000000] (<> SUDO.Auth_Succ)")
                        sudo.set_fixed_version ()
                        new_estim = self._uppaal.runVerification (sudo,"Pr[<=500;1000000] (<> SUDO.Auth_Succ)")

                        old_data = ([1]*old_estim.getSatisRuns())+([0]*old_estim.getNSatisRuns())
                        new_data = ([1]*new_estim.getSatisRuns())+([0]*new_estim.getNSatisRuns())

                        test = scipy.stats.ttest_ind(a=old_data,b=new_data,equal_var=False)

                        rows.append ([flips,user_pass,stored,hamming(user_pass,stored),old_estim.getSatisRuns(),new_estim.getSatisRuns (),test.pvalue])
            with loc.makeFile ("table.txt") as ff: 
                ff.write (tabulate.tabulate (rows,
                                             headers=["Max flips","User Password","Stored Pass","Hamming", "Old Succ","New Succ","PValue"])
            )

            with loc.makeFile ("table.tex") as ff: 
                self._output_tex_table(ff,rows)

    def runTobiasExtra (self):
        loc = self._locator.sublocator ("TobiasExtra")
        sudo = bitflipping.models.SUDO_Model()
        user_passs = "1245".encode('ascii')
        stored_pass = list([l.encode('ascii') for l in["2245","6789","2289","1367"]])
        rows = []
        with bitflipping.locator.Progresser() as prog:
            for user_pass in [user_passs,b'1355']:
                for stored in stored_pass+[b'1457']:
                    for flips in [1,3,5,10,20]:
                        prog.message (f"Tobias: {user_pass.decode('ascii')} - {stored.decode('ascii')} - {flips}")   

                        sudo.set_user_password (user_pass)
                        sudo.set_stored_password (stored)
                        sudo.set_max_flips (flips)
                        sudo.set_old_version ()

                        old_estim = self._uppaal.runVerification (sudo,"Pr[<=500;1000000] (<> SUDO.Auth_Succ)")
                        sudo.set_fixed_version ()
                        new_estim = self._uppaal.runVerification (sudo,"Pr[<=500;1000000] (<> SUDO.Auth_Succ)")

                        old_data = ([1]*old_estim.getSatisRuns())+([0]*old_estim.getNSatisRuns())
                        new_data = ([1]*new_estim.getSatisRuns())+([0]*new_estim.getNSatisRuns())

                        test = scipy.stats.ttest_ind(a=old_data,b=new_data,equal_var=False)

                        rows.append ([flips,user_pass,stored,hamming(user_pass,stored),old_estim.getSatisRuns(),new_estim.getSatisRuns (),test.pvalue])
            with loc.makeFile ("table.txt") as ff: 
                ff.write (tabulate.tabulate (rows,
                                             headers=["Max flips","User Password","Stored Pass","Hamming", "Old Succ","New Succ","PValue"])
            )

            with loc.makeFile ("table.tex") as ff: 
                self._output_tex_table(ff,rows)

                
    def runHammingDistFun(self):
        loc = self._locator.sublocator ("Hamming")
        sudo = bitflipping.models.SUDO_Model()
        user_pass = "1245".encode('ascii')
        
        stored_pass = [ hamming_dist_build (user_pass,hamm) for hamm in [2,4,8,10,12]]
                
        with bitflipping.locator.Progresser() as prog:
            for flips in range(0,6):
                subloc = loc.sublocator (f"Flips_{flips}")
                rows = []
                for i,stored in enumerate(stored_pass):
                    prog.message (f"HammingDist Fun: {flips} - {i} (flips - passwordnumber)")  
                    sudo.set_user_password (user_pass)
                    sudo.set_stored_password (stored)
                    sudo.set_max_flips (flips)

                    sudo.set_old_version ()
                    
                    
                    old_estim,  old_flip_data= self._uppaal.runVerification (sudo,"Pr[<=500;100000] (<> SUDO.Auth_Succ)",postprocess = bitflipping.uppaal.uppaal.FlipAndEstim)
                    
                    sudo.set_fixed_version ()
                    new_estim, new_flip_data= self._uppaal.runVerification (sudo,"Pr[<=500;100000] (<> SUDO.Auth_Succ)",postprocess = bitflipping.uppaal.uppaal.FlipAndEstim)

                    old_data = ([1]*old_estim.getSatisRuns())+([0]*old_estim.getNSatisRuns())
                    new_data = ([1]*new_estim.getSatisRuns())+([0]*new_estim.getNSatisRuns())
                    
                    
                    with open(subloc.makeFilePath(f"Hamming_{hamming(user_pass,stored)}_old"),'w') as ff:
                        ff.write (str(old_flip_data.res_data()))
                    with open(subloc.makeFilePath(f"Hamming_{hamming(user_pass,stored)}_new"),'w') as ff:
                        ff.write (str(new_flip_data.res_data()))
                    

                    test = scipy.stats.ttest_ind(a=old_data,b=new_data,equal_var=False)

                    rows.append ([flips,user_pass,stored,hamming(user_pass,stored),old_estim.getSatisRuns(),new_estim.getSatisRuns (),test.pvalue])
                
                with subloc.makeFile ("table.txt") as ff: 
                    ff.write (tabulate.tabulate (rows,
                                                 headers=["Max flips","User Password","Stored Pass","Hamming", "Old Succ","New Succ","PValue"])
                              )
                with loc.makeFile ("table.tex") as ff: 
                    ff.write ("""\\begin{tabular}{r | l | l | r | r | r | r}                \\hline
                \\uppExpr{MAX_FLIPS} & \\uppExpr{user_pass}& \\uppExpr{stored_pass}& Hamming & \\uppExpr{new_ver == 0} & \\uppExpr{new_ver == 1} & PValue \\\\ \\hline
                """)
                    for r in rows:
                        ff.write (f"{r[0]} & {r[1]} & {r[2]} & {r[3]} & {r[4]} & {r[5]} &  {r[6]:.2E} \\ \\hline")
                    ff.write ("""\\end{tabular}
\hline
                """)
                #ff.write (tabulate.tabulate (rows,
                #                             headers=["Max flips","User Password","Stored Pass","Hamming", "Old Succ","New Succ","PValue"])
            
    def _output_tex_table(self,ff,rows):
        ff.write ("""\\begin{tabular}{r | l | l | r | r | r | r}                \\toprule
                \\uppExpr{MAX_FLIPS} & \\uppExpr{user_pass}& \\uppExpr{stored_pass}& Hamming & \\uppExpr{new_ver == 0} & \\uppExpr{new_ver == 1} & PValue \\\\ \\midrule
                
                """)
        old = -1
        for r in rows:
            if old > r[0]:
                ff.write ("\\midrule")
            
            ff.write (f"{r[0]} & {r[1].decode('ascii')} & {r[2].decode('ascii')} & {r[3]} & {r[4]} & {r[5]} &  {r[6]:.2E} \\\\ ")
            ff.write ("\n")
            old = r[0]
        ff.write ("\\bottomrule \\end{tabular}")
            
        
                
    def run (self):
        self.runTobias ()
        self.runTobiasExtra ()
        #self.runHammingDistFun() 


class GUI:
    def __init__(self,uppaal):
        self._uppaal = uppaal
    
    def runGUI (self,user_pass = "1234".encode('ascii'),stored_pass = "2345".encode('ascii'),max_flips = 5,fixed_version=True):
        sudo = bitflipping.models.SUDO_Model()
        sudo.set_user_password (user_pass)
        sudo.set_stored_password (stored_pass)
        sudo.set_max_flips (max_flips)
        if fixed_version:
            sudo.set_fixed_version ()
        else:
            sudo.set_old_version ()
        
        self._uppaal.openGUI (sudo)
    
