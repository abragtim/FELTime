import datetime
import subjects from feltime.py
allhours = 112
for subject in subjects:
    subject.time = allhours*subject.jadro_v2()
    print(subject.time)

