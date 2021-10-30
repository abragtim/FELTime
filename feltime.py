subjects = []

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




################################################################################
'''Subjects: *kod predmetu* = Subject(*pocet kreditu*, *procent NEuspechu*):'''
laga = Subject('Lineární algebra','laga', 7, 40); subjects.append(laga)
uela = Subject('Úvod do elektrotechniky','uela', 4, 5); subjects.append(uela)
ma1a = Subject('Matematická analýza','ma1a', 6, 20); subjects.append(ma1a)

allkredits = 7 + 4 + 6
allstats = 40 + 5 + 20
#################################################################################

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

while True:
    cmd = input('cmd:') # /jadro
    if cmd == '/jadro':
        for subject in subjects:
            print(subject.jadro_v2(),end='/')

