import datetime
from database import *

''' ---------------------------- Main process ---------------------------- '''
def main():
    '''Interactive menu'''
    # client autorization"""
    autorize = client.login()
    print('Hello, {}'.format(autorize))
    database.synch_tables()
    subjects_init()
    database.reconnect()

    while True:
        for subject in subjects:
            print('> [{}%] {} ({}):'.format(int(subject.progress_check()//1),
                                            subject.name,
                                            subject.code),
                  subject.core_v2(), '%')

        cmd = str(input('cmd:'))
        if cmd == '/zapis':
            # write down subject
            client.add_subjects()
            database.reconnect()
        if cmd == '/test_result':
            # put test result
            data.add_test_result()
            database.reconnect()
        if cmd == '/opinion':
            # put opinion
            data.add_subjective_opinion()
            database.reconnect()
        if cmd == '/organize':
            # organize calendar
            organize()
        if cmd == '/work':
            # switch-on work timer
            work()
        if cmd == '/exit':
            # stop program
            exit()
        if cmd == '/help':
            # show program cmds
            print('''
            /zapis - zapsat předmět;
            /test_result - přidat výsledek testu;
            /opinion - přidat subjektivní pocit z předmětu;
            /organize - výtvořit plan na týden;
            /work - progress timer;
            /exit - ukončit program.
            ''')
            input()


''' ------------------------------ Functions ------------------------------ '''

def organize():
    ''' Time organization '''
    # prepare subjects before organization:
    if not _prepare_subject():
        return None
    input('Proveďte změny v soubru organize.txt. Po ukončení stiskněte ENTER')

    # analize after organization:
    dates, delta = _organization_alalyzing()
    if dates is None:
        return None

    # Add to calendar.txt
    _cal_adding(dates, delta)
    print('Váš rozvhrh je v souboru calendar.txt')


def work():
    '''Study stopwatch'''
    today = datetime.datetime.today()
    today = datetime.datetime(today.year, today.month,
                              today.day, today.hour, today.minute, second=0)

    # calendar scanning and getting activity
    current_activity = _get_current_activity(today)

    # timer
    start_time = today
    input('Hodně štěstí ve studiu! Po ukončení studia stiskňete ENTER.')
    finish_time = datetime.datetime.today()
    delta_time = finish_time - start_time
    print('Čas studia: {}'.format(delta_time))

    delta_time = str(delta_time)[:str(delta_time).index('.')].split(':')
    delta_time = [int(cas) for cas in delta_time]
    delta_time = delta_time[0] * 60 + delta_time[1] * 60 + delta_time[2]
    data.add_progress(current_activity, delta_time)


def progress():
    '''Users progress (return None)'''
    for subject in subjects:
        print(int(subject.progress_check()//1))


''' ------------------------- Tools for organize() ------------------------ '''

def _prepare_subject():
    try:
        allhours = int(input('Kolik hodin v týdnu budete studovat?: '))
        if allhours <= 0:
            raise ValueError
    except ValueError:
        print('ERROR: Používejte celá kladná čísla.')
        return False
    file = open('organize.txt', 'w')
    file.write('')
    file.close()
    file = open('organize.txt', 'a')
    for subject in subjects:
        debt = (subject.progress_check() - 100)/100*allhours
        subject.time = allhours*subject.core_v2()/100 - debt
        if subject.progress_check() == 0:
            subject.time = allhours*subject.core_v2()/100
        subject.number = int(subject.time//1.5)
        file.write('{}:{}-{}-dd-hh-mm \n'.format(subject.name,
                   datetime.datetime.today().year, datetime.datetime.today().month)*subject.number)
    file.close()
    return True


def _organization_alalyzing():
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
            date_input = line[lom+1:].replace('-', ' ').split()
            date = datetime.datetime(int(date_input[0]), int(date_input[1]), int(
                date_input[2]), int(date_input[3]), int(date_input[4]))
            dates.append([name, date])
        file.close()

        def dates_sorting(dates):
            sorted_dates = [[], [], [], [], [], [], []]
            i = 0
            storage = None
            activate_storage = False
            while True:
                if i == len(dates)-1:
                    i = 0
                    activate_storage = True
                #TODO: Index Error. Case: just 1 date in dates
                if dates[i][1] > dates[i+1][1]:
                    dates[i], dates[i+1] = dates[i+1], dates[i]
                    i += 1
                else:
                    i += 1
                if [dates] == storage:
                    break
                if activate_storage == True:
                    storage = [dates]
                    activate_storage == False
            for m in range(7):
                for i in range(len(dates)):
                    if datetime.datetime.weekday(dates[i][1]) == m:
                        sorted_dates[m].append(dates[i])
            del dates, storage, activate_storage, i
            return sorted_dates

        return dates_sorting(dates), delta
    except ValueError:
        print('ERROR: Chyba úprav v souboru.')
        return None, None
    except IndexError:
        print('ERROR: Chyba úprav v souboru.')
        return None, None


def _cal_adding(dates, delta):
    cal = open('calendar.txt', 'w')
    weekdays = ['MONDAY', 'TUESDAY', 'WENSDAY',
                'THURSADY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
    for j in range(7):
        cal.write('{}:\n'.format(weekdays[j]))
        cal.write(
            '--------------------------------------------------------------------\n')
        for i in range(len(dates[j])):
            minute = dates[j][i][1].minute
            if len(str(minute)) == 1:
                minute = '0' + str(minute)
            cal.write('   {}:{} | {}: {} - {}\n'.format(dates[j][i][1].hour, minute,
                      dates[j][i][0], dates[j][i][1], dates[j][i][1] + delta))
    cal.close()

''' --------------------------- Tools for work() -------------------------- '''

def _get_current_activity(today):
    status = True

    # calendar scanning (searching activity)
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
                start_date = datetime.datetime(int(delta_cal[:delta_cal.index('-')]),
                                               int(delta_cal[delta_cal.index(
                                                   '-')+1:delta_cal.index('-',
                                                                          delta_cal.index('-')+1)]),
                                               int(delta_cal[delta_cal.index('-',
                                                                             delta_cal.index(
                                                                                 '-')+1)+1:delta_cal.index(' ')]),
                                               int(delta_cal[delta_cal.index(
                                                   ' ')+1:delta_cal.index(' ')+3]),
                                               int(delta_cal[delta_cal.index(
                                                   ' ')+4:delta_cal.index(' ')+6]),
                                               int(delta_cal[delta_cal.index(' ')+7:delta_cal.index(' ')+9]))
                delta_cal = delta_cal.replace(str(start_date), '')
                delta_cal = delta_cal[3:]
                finish_date = datetime.datetime(int(delta_cal[:delta_cal.index('-')]),
                                                int(delta_cal[delta_cal.index(
                                                    '-')+1:delta_cal.index('-', delta_cal.index('-')+1)]),
                                                int(delta_cal[delta_cal.index('-', delta_cal.index(
                                                    '-')+1)+1:delta_cal.index(' ')]),
                                                int(delta_cal[delta_cal.index(
                                                    ' ')+1:delta_cal.index(' ')+3]),
                                                int(delta_cal[delta_cal.index(
                                                    ' ')+4:delta_cal.index(' ')+6]),
                                                int(delta_cal[delta_cal.index(' ')+7:delta_cal.index(' ')+9]))
                if bool(today > start_date) == True and bool(today < finish_date) == True:
                    current_activity = line[line.index(
                        '|')+2:line.index(':', line.index('|'))]
                    for subject in subjects:
                        if current_activity == subject.name:
                            current_activity = subject
                            ask = str(
                                input('Váše aktuální aktivita je {}?(yes/no): '\
                                    .format(
                                    current_activity.name)))

        if ask != 'yes':
            ask = 'no'
        if ask == 'no':
            # there isn't any activity in calendar -> getting from user
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

    return current_activity

''' ----------------------------------------------------------------------- '''
main()
