import getpass

from model import User

if __name__ == '__main__':
    print("We will now ask you for your email id and password to create a root user")
    email = input("Enter your email id:\n")
    password = getpass.getpass("Enter password: \n")
    password_re = getpass.getpass("Enter password again to confirm:\n")
    if password != password_re:
        print("passwords did not match. try again.")
    else:
        User.create_root(email, password)
        print("root user created")
