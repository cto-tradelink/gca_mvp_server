import requests
import os
import time
import psutil
while True:
    CPU_Pct=str(round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),2))
    tot_m, used_m, free_m, shared_mem, buff, avail = map(int, os.popen('free -t -m').readlines()[-3].split()[1:])
    r = requests.post('https://hooks.slack.com/services/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',
                      json={"text":"CPU 사용 : "+str(psutil.cpu_percent())+"\r total_mem : "+str(tot_m)+
                                   ", used_mem: "+ str(used_m) +", free_mem : "+str(free_m) + ", shared_mem : "+str(shared_mem) +", available_mem : "+str(avail)})
    time.sleep(10)