import pymysql
from dbconnection import MySQL


class Message:
    def __init__(self, sender, receiver, content, datetime, is_liked=0, msg_id=0):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.datetime = datetime
        self.is_liked = is_liked  # Integer value, from sql (0 or 1)
        self.msg_id = msg_id


class Chat:
    def __init__(self):
        self.messages = {}
        self.key = 0
        self.name = ''
        self.surname = ''

    def __getitem__(self, item):
        return self.messages[item]

    def add(self, message):
        self.key += 1
        # message.key = self.key
        self.messages[self.key] = message

    def delete(self, index):
        del self.messages[index]

    def get_last(self):
        if self.key == 0:
            return 0
        return self.messages[self.key]

    def get_list(self):
        return sorted(self.messages.items())

    def is_empty(self):
        return self.key == 0


class Inbox:
    def __init__(self):
        self.chats = []

    def add(self, chat, participant):
        if len(chat.messages) != 0:
            self.chats.append((chat, participant))


def get_inbox(user_id):
    inbox = Inbox()
    names = []
    try:
        conn = pymysql.connect(host=MySQL.HOST, port=MySQL.PORT, user=MySQL.USER,
                               passwd=MySQL.PASSWORD, db=MySQL.DB, charset=MySQL.CHARSET)
        c = conn.cursor()

        sql = """SELECT c.user_id, c.participant_id,
                        c.in_out, m.content, m.message_datetime,
                        m.message_id, m.is_liked,
                        (CASE
                             WHEN u.user_type = 3
                                THEN uni.university_name
                             WHEN u.user_type = 2
                                THEN com.company_name
                             WHEN u.user_type = 1
                                THEN CONCAT_WS(' ', ud.user_name, ud.user_surname)
                             ELSE
                                NULL
                        END) AS name

                 FROM messages AS m
                 INNER JOIN conversations AS c
                    ON c.message_id = m.message_id
                 INNER JOIN users AS u
                    ON u.user_id = c.participant_id

                 LEFT JOIN user_detail AS ud
                    ON ud.user_id = c.participant_id
                 LEFT JOIN university_detail AS uni
                    ON uni.user_id = c.participant_id
                 LEFT JOIN company_detail AS com
                    ON com.user_id = c.participant_id

                 WHERE c.user_id = %d
                 ORDER BY c.participant_id;""" % user_id
        c.execute(sql)

        old_p = 0
        chat = Chat()

        for user, participant, in_out, content, msg_datetime, msg_id, is_liked, name in c:
            if in_out == 0:
                sender = user
                receiver = participant
            else:
                sender = participant
                receiver = user

            msg = Message(sender, receiver, content, msg_datetime,
                          is_liked=is_liked, msg_id=msg_id)

            if old_p == participant:
                chat.add(msg)
            else:
                if chat.key != 0:
                    inbox.add(chat, old_p)
                chat = Chat()
                chat.name = name
                # chat.surname = surname
                chat.add(msg)
            old_p = participant

        chat.name = name
        # chat.surname = surname
        inbox.add(chat, old_p)

        # # GET FOLLOWERS # #
        sql = """SELECT c.following_id,
                        (CASE
                             WHEN u.user_type = 3
                                THEN uni.university_name
                             WHEN u.user_type = 2
                                THEN com.company_name
                             WHEN u.user_type = 1
                                THEN CONCAT_WS(' ', ud.user_name, ud.user_surname)
                             ELSE
                                NULL
                        END) AS name

                 FROM connections AS c
                 INNER JOIN users AS u
                    ON u.user_id = c.following_id

                 LEFT JOIN user_detail AS ud
                    ON c.following_id = ud.user_id
                 LEFT JOIN university_detail AS uni
                    ON c.following_id = uni.user_id
                 LEFT JOIN company_detail AS com
                    ON c.following_id = com.user_id

                 WHERE c.user_id = %d
                 ORDER BY name;""" % user_id
        c.execute(sql)

        for name in c:
            names.append(name)

        c.close()
        conn.close()

    except Exception as e:
        print(str(e))

    return inbox, names


def send_message(user_id, participant_id, content, date):
    print('sending...')
    try:
        conn = pymysql.connect(host=MySQL.HOST, port=MySQL.PORT, user=MySQL.USER,
                               passwd=MySQL.PASSWORD, db=MySQL.DB, charset=MySQL.CHARSET)
        c = conn.cursor()
        f = '%Y-%m-%d %H:%M:%S'
        sql = """INSERT INTO messages(content, message_datetime, is_liked)
                              VALUES('%s', '%s', 0)""" % (content, date.strftime(f))
        c.execute(sql)
        print('message inserted')

        sql = """INSERT INTO conversations(user_id, participant_id, in_out, message_id)
           SELECT %d, %d, %d, MAX(message_id)
           FROM messages""" % (user_id, participant_id, 0)
        c.execute(sql)

        sql = """INSERT INTO conversations(user_id, participant_id, in_out, message_id)
           SELECT %d, %d, %d, MAX(message_id)
           FROM messages""" % (participant_id, user_id, 1)
        c.execute(sql)
        print('conversations inserted')

        conn.commit()
        c.close()
        conn.close()

    except Exception as e:
        print(str(e))


def delete_conversation(user_id, participant_id):
    try:
        conn = pymysql.connect(host=MySQL.HOST, port=MySQL.PORT, user=MySQL.USER,
                               passwd=MySQL.PASSWORD, db=MySQL.DB, charset=MySQL.CHARSET)
        c = conn.cursor()

        sql = """DELETE FROM conversations
                      WHERE (user_id = %d)
                        AND (participant_id = %d)""" % (user_id, participant_id)
        c.execute(sql)

        conn.commit()
        c.close()
        conn.close()
    except Exception as e:
        print(str(e))


def like_message(message_id):
    try:
        conn = pymysql.connect(host=MySQL.HOST, port=MySQL.PORT, user=MySQL.USER,
                               passwd=MySQL.PASSWORD, db=MySQL.DB, charset=MySQL.CHARSET)
        c = conn.cursor()

        sql = """UPDATE messages
                  SET is_liked = 1
                  WHERE message_id = %d""" % message_id
        c.execute(sql)

        conn.commit()
        c.close()
        conn.close()

    except Exception as e:
        print(str(e))


def unlike_message(message_id):
    try:
        conn = pymysql.connect(host=MySQL.HOST, port=MySQL.PORT, user=MySQL.USER,
                               passwd=MySQL.PASSWORD, db=MySQL.DB, charset=MySQL.CHARSET)
        c = conn.cursor()

        sql = """UPDATE messages
                  SET is_liked = 0
                  WHERE message_id = %d""" % message_id
        c.execute(sql)

        conn.commit()
        c.close()
        conn.close()

    except Exception as e:
        print(str(e))


def delete_message(message_id):
    try:
        conn = pymysql.connect(host=MySQL.HOST, port=MySQL.PORT, user=MySQL.USER,
                               passwd=MySQL.PASSWORD, db=MySQL.DB, charset=MySQL.CHARSET)
        c = conn.cursor()

        sql = """DELETE FROM conversations
                    WHERE message_id = %d""" % message_id
        c.execute(sql)

        sql = """DELETE FROM messages
                    WHERE message_id = %d""" % message_id
        c.execute(sql)

        conn.commit()
        c.close()
        conn.close()

    except Exception as e:
        print(str(e))


def get_name(user_id):
    try:
        conn = pymysql.connect(host=MySQL.HOST, port=MySQL.PORT, user=MySQL.USER,
                               passwd=MySQL.PASSWORD, db=MySQL.DB, charset=MySQL.CHARSET)
        c = conn.cursor()

        sql = """SELECT (CASE
                          WHEN u.user_type = 3
                              THEN uni.university_name
                          WHEN u.user_type = 2
                              THEN com.company_name
                          WHEN u.user_type = 1
                              THEN CONCAT_WS(' ', ud.user_name, ud.user_surname)
                          ELSE
                              NULL
                        END) AS name
                  FROM users AS u
                  LEFT JOIN user_detail AS ud
                      ON ud.user_id = u.user_id
                  LEFT JOIN university_detail AS uni
                      ON uni.user_id = u.user_id
                  LEFT JOIN company_detail AS com
                      ON com.user_id = u.user_id
                  WHERE u.user_id = %d""" % user_id
        c.execute(sql)

        for n in c:
            name = n

        c.close()
        conn.close()

        return name

    except Exception as e:
        print(str(e))
