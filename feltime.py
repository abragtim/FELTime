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
BAB31AF1 = Subject('Základy anatomie a fyziologie I','BAB31AF1', 4, 14); 
B0B01LAGA = Subject('Lineární algebra','B0B01LAGA', 7, 47.08); 
B2B15UELA = Subject('Úvod do elektrotechniky','B2B15UELA', 4, 16.67); 
B0B01MA1A = Subject('Matematická analýza','B0B01MA1A', 6, 44.64); 
BAB37ZPR = Subject('Základy programování','BAB37ZPR', 6, 22.78); 
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

import datetime
def organize():
    allhours = int(input('Kolik hodin v týdnu budete studovat?:'))
    file = open('organize.txt','w')
    file.write('')
    file.close()
    file = open('organize.txt','a')
    for subject in subjects:
        subject.time = allhours*subject.jadro_v2()/100
        subject.number = int(subject.time//1.5)
        subject.list = []
        subject.list.append(subject.time)
        file.write('{}:yyyy-mm-dd-hh-mm \n'.format(subject.name)*subject.number)
    file.close()
    input('Proveďte změny v soubru organize.txt. Po ukončení stiskněte ENTER')
    delta = datetime.timedelta(hours = 1,minutes = 30)
    file = open('organize.txt','r')
    dates = []
    while True:
        line = file.readline()
        try:
            lom = line.index(':')
        except ValueError:
            break
        name = line[:lom]
        date_vstup = line[lom+1:].replace('-',' ').split()
        date = datetime.datetime(int(date_vstup[0]), int(date_vstup[1]), int(date_vstup[2]), int(date_vstup[3]), int(date_vstup[4]))
        dates.append([name,date])
    file.close()

    dates.sort()
    sorted_dates = [[],[],[],[],[],[],[]]
    for i in range(len(dates)):
        if datetime.datetime.weekday(dates[i][1]) == 0:
            sorted_dates[0].append(dates[i])
        if datetime.datetime.weekday(dates[i][1]) == 1:
            sorted_dates[1].append(dates[i])
        if datetime.datetime.weekday(dates[i][1]) == 2:
            sorted_dates[2].append(dates[i])
        if datetime.datetime.weekday(dates[i][1]) == 3:
            sorted_dates[3].append(dates[i])
        if datetime.datetime.weekday(dates[i][1]) == 4:
            sorted_dates[4].append(dates[i])
        if datetime.datetime.weekday(dates[i][1]) == 5:
            sorted_dates[5].append(dates[i])
        if datetime.datetime.weekday(dates[i][1]) == 6:
            sorted_dates[6].append(dates[i])
        else:
            continue

    cal = open('calendar.txt','w')
    weekdays = ['MONDAY','TUESDAY','WENSDAY','THURSADY','FRIDAY','SATURDAY','SUNDAY']
    for j in range(7):
        cal.write('{}:\n'.format(weekdays[j]))
        cal.write('--------------------------------------------------------------------\n')
        for i in range(len(sorted_dates[j])):
            minute = sorted_dates[j][i][1].minute
            if len(str(minute)) == 1:
                minute = '0' + str(minute)
            cal.write('   {}:{} | {}: {} - {}\n'.format(sorted_dates[j][i][1].hour,minute,sorted_dates[j][i][0], sorted_dates[j][i][1],sorted_dates[j][i][1] + delta))
    cal.close()
    print('Váš rozvhrh je v souboru calendar.txt')

def work():
    today = datetime.datetime.today()
    today = datetime.datetime(today.year, today.month, today.day, today.hour, today.minute, second=0)
    with open('calendar.txt','r') as file:
        lines = file.readlines()
        for line in lines:
            try:
                line.index(str(today.year))
            except ValueError:
                continue
            if bool(line.index(str(today.year))) == True:
                delta_cal = line[line.index(str(today.year)):]
                i = 0
                while i != -1:
                    try:
                       int(delta_cal[len(delta_cal)-2-i])
                       i = -2
                    except ValueError:
                        pass
                    finally:
                        i = i + 1
                delta_cal = delta_cal[0:len(delta_cal)-2-i]
                # CONTINUE

def menu():
    while True:
        """Client autorization"""   
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
        if cmd == '/organize':
            organize()
        if cmd == '/work':
            pass
        if cmd =='/exit':
            exit()

work()
#menu()