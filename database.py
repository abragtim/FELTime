from subjects import *
import sqlite3


class DATABASE:
    def __init__(self, file_db):
        self.file_db = file_db
        self.connect = sqlite3.connect(file_db)
        self.cursor = self.connect.cursor()

    def reconnect(self):
        '''Recconectiont database'''
        self.close()
        self.__init__('{}'.format(self.file_db))

    def synch_tables(self):
        '''Synchronization tables from users -> ***'''
        self.cursor.execute('SELECT user FROM users')
        s1 = self.cursor.fetchall()
        for profile in s1:
            try:
                self.cursor.execute(
                    "INSERT INTO 'tests' ('user') VALUES (?)", (profile[0],))
                self.connect.commit()
            except sqlite3.IntegrityError:
                pass
        self.cursor.execute('SELECT user FROM users')
        s1 = self.cursor.fetchall()
        for profile in s1:
            try:
                self.cursor.execute(
                    "INSERT INTO 'subjects' ('user') VALUES (?)", (profile[0],))
                self.connect.commit()
            except sqlite3.IntegrityError:
                pass
        self.cursor.execute('SELECT user FROM users')
        s1 = self.cursor.fetchall()
        for profile in s1:
            try:
                self.cursor.execute(
                    "INSERT INTO 'opinions' ('user') VALUES (?)", (profile[0],))
                self.connect.commit()
            except sqlite3.IntegrityError:
                pass
        self.cursor.execute('SELECT user FROM users')
        s1 = self.cursor.fetchall()
        for profile in s1:
            try:
                self.cursor.execute(
                    "INSERT INTO 'progress' ('user') VALUES (?)", (profile[0],))
                self.connect.commit()
            except sqlite3.IntegrityError:
                pass

    def close(self):
        self.connect.close()


class Client(DATABASE):
    def __init__(self, file_db):
        super().__init__(file_db)

    def add_user(self, user, password):
        '''Add user to the DB'''
        self.user = user
        try:
            self.cursor.execute(
                "INSERT INTO 'users' ('user') VALUES (?)", (self.user,))
            self.cursor.execute(
                f"UPDATE users SET password = '{password}' WHERE user = '{self.user}'")
        except sqlite3.IntegrityError:
            print('Login už existuje. Zkuste jiný.')
            self.add_user(str(input('Login:')), str(input('Password:')))
        return self.connect.commit()

    def user_check(self):
        '''Is *user* in the table?'''
        result = self.cursor.execute(
            f"SELECT id FROM users WHERE user = '{self.user}'")
        return bool(len(result.fetchall()))

    def get_user_id(self):
        '''Return user's id'''
        user_id = self.cursor.execute(
            f"SELECT id FROM users WHERE user = '{self.user}'")
        return user_id.fetchone()[0]

    def login(self):
        ''' Logining...'''
        global login
        login = str(input('Login:'))
        password = str(input('Password:'))
        self.cursor.execute(f"SELECT user FROM users WHERE user = '{login}'")
        if self.cursor.fetchone() != None:
            self.cursor.execute(
                f"SELECT password FROM users WHERE user = '{login}'")
            check_password = str(self.cursor.fetchone()[0])
            if check_password == password:
                return login
            else:
                print('Nespravné heslo.')
                self.login()
        else:
            print('Takový login neexistuje. Udělejte registaci:')
            self.add_user(str(input('Login:')), str(input('Password:')))
        return None

    def add_subjects(self):
        '''Add subject to the user's subject-list'''
        try:
            for i in range(len(subjects)):
                del subjects[0]
            subject = str(
                input('Uveďte kod předmětu, který je zapsán v osobním rozvrhu:'))
            subjects_list_codes_str = [sub.code for sub in subjects_list]
            if subject not in subjects_list_codes_str:
                raise sqlite3.OperationalError
            database.cursor.execute(
                f"UPDATE subjects SET {subject} = '1' WHERE user = '{login}'")
            database.connect.commit()
            data.add_subjective_opinion(subject)
            subjects_init()
            data.default_test_result()
            database.reconnect()
            print('Úspěšně')
        except sqlite3.OperationalError:
            print('ERROR: Takový predmět zapsat nelze.')


class Subject:
    def __init__(self, name, code, kred, stat):
        self.name = name
        self.code = code
        self.kred = kred  # pocet kreditu
        self.stat = stat  # statistika uspechu
        self.progress = 0

    def kod(self):
        '''Return subject's code'''
        return self.code

    def kredits(self):
        '''Return the number of kredits'''
        return self.kred

    def statistics(self):
        '''Return % of failers'''
        return self.stat

    def jadro_v1_kred(self):
        '''Jadro v.1: kredit-part'''
        kredit_part = self.kredits()/allkredits*100
        return kredit_part

    def jadro_v1_stat(self):
        '''Jadro v.2: failers-part'''
        statistics_part = self.statistics()/allstats*100
        return statistics_part

    def jadro_v1(self):
        '''Jadro v.1'''
        part = ((self.jadro_v1_kred() + self.jadro_v1_stat())/2)
        return part

    def jadro_v2(self):
        '''Jadro v.2'''
        a = data.tests()
        b = data.subjective()
        func_results = []
        subj_results = []
        for i in a:
            func_results.append(a[i])
        for i in a:
            subj_results.append(b[i])
        part = (func_results[subjects.index(self)] +
                subj_results[subjects.index(self)])/2
        return part

    def progress_check(self):
        '''Cheking the progress'''
        sum = data.get_progress_information()
        if sum != 0:
            self.progress = self.progress*100/sum
            procent_progress = self.progress*100/self.jadro_v2()
        else:
            self.progress = 0
            procent_progress = 0
        return procent_progress


class Data(DATABASE):
    def __init__(self, file_db):
        super().__init__(file_db)

    def add_test_result(self):
        ''' Add test result'''
        try:
            database.reconnect()
            predmet = str(input('Uveďte kod předmětu:'))
            result = int(
                input('Jaký máte výsledek (v procentech) z tohoto předmětu?'))
            if result <= 0 or result > 100:
                raise sqlite3.OperationalError
            data.cursor.execute(
                f"UPDATE tests SET {predmet} = '{result}' WHERE user = '{login}'")
            data.connect.commit()
        except sqlite3.OperationalError:
            print('ERROR: Výsledek nebyl zapsán.')
            return None
        except ValueError:
            print('ERROR: Používejte celá čísla.')
            return None

    def add_subjective_opinion(self, predmet=None):
        '''Add subjective feelings'''
        try:
            if predmet == None:
                predmet = str(input('Uveďte kod předmětu:'))
            database.reconnect()
            opinion = int(input(
                'Jaký máte pocit z tohoto předmětu? Ohodnoťte svůj pocit od 1 do 10 (1 - vůbec mi nejde; 10 - zvládám uplně všechno):'))
            if opinion < 1 or opinion > 10:
                print('ERROR: Pocit musí být ohodnocen OD 1 DO 10!')
                raise sqlite3.OperationalError
            data.cursor.execute(
                f"UPDATE opinions SET {predmet} = '{opinion}' WHERE user = '{login}'")
            data.connect.commit()
        except sqlite3.OperationalError:
            print('ERROR: Pocit nebyl zapsán.')
            return None
        except ValueError:
            print('ERROR: Používejte celá čísla.')
            return None

    def default_test_result(self):
        '''Before the first test: test_result = feelings * 10'''
        database.reconnect()
        for subject in subjects:
            set = subject.kod()
            data.cursor.execute(
                f"SELECT {set} FROM opinions WHERE user = '{login}'")
            fetch = data.cursor.fetchone()[0]*10
            data.cursor.execute(
                f"UPDATE tests SET {set} = '{fetch}' WHERE user = '{login}'")
            data.connect.commit()

    def subjective(self):
        '''Jadro v.2: subjective-part'''
        scores = []
        for subject in subjects:
            data.cursor.execute(
                f"SELECT {subject.kod()} FROM opinions WHERE user = '{login}'")
            fetch = data.cursor.fetchone()[0]
            subject.score = fetch
            scores.append(subject.score)
        for subject in subjects:
            subject.procent = subject.score/sum(scores)*100
        goal_procent = 100/len(scores)
        parts_subjectives = {}
        for subject in subjects:
            subject.delta_multiply = 1 + (goal_procent - subject.procent)/100
            part_subjective = subject.jadro_v1() * subject.delta_multiply
            parts_subjectives[subject] = part_subjective
        return parts_subjectives

    def tests(self):
        '''Jadro v.2: tests-part'''
        bods = []
        for subject in subjects:
            data.cursor.execute(
                f"SELECT {subject.kod()} FROM tests WHERE user = '{login}'")
            fetch = data.cursor.fetchone()[0]
            subject.bod = fetch
            bods.append(subject.bod)
        for subject in subjects:
            subject.procent = subject.bod/sum(bods)*100
        goal_procent = 100/len(bods)
        parts_subjectives = {}
        for subject in subjects:
            subject.delta_multiply = 1 + (goal_procent - subject.procent)/100
            part_subjective = subject.jadro_v1() * subject.delta_multiply
            parts_subjectives[subject] = part_subjective
        return parts_subjectives

    def add_progress(self, subject, seconds):
        '''Add progress of user in subject'''
        database.reconnect()
        data.cursor.execute(
            f"SELECT {subject.kod()} FROM progress WHERE user = '{login}'")
        fetch = data.cursor.fetchone()[0]
        if isinstance(fetch, type(None)) == True:
            fetch = 0
        seconds = int(fetch) + seconds
        data.cursor.execute(
            f"UPDATE progress SET {subject.kod()} = '{seconds}' WHERE user = '{login}'")
        data.connect.commit()
        database.reconnect()

    def get_progress_information(self):
        '''Get user's progress information'''
        database.reconnect()
        sum = 0
        for subject in subjects:
            data.cursor.execute(
                f"SELECT {subject.kod()} FROM progress WHERE user = '{login}'")
            subject.progress = data.cursor.fetchone()[0]
            sum = sum + subject.progress
        return sum


database = DATABASE('database.db')
client = Client('database.db')
data = Data('database.db')


def subjects_init():
    '''Inicialization of user's subjects'''
    database.cursor.execute(f"SELECT * FROM subjects WHERE user = '{login}'")
    k = -1
    for bod in database.cursor.fetchall()[0]:
        k = k + 1
        if k == 0 or k == 1:
            pass
        elif bod == None:
            pass
        elif bod == 1:
            subjects.append(subjects_list[k-2])
    global allkredits
    allkredits = sum([subject.kredits() for subject in subjects])
    global allstats
    allstats = sum([subject.statistics() for subject in subjects])
