import sqlite3

subjects = []

class DATABASE:

    def __init__(self, file_db):
        self.connect = sqlite3.connect(file_db)
        self.cursor = self.connect.cursor()

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
            self.cursor.execute(f"UPDATE users SET password = {password} WHERE user = '{self.user}'") # Работает только с числами
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

class Subject:
    def __init__(self,name, code, kred, stat):
        self.name = name
        self.code = code
        self.kred = kred #pocet kreditu
        self.stat = stat #statistika uspechu

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
        a = tests()
        b = subjective()
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

    def subjective(): 
        scores = []
        for subject in subjects:
            subject.score = int(input('Jaký máte pocit ze předmětu {}? Ohodnoťte svůj pocit od 1 do 10 (1 - vůbec mi nejde; 10 - zvládám uplně všechno):'.format(subject.name)))
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

    def tests(): 
        bods = []
        for subject in subjects:
            subject.bod = int(input('Jaký máte poslední výsledek ze předmětu "{}"? Uveďte výsledek v procentech (P.S. Jestli nemáte žádný výsledek, uveďte v procentech svůj subjektivní pocit ze předmětu):'.format(subject.name)))
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

    def add_subject(self,subject):
        ''' Klient přidává svoje předměty'''
        

    

################################################################################

'''Subjects: *kod predmetu* = Subject(*pocet kreditu*, *procent NEuspechu*):'''
laga = Subject('Lineární algebra','laga', 7, 40); subjects.append(laga)
uela = Subject('Úvod do elektrotechniky','uela', 4, 5); subjects.append(uela)
ma1a = Subject('Matematická analýza','ma1a', 6, 20); subjects.append(ma1a)
subjects_list = [laga, uela, ma1a]

allkredits = 7 + 4 + 6 # ПОСЧИТАТЬ ЧЕРЕЗ ИНИЦИАЛИЗОВАННЫЕ ПРЕДМЕТЫ
allstats = 40 + 5 + 20 # -//-

#################################################################################
database = DATABASE('database.db')
client = Client('database.db')
data = Data('database.db')

def subjects_init():
    database.cursor.execute(f"SELECT * FROM subjects WHERE user = '{login}'")
    k = -1
    for bod in database.cursor.fetchall()[0]:
        k = k + 1
        if k == 0 or k == 1:
            pass
        elif bod == None:
            pass
        else:
            subjects.append(subjects_list[k-2])



while True:
    """Client autorization"""    
    #logining = client.login()
    autorize = client.login()
    if str(autorize) == login:
        print('Hello, {}'.format(autorize))
        database.synch_tables()
        subjects_init()
        break

while True:
    pass
    cmd = str(input('cmd:'))