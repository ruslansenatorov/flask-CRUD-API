import bcrypt

def hashPassword(password):
    salt = bcrypt.gensalt()
    bytes = password.encode('utf-8')
    hashedpassword = bcrypt.hashpw(bytes, salt)
    return hashedpassword


def chechPassword(hashedpassword, userpassword):
    if isinstance(hashedpassword, memoryview):
        hashedpassword = hashedpassword.tobytes()
    userbytes = userpassword.encode('utf-8')

    result = bcrypt.checkpw(userbytes, hashedpassword)
    return result

