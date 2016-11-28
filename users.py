import pymysql
from dbconnection import MySQL


class Users:
    def __init__(self):
        self.users = {}
        self.key = 0

    def add_user(self, user):
        self.key += 1
        # user.key = self.key
        self.users[self.key] = user

    def get_user(self, key):
        return self.users[key]

    def get_users(self):
        return sorted(self.users.items())


class User:
    def __init__(self, user_id="", user_type="", user_email="", user_password="", user_name="", user_surname="",
                 user_birth="", user_phone="", user_address=""):
        self.user_id = user_id
        self.user_type = user_type
        self.user_email = user_email
        self.user_password = user_password
        self.user_name = user_name
        self.user_surname = user_surname
        self.user_birth = user_birth
        self.user_phone = user_phone
        self.user_address = user_address

        if user_type == 1:
            self.add_user_detail(user_name, user_surname, user_birth, user_phone, user_address)
        elif user_type == 2:
            self.add_company_detail(user_name, user_phone, user_address)
        elif user_type == 3:
            self.add_university_detail(user_name, user_address)

    def add_user_detail(self, user_name="", user_surname="", user_birth="", user_phone="", user_address=""):
        self.user_name = user_name
        self.user_surname = user_surname
        self.user_birth = user_birth
        self.user_phone = user_phone
        self.user_address = user_address
        print('add user detail')

    def add_company_detail(self, user_name="", user_phone="", user_address=""):
        self.user_name = user_name
        self.user_phone = user_phone
        self.user_address = user_address
        print('add company detail')

    def add_university_detail(self, user_name="", user_address=""):
        self.user_name = user_name
        self.user_address = user_address
        print('add university detail')


def user_show(user_id):
    user = User()
    try:
        conn = pymysql.connect(host=MySQL.HOST, port=MySQL.PORT, user=MySQL.USER,
                               passwd=MySQL.PASSWORD, db=MySQL.DB, charset=MySQL.CHARSET)
        c = conn.cursor()
        sql = """SELECT user_id, user_type, user_email, user_password FROM users WHERE  user_id = %d """ % (
            int(user_id))

        c.execute(sql)
        print(user_id)
        for row in c:
            user_id, user_type, user_email, user_password = row
            if user_type == 1:
                sql = """SELECT user_name, user_surname, user_birth, user_phone, user_address
                          FROM user_detail WHERE  user_id = %d """ % (
                    int(user_id))

                c.execute(sql)

            elif user_type == 2:
                sql = """SELECT company_name, company_phone, company_address
                          FROM company_detail WHERE company_id = %d """ % (
                    int(user_id))

                c.execute(sql)

            elif user_type == 3:
                sql = """SELECT university_name, university_address
                          FROM university_detail WHERE  university_id = %d """ % (
                    int(user_id))

                c.execute(sql)
            user = User(user_id=user_id, user_type=user_type, user_email=user_email, user_password=user_password)

        c.close()
        conn.close()

    except Exception as e:
        print(str(e))
    print(user)
    return user


def user_edit(user_id, user_name, user_surname):
    try:
        conn = pymysql.connect(host=MySQL.HOST, port=MySQL.PORT, user=MySQL.USER,
                               passwd=MySQL.PASSWORD, db=MySQL.DB, charset=MySQL.CHARSET)
        c = conn.cursor()
        sql = """UPDATE users SET user_name = '%s', user_surname = '%s'  WHERE user_id = %d """ % (
            user_name, user_surname, int(user_id))

        c.execute(sql)
        conn.commit()
        c.close()
        conn.close()

    except Exception as e:
        print(str(e))


def user_delete(user_id):
    try:
        conn = pymysql.connect(host=MySQL.HOST, port=MySQL.PORT, user=MySQL.USER,
                               passwd=MySQL.PASSWORD, db=MySQL.DB, charset=MySQL.CHARSET)
        c = conn.cursor()
        sql = """DELETE FROM users WHERE user_id = (%d) """ % (int(user_id))
        c.execute(sql)
        conn.commit()
        c.close()
        conn.close()

    except Exception as e:
        print(str(e))
