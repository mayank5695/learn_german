import getpass

from model import User

if __name__ == '__main__':
    print("We will now ask you for your email id and password to create a root user")
    email = input("Enter your email id:\n")
    password = getpass.getpass("Enter password: \n")
    password_re = getpass.getpass("Enter password again to confirm:\n")
    name=input("Enter your name: \n")
    roles=input("Are you student or teacher? Enter S or T : ")

    if password != password_re:
        print("passwords did not match. try again.")
    else:
        if roles.lower() == 's':
            roles='student'
            level='guest'
        else:
            roles='teacher'
            level='admin'
        User.create(email, password,'student','guest','bdadbk')
        print("root user created")
