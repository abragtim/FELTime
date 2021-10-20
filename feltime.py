subjects = []

class Subject:
    def __init__(self,kred,stat):
        self.kred = kred #pocet kreditu
        self.stat = stat #statistika uspechu
    def kredits(self):
        return self.kred
    def statistics(self):
        return self.stat
    def jadro_v1_kred(self):
        kredit_part = self.kredits()/allkredits*100*0.5
        return kredit_part 
    def jadro_v1_stat(self):
        statistics_part = self.statistics()/allstats*100*0.5
        return statistics_part

'''Subjects: *kod predmetu* = Subject(*pocet kreditu*, *procent uspechu*):'''


laga = Subject(7,60); subjects.append(laga)
uela = Subject(4,95); subjects.append(uela)
ma1a = Subject(6,80); subjects.append(ma1a)
allkredits = 7 + 4 + 6
allstats = 60 + 95 + 80

""" 
def jadro_v1(self):
    kredit_part = self.kredits()/allkredits*100*0.5
    statistics_part = self.statistics()/allstats*100*0.5
    print('{}, {}'.format(kredit_part, statistics_part))
"""

for subject in subjects:
    print(subject.jadro_v1_kred())


