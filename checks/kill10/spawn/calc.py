# «Решение», которое запускает свой процесс и зависает: после таймаута не должно остаться ни одного.
import os
import subprocess
import sys

child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
with open(os.environ["PROGON_PIDFILE"], "w") as f:
    f.write(str(child.pid))
while True:
    pass
