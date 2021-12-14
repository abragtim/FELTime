#from os import X_OK
import sqlite3
#from types import NoneType
import datetime

subjects = []

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
        self.cursor.execute('SELECT user FROM users')
        s1 = self.cursor.fetchall()
        for profile in s1:
            try:
                self.cursor.execute("INSERT INTO 'progress' ('user') VALUES (?)",(profile[0],))
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
            self.cursor.execute("INSERT INTO 'users' ('user') VALUES (?)",(self.user,))
            self.cursor.execute(f"UPDATE users SET password = '{password}' WHERE user = '{self.user}'")
        except sqlite3.IntegrityError:
            print('Login už existuje. Zkuste jiný.')
            self.add_user(str(input('Login:')), str(input('Password:')))
        return self.connect.commit() 

    def user_check(self):
        '''Is *user* in the table?'''
        result = self.cursor.execute(f"SELECT id FROM users WHERE user = '{self.user}'")
        return bool(len(result.fetchall()))

    def get_user_id(self):
        '''Return user's id'''
        user_id = self.cursor.execute(f"SELECT id FROM users WHERE user = '{self.user}'")
        return user_id.fetchone()[0]

    def login(self):
        ''' Logining...'''
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
        '''Add subject to the user's subject-list'''
        try:
            for i in range(len(subjects)):
                del subjects[0]
            subject = str(input('Uveďte kod předmětu, který je zapsán v osobním rozvrhu:'))
            if subject not in subjects_list:
                raise sqlite3.OperationalError
            database.cursor.execute(f"UPDATE subjects SET {subject} = '1' WHERE user = '{login}'")
            database.connect.commit()
            data.add_subjective_opinion(subject)
            subjects_init()
            data.default_test_result()
            database.reconnect()
            print('Úspěšně')
        except sqlite3.OperationalError:
            print('ERROR: Takový predmět zapsat nelze.')

class Subject:
    def __init__(self,name, code, kred, stat):
        self.name = name
        self.code = code
        self.kred = kred #pocet kreditu
        self.stat = stat #statistika uspechu
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
        part = (func_results[subjects.index(self)] + subj_results[subjects.index(self)])/2    
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
            result = int(input('Jaký máte výsledek (v procentech) z tohoto předmětu?'))
            if result <= 0 or result > 100:
                raise sqlite3.OperationalError
            data.cursor.execute(f"UPDATE tests SET {predmet} = '{result}' WHERE user = '{login}'")
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
            opinion = int(input('Jaký máte pocit z tohoto předmětu? Ohodnoťte svůj pocit od 1 do 10 (1 - vůbec mi nejde; 10 - zvládám uplně všechno):'))
            if opinion <1 or opinion > 10:
                print('ERROR: Pocit musí být ohodnocen OD 1 DO 10!')
                raise sqlite3.OperationalError
            data.cursor.execute(f"UPDATE opinions SET {predmet} = '{opinion}' WHERE user = '{login}'")
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
            data.cursor.execute(f"SELECT {set} FROM opinions WHERE user = '{login}'")
            fetch = data.cursor.fetchone()[0]*10
            data.cursor.execute(f"UPDATE tests SET {set} = '{fetch}' WHERE user = '{login}'")
            data.connect.commit()

    def subjective(self): 
        '''Jadro v.2: subjective-part'''
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
        '''Jadro v.2: tests-part'''
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

    def add_progress(self,subject, seconds):
        '''Add progress of user in subject'''
        database.reconnect()
        data.cursor.execute(f"SELECT {subject.kod()} FROM progress WHERE user = '{login}'")
        fetch = data.cursor.fetchone()[0]
        if isinstance(fetch,type(None)) == True:
            fetch = 0
        seconds = int(fetch) + seconds
        data.cursor.execute(f"UPDATE progress SET {subject.kod()} = '{seconds}' WHERE user = '{login}'")
        data.connect.commit()
        database.reconnect()

    def get_progress_information(self):
        '''Get user's progress information'''
        database.reconnect()
        sum = 0
        for subject in subjects:
            data.cursor.execute(f"SELECT {subject.kod()} FROM progress WHERE user = '{login}'")
            subject.progress = data.cursor.fetchone()[0]
            sum = sum + subject.progress
        return sum

################################################################################

'''Subjects: *kod predmetu* = Subject(*pocet kreditu*, *procent NEuspechu*):'''
BAB31AF1 = Subject('Základy anatomie a fyziologie I','BAB31AF1', 4, 14); 
B0B01LAGA = Subject('Lineární algebra','B0B01LAGA', 7, 47.08); 
B2B15UELA = Subject('Úvod do elektrotechniky','B2B15UELA', 4, 16.67); 
B0B01MA1A = Subject('Matematická analýza I','B0B01MA1A', 6, 44.64); 
BAB37ZPR = Subject('Základy programování','BAB37ZPR', 6, 22.78); 
subjects_list = [BAB31AF1, B0B01LAGA, B0B01MA1A, B2B15UELA,BAB37ZPR]

#################################################################################
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

def organize():
    '''Organizece casu'''
    #Priprava predmetu k organizaci:
    try:
        allhours = int(input('Kolik hodin v týdnu budete studovat?: '))
        if allhours <= 0:
            raise ValueError
    except ValueError:
        print('ERROR: Používejte celá kladná čísla.')
        return None
    file = open('organize.txt','w')
    file.write('')
    file.close()
    file = open('organize.txt','a')
    for subject in subjects:
        dluh = (subject.progress_check() - 100)/100*allhours
        subject.time = allhours*subject.jadro_v2()/100 - dluh
        if subject.progress_check() == 0:
            subject.time = allhours*subject.jadro_v2()/100
        subject.number = int(subject.time//1.5)
        file.write('{}:{}-{}-dd-hh-mm \n'.format(subject.name, datetime.datetime.today().year, datetime.datetime.today().month)*subject.number)
    file.close()
    input('Proveďte změny v soubru organize.txt. Po ukončení stiskněte ENTER')
    #Analýza po organizaci:
    try:
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
        def dates_sorting(dates):
            sorted_dates = [[], [], [], [], [], [], []]
            i = 0
            pamet = None
            activate_pamet = False
            while True:
                if i == len(dates)-1:
                    i = 0
                    activate_pamet = True
                if dates[i][1] > dates[i+1][1]:
                    dates[i], dates[i+1] = dates[i+1], dates[i]
                    i += 1
                else:
                    i += 1
                if [dates] == pamet:
                    break
                if activate_pamet == True:
                    pamet = [dates]
                    activate_pamet == False
            for m in range(7):
                for i in range(len(dates)):
                    if datetime.datetime.weekday(dates[i][1]) == m:
                        sorted_dates[m].append(dates[i])
            del dates, pamet, activate_pamet, i
            return sorted_dates
        sorted_dates = dates_sorting(dates)
    except ValueError:
        print('ERROR: Chyba úprav v souboru.')
        return None
    except IndexError:
        print('ERROR: Chyba úprav v souboru.')
        return None
    #Add to calendar.txt
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
    '''Study stopwatch'''
    today = datetime.datetime.today()
    today = datetime.datetime(today.year, today.month, today.day, today.hour, today.minute, second=0)
    status  = True
    with open('calendar.txt','r') as file:
        lines = file.readlines()
        ask = None
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
                start_date = datetime.datetime(int(delta_cal[:delta_cal.index('-')]),int(delta_cal[delta_cal.index('-')+1:delta_cal.index('-',delta_cal.index('-')+1)]),int(delta_cal[delta_cal.index('-',delta_cal.index('-')+1)+1:delta_cal.index(' ')]),int(delta_cal[delta_cal.index(' ')+1:delta_cal.index(' ')+3]),int(delta_cal[delta_cal.index(' ')+4:delta_cal.index(' ')+6]),int(delta_cal[delta_cal.index(' ')+7:delta_cal.index(' ')+9]))
                delta_cal = delta_cal.replace(str(start_date),'')
                delta_cal = delta_cal[3:]
                finish_date = datetime.datetime(int(delta_cal[:delta_cal.index('-')]),int(delta_cal[delta_cal.index('-')+1:delta_cal.index('-',delta_cal.index('-')+1)]),int(delta_cal[delta_cal.index('-',delta_cal.index('-')+1)+1:delta_cal.index(' ')]),int(delta_cal[delta_cal.index(' ')+1:delta_cal.index(' ')+3]),int(delta_cal[delta_cal.index(' ')+4:delta_cal.index(' ')+6]),int(delta_cal[delta_cal.index(' ')+7:delta_cal.index(' ')+9]))
                if bool(today > start_date) == True and bool(today < finish_date) == True:
                    current_activity = line[line.index('|')+2:line.index(':',line.index('|'))]
                    for subject in subjects:
                        if current_activity == subject.name:
                            current_activity = subject
                            ask = str(input('Váše aktuální aktivita je {}?(yes/no):'.format(current_activity.name)))
        if ask != 'yes':
            ask = 'no'
        if ask == 'no':
            while status == True:
                ask = str(input('Uveďte název předmětu, nad kterým teď pracujete?:'))
                for subject in subjects:
                    if bool(ask == subject.name) == True:
                        current_activity = subject
                        status = False
                if status == False:
                    status = False
                    break
                print('Nenašli jmse takový název. Zkuste znovu.')
    start_time = today
    input('Hodně štěstí ve studiu! Po ukončení studia stiskňete ENTER.')
    finish_time = datetime.datetime.today()
    delta_time = finish_time - start_time
    print('Čas studia: {}'.format(delta_time))
    delta_time = str(delta_time)
    delta_time = delta_time[:delta_time.index('.')]
    delta_time = delta_time.split(':')
    delta_time = [int(cas) for cas in delta_time]
    delta_time = delta_time[0] * 60 + delta_time[1] * 60 + delta_time[2]
    data.add_progress(current_activity,delta_time)

def progress():
    for subject in subjects:
        print(int(subject.progress_check()//1))

def menu():
    '''Interactive menu'''
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
            print('> [{}%] {} ({}):'.format(int(subject.progress_check()//1),subject.name, subject.code),subject.jadro_v2(),'%')
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
            work()
        if cmd =='/exit':
            exit()

#try:
menu()
#except:
    #print('ERROR')
