import sqlite3

subjects = []

class DATABASE:

    def __init__(self, file_db):
        self.file_db = file_db
        self.connect = sqlite3.connect(file_db)
        self.cursor = self.connect.cursor()

    def reconnect(self):
        self.close()
        self.__init__('{}'.format(self.file_db))

    def synch_tables(self):
        self.cursor.execute('SELECT user FROM users')
        s1 = self.cursor.fetchall()
        for profile in s1:
            try:
                self.cursor.execute("INSERT INTO 'tests' ('user') VALUES (?)",(profile[0],))
                self.connect.commit()
            except sqlite3.IntegrityError:
                pass
        self.cursor.execute('SELECT user FROM users')
        s1 = self.cursor.fetchall()
        for profile in s1:
            try:
                self.cursor.execute("INSERT INTO 'subjects' ('user') VALUES (?)",(profile[0],))
                self.connect.commit()
            except sqlite3.IntegrityError:
                pass
        self.cursor.execute('SELECT user FROM users')
        s1 = self.cursor.fetchall()
        for profile in s1:
            try:
                self.cursor.execute("INSERT INTO 'opinions' ('user') VALUES (?)",(profile[0],))
                self.connect.commit()
            except sqlite3.IntegrityError:
                pass

    def close(self):
        self.connect.close()

class Client(DATABASE):
    def __init__(self, file_db):
        super().__init__(file_db)

    def add_user(self, user, password):
        self.user = user
        try: 
            self.cursor.execute("INSERT INTO 'users' ('user') VALUES (?)",(self.user,))
            self.cursor.execute(f"UPDATE users SET password = '{password}' WHERE user = '{self.user}'")
        except sqlite3.IntegrityError:
            print('Login už existuje. Zkuste jiný.')
            self.add_user(str(input('Login:')), str(input('Password:')))
        return self.connect.commit() 

    def user_check(self):
        result = self.cursor.execute(f"SELECT id FROM users WHERE user = '{self.user}'")
        return bool(len(result.fetchall()))

    def get_user_id(self):
        user_id = self.cursor.execute(f"SELECT id FROM users WHERE user = '{self.user}'")
        return user_id.fetchone()[0]

    def login(self):
        global login
        login = str(input('Login:'))
        password = str(input('Password:'))
        self.cursor.execute(f"SELECT user FROM users WHERE user = '{login}'")
        if self.cursor.fetchone() != None:
            self.cursor.execute(f"SELECT password FROM users WHERE user = '{login}'")
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
        for i in range(len(subjects)):
            del subjects[0]
        subject = str(input('Uveďte kod předmětu, který je zapsán v osobním rozvrhu:'))
        database.cursor.execute(f"UPDATE subjects SET {subject} = '1' WHERE user = '{login}'")
        database.connect.commit()
        data.add_subjective_opinion(subject)
        subjects_init()
        data.default_test_result()
        database.reconnect()
        print('Úspěšně')

class Subject:
    def __init__(self,name, code, kred, stat):
        self.name = name
        self.code = code
        self.kred = kred #pocet kreditu
        self.stat = stat #statistika uspechu

    def kod(self):
        return self.code

    def kredits(self):
        return self.kred

    def statistics(self):
        return self.stat

    def jadro_v1_kred(self):
        kredit_part = self.kredits()/allkredits*100
        return kredit_part 

    def jadro_v1_stat(self): 
        statistics_part = self.statistics()/allstats*100
        return statistics_part

    def jadro_v1(self):
        part = ((self.jadro_v1_kred() + self.jadro_v1_stat())/2)
        return part

    def jadro_v2(self):
        a = data.tests()
        b = data.subjective()
        func_results = []
        subj_results = []
        for i in a:
            func_results.append(a[i])
        for i in a:
            subj_results.append(b[i])    
        part = (func_results[subjects.index(self)] + subj_results[subjects.index(self)])/2    
        return part 

class Data(DATABASE):
    def __init__(self, file_db):
        super().__init__(file_db)

    def add_test_result(self):
        database.reconnect()
        predmet = str(input('Uveďte kod předmětu:'))
        result = int(input('Jaký máte výsledek (v procentech) z tohoto předmětu?'))
        data.cursor.execute(f"UPDATE tests SET {predmet} = '{result}' WHERE user = '{login}'")
        data.connect.commit()

    def add_subjective_opinion(self, predmet=None):
        if predmet == None:
            predmet = str(input('Uveďte kod předmětu:'))
        database.reconnect()
        opinion = int(input('Jaký máte pocit z tohoto předmětu? Ohodnoťte svůj pocit od 1 do 10 (1 - vůbec mi nejde; 10 - zvládám uplně všechno):'))
        data.cursor.execute(f"UPDATE opinions SET {predmet} = '{opinion}' WHERE user = '{login}'")
        data.connect.commit()

    def default_test_result(self): 
        database.reconnect()
        for subject in subjects:
            set = subject.kod()
            data.cursor.execute(f"SELECT {set} FROM opinions WHERE user = '{login}'")
            fetch = data.cursor.fetchone()[0]*10
            data.cursor.execute(f"UPDATE tests SET {set} = '{fetch}' WHERE user = '{login}'")
            data.connect.commit()

    def subjective(self): 
        scores = []
        for subject in subjects:
            data.cursor.execute(f"SELECT {subject.kod()} FROM opinions WHERE user = '{login}'")
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
        bods = []
        for subject in subjects:
            data.cursor.execute(f"SELECT {subject.kod()} FROM tests WHERE user = '{login}'")
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
        

################################################################################

'''Subjects: *kod predmetu* = Subject(*pocet kreditu*, *procent NEuspechu*):'''
BAB31AF1 = Subject('Základy anatomie a fyziologie I','BAB31AF1', 4, 10); 
B0B01LAGA = Subject('Lineární algebra','B0B01LAGA', 7, 30); 
B2B15UELA = Subject('Úvod do elektrotechniky','B2B15UELA', 4, 10); 
B0B01MA1A = Subject('Matematická analýza','B0B01MA1A', 6, 17); 
BAB37ZPR = Subject('Základy programování','BAB37ZPR', 6, 10); 
subjects_list = [BAB31AF1, B0B01LAGA, B0B01MA1A, B2B15UELA,BAB37ZPR]

#################################################################################
database = DATABASE('database.db')
client = Client('database.db')
data = Data('database.db')

def subjects_init(): # Доделать
    '''Inicializace svých předmětů userem'''
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
    allstats = sum([subject.statistics() for subject in subjects]) # ПРОВЕРИТЬ ПОТОМ. ЗДЕСЬ СУММА НЕУСПЕХА

while True:
    """Client autorization"""    
    #logining = client.login()
    autorize = client.login()
    if str(autorize) == login:
        print('Hello, {}'.format(autorize))
        database.synch_tables()
        subjects_init()
        database.reconnect()
        break

while True:
    for subject in subjects:
        print('> {}:'.format(subject.name),subject.jadro_v2(),'%')
    cmd = str(input('cmd:'))
    if cmd == '/zapis':
        client.add_subjects()
        database.reconnect()
    if cmd == '/test_result':
        data.add_test_result()
        database.reconnect()
    if cmd == '/opinion':
        data.add_subjective_opinion()
        database.reconnect()
    if cmd =='/exit':
        exit()