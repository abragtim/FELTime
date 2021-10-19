class Subject:
    def __init__(self,kred,stat):
        self.kred = kred #pocet kreditu
        self.stat = stat #statistika uspechu
    def kredits(self):
        return self.kred
    def statistics(self):
        return self.stat

'''Subjects: *kod predmetu* = Subject(*pocet kreditu*, *procent uspechu*):'''
laga = Subject(7,60)
uela = Subject(4,95)
ma1a = Subject(6,80)
