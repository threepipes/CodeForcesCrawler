import getCodeCF as gc
import random
from Database import Database

user_list = gc.getUsers(gc.userdata_format)
current_sample = gc.loadData(gc.samplefile)
for user in current_sample:
    user_list.remove(user)
new_sample = random.sample(user_list, 2000)

db = Database()
border = gc.getLeastTime()
end = gc.end
gc.setSubmissionHistory(db, new_sample, border, end)
