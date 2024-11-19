from multiprocessing import Process
import os

def run_flask():
    os.system("python app.py")

def run_twitchbot():
    os.system("python twitchbot.py")

if __name__ == "__main__":
    p1 = Process(target=run_flask)
    p2 = Process(target=run_twitchbot)

    p1.start()
    p2.start()

    p1.join()
    p2.join()
