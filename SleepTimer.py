import time


class SleepTimer:
    def __init__(self):
        self.reset()

    def reset(self):
        self.time = time.time()

    def sleep(self, sec=1):
        passed = time.time() - self.time
        # print('sleep time: %f' % (sec-passed))
        if passed >= sec:
            return
        time.sleep(sec-passed)
        self.time = time.time()
