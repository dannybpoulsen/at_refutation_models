import os
import libs

class SUDO_Model:
    def __init__(self):
        self._libpath  =libs.getlib ()
        base_model_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"SUDO.xml")
        with open(base_model_path,'r') as ff:
            self._base_model_text = ff.read ()
        #print (self._base_model_text)
        self._user_pass = b'1234\0'
        self._stored_pass = b'2345\0'
        self._max_flips = 5
        self._version = 0 
        

    def set_stored_password(self,password):
        self._user_pass = password

    def set_user_password(self,password):
        self._stored_pass = password

    def set_fixed_version(self):
        self._version = 1

    def set_old_version(self):
        self._version = 0
    
        
    def set_max_flips(self,flips):
        self._max_flips = flips
        
    def model_text (self):
        return self._base_model_text.replace("@SIZE@",str(len(self._user_pass))).replace("@USER_PASS@",f"{{ {','.join ([str(b) for b in self._user_pass]) } }}").replace("@STORED_PASS@",f"{{ {','.join ([str(b) for b in self._stored_pass]) } }}").replace("@MAX_FLIPS@",str(self._max_flips)).replace ("@VERSION@",str(self._version)).replace("@LIBPATH@",self._libpath)



class OpenSSH_Model:
    def __init__(self):
        base_model_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"OpenSSH.xml")
        with open(base_model_path,'r') as ff:
            self._old_base_model_text = ff.read ()
        fixed_base_model_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"OpenSSH-fixed.xml")
        with open(fixed_base_model_path,'r') as ff:
            self._fixed_base_model_text = ff.read ()
        
        
        self._max_flips = 5
        self._fixed_version = False 
        

    def set_fixed_version(self):
        self._fixed_version = True

    def set_old_version(self):
        self._fixed_version = False
    
        
    def set_max_flips(self,flips):
        self._max_flips = flips
        
    def model_text (self):
        if self._version:
            text = self._fixed_base_model_text
        else:
            text = self._old_base_model_text
        
        return text.replace("@MAX_FLIPS@",str(self._max_flips))


