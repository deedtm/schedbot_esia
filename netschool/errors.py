class NetSchoolError(Exception):
    pass

class LoginError(NetSchoolError):
    pass

class MissingCredentials(LoginError):
    pass
