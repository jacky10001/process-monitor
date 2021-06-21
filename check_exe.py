import psutil

def checkprocess(processname):
    pids = psutil.pids()

    for pid in pids:
        p = psutil.Process(pid)
        if p.name() == processname:
            return pid

if isinstance(checkprocess("winMain.exe"), int):
    print("存在")
else:
    print("不存在")