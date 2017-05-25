from passlib.hash import sha256_crypt

hash = sha256_crypt.hash("jessica")
print(hash)
