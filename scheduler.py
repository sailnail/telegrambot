import schedule
import time
import pickle

user_data = []


def job():
    with open("user_data.pkl", "wb") as pickle_file:
        pickle.dump(user_data, pickle_file)
    print('done')


schedule.every().day.at("17:16").do(job)
job()
while True:
    schedule.run_pending()
    time.sleep(0)
