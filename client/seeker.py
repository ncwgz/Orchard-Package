# ==============================================
#                  OrchardSeeker
#
# Author:   Guozhi Wang
# Date:     Jun 05 2019
# Verwion:  0.1.2
# This file is delivered within OrchardPackage.
# ==============================================

import socket
import json

obj = socket.socket()
obj.connect(("127.0.0.1",9070))

def command(command):
    req_bytes = bytes(json.dumps(command), encoding="utf-8")
    obj.sendall(req_bytes)
    ret_bytes = obj.recv(65535)
    ret_str = str(ret_bytes, encoding="utf-8")
    print(ret_str)

def start():
    cmd = {"action": "start"}
    command(cmd)

def stop():
    cmd = {"action": "stop"}
    command(cmd)

def health():
    cmd = {"action": "health"}
    command(cmd)

def refresh():
    cmd = {"action": "synchronize"}
    flag = True
    data = []
    while flag == True:
        id = input("Type id:\n")
        port = input("Type port\n")
        secret = input("Type secret:\n")
        choice_legal = False
        while choice_legal == False:
            choice = input("Continue another user? y/n")
            if choice == 'y' or choice == 'Y':
                flag = True
                choice_legal = True
            if choice == 'n' or choice == 'N':
                flag = False
                choice_legal = True
        data.append({"id": id, "port": port, "secret": secret})
    cmd["data"] = json.dumps(data)
    command(cmd)

def add():
    cmd = {"action": "add"}
    user = {}
    user["id"] = input("Type id:\n")
    user["port"] = input("Type port\n")
    user["secret"] = input("Type secret\n")
    cmd["data"] = json.dumps(user)
    command(cmd)

def delete():
    id = input('Type id:\n')
    cmd = {
        "action": "delete",
        "data": id
    }
    command(cmd)

def quitt():
    cmd = {"action": "quit"}
    command(cmd)

def illegal():
    cmd = {"action": "illegal"}
    command(cmd)

while True:
    inp = input("Select action:\n"
                + " 1> health\n"
                + " 2> refresh\n"
                + " 3> add\n"
                + " 4> delete\n"
                + " 5> start\n"
                + " 6> stop\n"
                + " 7> quit\n"
                + " 8> illegal\n")
    if inp == '1':
        health()
    elif inp == '2':
        refresh()
    elif inp == '3':
        add()
    elif inp == '4':
        delete()
    elif inp == '5':
        start()
    elif inp == '6':
        stop()
    elif inp == '7':
        quitt()
        break
    elif inp == '8':
        illegal()
    else:
        print("Illegal choice!")