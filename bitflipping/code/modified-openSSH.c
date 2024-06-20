/* Code modified from https://github.com/openssh/openssh-portable/blob/master/auth-passwd.c 
   with inspration from Mayhem: Targeted Corruption of Register and Stack Variables by Adiletta et al.
*/

/* RISC-V rv32gc clang compiler used */

#define AUTH_SUCCESS		0x52a2925	/* 0101001010100010100100100101 */
#define AUTH_FAILURE		0xad5d6da	/* 1010110101011101011011011010 */


typedef struct Authctxt Authctxt;
typedef unsigned int u_int;
typedef unsigned int u_int32_t;
typedef int dispatch_fn(int, u_int32_t, struct ssh *);
int sys_auth_passwd(struct ssh *ssh, const char *password);
void	 auth_restrict_session(struct ssh *);

typedef struct {
	int     permit_empty_passwd;	/* If false, do not permit empty
					 * passwords. */
}       ServerOptions;


struct ssh {

	/* Client/Server authentication context */
	void *authctxt;

};


struct Authctxt {
	int		 valid;		/* user exists and is allowed to login */
	int		 force_pwchange;
};

extern ServerOptions options;

int auth_password(struct ssh *ssh, const char *password)
{
	Authctxt *authctxt = ssh->authctxt;
	int result, ok = authctxt->valid;


	if (*password == '\0' && options.permit_empty_passwd == 0)
		return AUTH_FAILURE;

    result = sys_auth_passwd(ssh, password);
	if (authctxt->force_pwchange)
		auth_restrict_session(ssh);

    if(!ok)
        return AUTH_FAILURE;    
	if(result == AUTH_SUCCESS)
        return AUTH_SUCCESS;
    return AUTH_FAILURE;
}