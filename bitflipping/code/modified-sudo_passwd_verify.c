// SUDO code from: https://github.com/sudo-project/sudo/commit/7873f8334c8d31031f8cfa83bd97ac6029309e4f#diff-b8ac7ab4c3c4a75aed0bb5f7c5fd38b9ea6c81b7557f775e46c6f8aa115e02cd

// Modified SUDO (new version)
#define AUTH_SUCCESS		0x52a2925	/* 0101001010100010100100100101 */
#define AUTH_FAILURE		0xad5d6da	/* 1010110101011101011011011010 */

typedef struct sudo_auth {
    unsigned int flags;		/* various flags, see below */
    int status;			/* status from verify routine */
    const char *name;		/* name of the method as a string */
    void *data;			/* method-specific data pointer */
} sudo_auth;


int sudo_passwd_verify(const char *pass, sudo_auth *auth)
{
    char *pw_passwd = auth->data;
    int ret;

    int strCmpRes = 4095;
    while (*pass == *pw_passwd++)
		if (*pass++ == '\0'){
			strCmpRes = 0;
            break;
        }
    if (strCmpRes != 0)
	    strCmpRes = (*(const unsigned char *)pass - *(const unsigned char *)(pw_passwd - 1));

    if (strCmpRes == 0)
	    ret = AUTH_SUCCESS;
    else
	    ret = AUTH_FAILURE;


    return ret;
}


// Modified SUDO (old version)
#define AUTH_SUCCESS		1
#define AUTH_FAILURE		0

typedef struct sudo_auth {
    unsigned int flags;		/* various flags, see below */
    int status;			/* status from verify routine */
    const char *name;		/* name of the method as a string */
    void *data;			/* method-specific data pointer */
} sudo_auth;


int sudo_passwd_verify(const char *pass, sudo_auth *auth)
{
    char *pw_passwd = auth->data;
    int ret;

 int strCmpRes = 4095;
    while (*pass == *pw_passwd++)
		if (*pass++ == '\0'){
			strCmpRes = 0;
            break;
        }
    if (strCmpRes != 0)
	    strCmpRes = (*(const unsigned char *)pass - *(const unsigned char *)(pw_passwd - 1));

    /* Simple string compare for systems without crypt(). */
    ret = strCmpRes;

    return ret ? AUTH_SUCCESS : AUTH_FAILURE;
}