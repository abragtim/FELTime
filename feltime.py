import sqlite3
import datetime
from database import *


def main():
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
            print('> [{}%] {} ({}):'.format(int(subject.progress_check()//1),
                                            subject.name,
                                            subject.code),
                  subject.jadro_v2(), '%')
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
        if cmd == '/exit':
            exit()
        if cmd == '/help':
            print('''
            /zapis - zapsat předmět;
            /test_result - přidat výsledek testu;
            /opinion - přidat subjektivní pocit z předmětu;
            /organize - výtvořit plan na týden;
            /work - progress timer;
            /exit - ukončit program.
            ''')
            input()


def organize():
    '''Organizece casu'''
    # Priprava predmetu k organizaci:
    try:
        allhours = int(input('Kolik hodin v týdnu budete studovat?: '))
        if allhours <= 0:
            raise ValueError
    except ValueError:
        print('ERROR: Používejte celá kladná čísla.')
        return None
    file = open('organize.txt', 'w')
    file.write('')
    file.close()
    file = open('organize.txt', 'a')
    for subject in subjects:
        dluh = (subject.progress_check() - 100)/100*allhours
        subject.time = allhours*subject.jadro_v2()/100 - dluh
        if subject.progress_check() == 0:
            subject.time = allhours*subject.jadro_v2()/100
        subject.number = int(subject.time//1.5)
        file.write('{}:{}-{}-dd-hh-mm \n'.format(subject.name,
                   datetime.datetime.today().year, datetime.datetime.today().month)*subject.number)
    file.close()
    input('Proveďte změny v soubru organize.txt. Po ukončení stiskněte ENTER')
    # Analýza po organizaci:
    try:
        delta = datetime.timedelta(hours=1, minutes=30)
        file = open('organize.txt', 'r')
        dates = []
        while True:
            line = file.readline()
            try:
                lom = line.index(':')
            except ValueError:
                break
            name = line[:lom]
            date_vstup = line[lom+1:].replace('-', ' ').split()
            date = datetime.datetime(int(date_vstup[0]), int(date_vstup[1]), int(
                date_vstup[2]), int(date_vstup[3]), int(date_vstup[4]))
            dates.append([name, date])
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
    # Add to calendar.txt
    cal = open('calendar.txt', 'w')
    weekdays = ['MONDAY', 'TUESDAY', 'WENSDAY',
                'THURSADY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
    for j in range(7):
        cal.write('{}:\n'.format(weekdays[j]))
        cal.write(
            '--------------------------------------------------------------------\n')
        for i in range(len(sorted_dates[j])):
            minute = sorted_dates[j][i][1].minute
            if len(str(minute)) == 1:
                minute = '0' + str(minute)
            cal.write('   {}:{} | {}: {} - {}\n'.format(sorted_dates[j][i][1].hour, minute,
                      sorted_dates[j][i][0], sorted_dates[j][i][1], sorted_dates[j][i][1] + delta))
    cal.close()
    print('Váš rozvhrh je v souboru calendar.txt')


def work():
    '''Study stopwatch'''
    today = datetime.datetime.today()
    today = datetime.datetime(today.year, today.month,
                              today.day, today.hour, today.minute, second=0)
    status = True
    with open('calendar.txt', 'r') as file:
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
                start_date = datetime.datetime(int(delta_cal[:delta_cal.index('-')]), int(delta_cal[delta_cal.index('-')+1:delta_cal.index('-', delta_cal.index('-')+1)]), int(delta_cal[delta_cal.index('-', delta_cal.index(
                    '-')+1)+1:delta_cal.index(' ')]), int(delta_cal[delta_cal.index(' ')+1:delta_cal.index(' ')+3]), int(delta_cal[delta_cal.index(' ')+4:delta_cal.index(' ')+6]), int(delta_cal[delta_cal.index(' ')+7:delta_cal.index(' ')+9]))
                delta_cal = delta_cal.replace(str(start_date), '')
                delta_cal = delta_cal[3:]
                finish_date = datetime.datetime(int(delta_cal[:delta_cal.index('-')]), int(delta_cal[delta_cal.index('-')+1:delta_cal.index('-', delta_cal.index('-')+1)]), int(delta_cal[delta_cal.index('-', delta_cal.index(
                    '-')+1)+1:delta_cal.index(' ')]), int(delta_cal[delta_cal.index(' ')+1:delta_cal.index(' ')+3]), int(delta_cal[delta_cal.index(' ')+4:delta_cal.index(' ')+6]), int(delta_cal[delta_cal.index(' ')+7:delta_cal.index(' ')+9]))
                if bool(today > start_date) == True and bool(today < finish_date) == True:
                    current_activity = line[line.index(
                        '|')+2:line.index(':', line.index('|'))]
                    for subject in subjects:
                        if current_activity == subject.name:
                            current_activity = subject
                            ask = str(
                                input('Váše aktuální aktivita je {}?(yes/no):'.format(current_activity.name)))
        if ask != 'yes':
            ask = 'no'
        if ask == 'no':
            while status == True:
                ask = str(
                    input('Uveďte název předmětu, nad kterým teď pracujete?:'))
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
    data.add_progress(current_activity, delta_time)


def progress():
    '''Users progress (return None)'''
    for subject in subjects:
        print(int(subject.progress_check()//1))


main()
