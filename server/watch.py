# ==============================================
#                   OrchardWatch
#
# Author:   Guozhi Wang
# Date:     Jun 16 2019
# Verwion:  0.2.0
# This file is delivered within OrchardPackage.
# ==============================================

# This file should NOT be called manually!

import yaml
import time
import json
import socketserver
import subprocess
import asyncio
import os

# 默认加密方式为chacha20-ietf-poly1305
CIPHER = 'chacha20-ietf-poly1305'
# 默认存放用户信息的配置文件
YMLPATH = '/usr/local/orchard/config.yml'

# 开启SSG(ShadowsocksGO)服务
def shadowsocksGo():
    shellscript = 'service SSG start'
    rc, out = subprocess.getstatusoutput(shellscript)
    log('SSG_EST', 'Shadowsocks GO server is running!', 2)

# 关闭SSG服务
def shadowsocksShut():
    shellscript = 'service SSG stop'
    rc, out = subprocess.getstatusoutput(shellscript)
    log('SSG_END', 'Shadowsocks GO server closed!', 1)

# 重启SSG服务
def shadowsocksRefresh():
    shellscript = 'service SSG stop'
    rc, out = subprocess.getstatusoutput(shellscript)
    shellscript = 'service SSG start'
    rc, out = subprocess.getstatusoutput(shellscript)
    log('SSG_RST', 'Shadowsocks GO server restarted!', 2)

# 统一格式输出日志 action为动作标识 msg为日志信息 type为消息类型
# type默认为0 0:普通 蓝色 1:警告 红色 2:成功 绿色 3:小问题 黄色
def log(action, msg, type=0):
    print(time.asctime() + ' [' + action, end=']:\t')
    if type == 0:
        print('\033[1;34m', end='')
    elif type == 1:
        print('\033[1;35m', end='')
    elif type == 2:
        print('\033[1;32m', end='')
    elif type == 3:
        print('\033[1;33m', end='')
    print(msg + '\033[0m')

# 读取config.yml获取用户信息
def getYml():
    with open(YMLPATH, 'r', encoding='utf-8') as file:
        yml = file.read()
        return yaml.load(yml)

# 将yml保存到config.yml中
def saveYml(yml):
    with open(YMLPATH, 'w', encoding='utf-8') as stream:
        yaml.dump(yml, stream)

# 检查是否有重名id
def checkDuplicate(id):
    yml = getYml()
    for user in yml['keys']:
        if user['id'] == id:
            return True
    return False

# 添加用户 id用户名 port端口 secret密码
def addUser(id, port, secret):
    if checkDuplicate(id):
        log('ADD_USR', 'User ' + id + ' duplicated!', 1)
    else:
        addUserWithoutRefresh(id, port, secret)
        shadowsocksRefresh()

def addUserWithoutRefresh(id, port, secret):
    yml = getYml()
    yml['keys'].append({
        'id': id,
        'port': int(port),
        'cipher': CIPHER,
        'secret': secret
    })
    saveYml(yml)
    log('ADD_USR', 'User ' + id + ' has been added.', 2)

def deleteUsers():
    yml = getYml()
    for i in range(len(yml['keys'])):
        yml['keys'].pop(0)
    saveYml(yml)
    log('DEL_USR', 'All users has been deleted.', 2)
    shadowsocksRefresh()
    return 0

# 按用户名删除用户
def deleteUserByID(id):
    yml = getYml()
    for i in range(len(yml['keys'])):
        if yml['keys'][i]['id'] == id:
            yml['keys'].pop(i)
            saveYml(yml)
            log('DEL_USR', 'User ' + id + ' has been deleted.', 2)
            shadowsocksRefresh()
            return 0
    log('DEL_USR', 'User ' + id + ' was not found when deleting.', 3)

# 将从网站传来的用户信息同步到config.yml
def synchronize(yml):
    yml_old = getYml()
    l1 = len(yml_old['keys'])
    l2 = len(yml['keys'])
    saveYml(yml)
    shadowsocksRefresh()
    log('SYN_USR', 'The yaml file has been synchronized. User amount: ' + str(l1) + ' ==> ' + str(l2), 1)

# 获取内存使用信息
def memory_stat():
    mem = {}
    f = open("/proc/meminfo")
    lines = f.readlines()
    f.close()
    for line in lines:
        if len(line) < 2: continue
        name = line.split(':')[0]
        var = line.split(':')[1].split()[0]
        mem[name] = int(var) * 1024.0
    mem['MemUsed'] = mem['MemTotal'] - mem['MemFree'] - mem['Buffers'] - mem['Cached']
    return mem

# 获取CPU使用信息
def cpu_stat():
    cpu = []
    cpuinfo = {}
    f = open("/proc/cpuinfo")
    lines = f.readlines()
    f.close()
    for line in lines:
        if line == '\n':
            cpu.append(cpuinfo)
            cpuinfo = {}
        if len(line) < 2: continue
        name = line.split(':')[0].rstrip()
        var = line.split(':')[1]
        cpuinfo[name] = var
    return cpu

# 获取系统负载程度信息
def load_stat():
    loadavg = {}
    f = open("/proc/loadavg")
    con = f.read().split()
    f.close()
    loadavg['lavg_1']=con[0]
    loadavg['lavg_5']=con[1]
    loadavg['lavg_15']=con[2]
    loadavg['nr']=con[3]
    loadavg['last_pid']=con[4]
    return loadavg

# 获取磁盘用量信息
def disk_stat():
    import os
    hd={}
    disk = os.statvfs("/")
    hd['available'] = disk.f_bsize * disk.f_bavail
    hd['capacity'] = disk.f_bsize * disk.f_blocks
    hd['used'] = disk.f_bsize * disk.f_bfree
    return hd

# 调用以上四个方法获取综合健康信息
def getHealth():
    memmm = memory_stat()
    toReturn = {}
    toReturn["ratioMem"] = int(memmm["MemUsed"] / memmm["MemTotal"] * 100)
    toReturn["total"] = int(memmm["MemTotal"] / 1024 / 1024)
    loaddd = load_stat()
    toReturn["load"] = loaddd["lavg_1"]
    diskkk = disk_stat()
    toReturn["ratioDisk"] = int(diskkk["used"] / diskkk["capacity"] * 100)
    toReturn["capacity"] = int(diskkk["capacity"] / 1024 / 1024)
    return json.dumps(toReturn)

# 用于收发Socket数据包的服务器
class Slaver(socketserver.BaseRequestHandler):
    def handle(self):
        conn = self.request
        client_ip = self.client_address[0]
        client_port = self.client_address[1]
        log('CON_EST', 'Established connection with ' + client_ip + ':' + (str)(client_port))

        while True:
            ret_bytes = conn.recv(4096)
            try:
                ret_str = str(ret_bytes, encoding="utf-8")
                req = json.loads(ret_str)
            except:
                log('MSG_ERR', 'Illegal packet received from ' + (str)(client_ip))
                continue

            if req["action"] == "health":
                log('MSG_OUT', 'Health information sent to ' + (str)(client_ip))
                conn.sendall(bytes(getHealth(), encoding="utf-8"))

            elif req["action"] == "add":
                user = json.loads(req["data"])
                addUser(user["id"], user["port"], user["secret"])
                msg = ("Added.")
                conn.sendall(bytes(msg, encoding="utf-8"))

            elif req["action"] == "addd":
                user = json.loads(req["data"])
                addUserWithoutRefresh(user["id"], user["port"], user["secret"])
                msg = ("Added.")
                conn.sendall(bytes(msg, encoding="utf-8"))

            elif req["action"] == "refresh":
                shadowsocksRefresh()
                msg = ("Refreshed.")
                conn.sendall(bytes(msg, encoding="utf-8"))

            elif req["action"] == "delete":
                id = req["data"]
                deleteUserByID(id)
                msg = ("Deleted.")
                conn.sendall(bytes(msg, encoding="utf-8"))
            
            elif req["action"] == "delete_all":
                deleteUsers()
                msg = ("Deleted.")
                conn.sendall(bytes(msg, encoding="utf-8"))

            elif req["action"] == "synchronize":
                data = json.loads(req["data"])
                yml = {}
                yml['keys'] = data
                synchronize(yml)
                msg = ("Synchronized.")
                conn.sendall(bytes(msg, encoding="utf-8"))
                
            elif req["action"] == "start":
                shadowsocksGo()
                msg = ("Started.")
                conn.sendall(bytes(msg, encoding="utf-8"))
                
            elif req["action"] == "stop":
                shadowsocksShut()
                msg = ("Stopped.")
                conn.sendall(bytes(msg, encoding="utf-8"))

            elif req["action"] == "quit":
                log('CON_END', 'Connection closed with ' + (str)(client_ip))
                msg = ("Connection closed.")
                conn.sendall(bytes(msg, encoding="utf-8"))
                break
            elif req["action"] == "check":
                log('CON_CHK', 'Check request from' + (str)(client_ip))
                msg = ('OK')
                conn.sendall(bytes(msg, encoding='utf-8'))

            else:
                log('MSG_ERR', 'Illegal command received from ' + (str)(client_ip))
                conn.sendall((bytes("Illegal command!", encoding="utf-8")))

if __name__ == "__main__":
    shadowsocksGo()
    server = socketserver.ThreadingTCPServer(("0.0.0.0", 9070), Slaver)
    server.serve_forever()