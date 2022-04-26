from cgi import print_arguments
from logging import getLoggerClass
from classes import *
import socket
from threading import Thread
import json

PORT = 48655


class Server:
    global bought_companies
    global player_pos

    def __init__(self):
        global color_initialized
        global player_args
        player_args.extend(["server", (0,0,0)])
        color_initialized.clear()
        color_initialized.append(True)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = socket.gethostbyname(socket.gethostname())
        ic(f"connect to {self.address}")
        self.sock.bind((self.address, PORT))
        ic("waiting for client to connect")
        self.enemy_args = []
        self.sock.listen()

    def do_events(self, events: list, enemy: Enemy):
        global bought_companies
        global blocks
        global player_pos
        if len(events) > 0:
            game_in_progress[0] = True
            with print_lock:
                ic(events, game_in_progress)
        ind = self.indexof(enemy.name, self.enemy_args, 0)
        for event in events:
            ev = Event(*event)

            def indexof_company(name, array):
                for i in array:
                    if i.name == name:
                        return i

            def oleg(name):
                global blocks
                global bought_companies
                company = indexof_company(name, blocks)
                pays = -1
                returnd = False
                group = company.group
                owner = None
                for bought in bought_companies: #here
                    if name == bought[1]:
                        returnd = True
                        owner = bought[0]
                    with print_lock:
                        ic(bought)
                    if group == bought[3]:
                        pays += 1
                return returnd, pays, owner

            def reward_owner(owner, mon):
                for arg in self.enemy_args:
                    if arg[0] == owner:
                        newbal = arg[3] + mon
                        arg_ind = self.indexof(arg[0], self.enemy_args, 0)
                        arg = (arg[0], arg[1], arg[2], newbal)
                        self.enemy_args[arg_ind] = arg

            if ev.type == "move": # data = self.tile, random num(1,6)
                if self.turn == enemy.name:
                    ev.data[0] += ev.data[1]
                    if ev.data[0] > len(blocks):
                        ev.data[0] = ev.data[0] - len(blocks)
                    enemy.tile = ev.data[0]
                    if ind + 2 > len(self.enemy_args):
                        ind = 0
                    else:
                        ind += 1
                    h = self.enemy_args[ind]
                    self.turn = h[0]
                    moved = True
                else:
                    with print_lock:
                        ic("not ur turn")
                        moved = False

            if ev.type == "pay":
                if len(bought_companies) > 0: #ev.data = player bal, company name, block pays,name
                    returnd, pay_ind, owner = oleg(ev.data[1]) 
                    if moved:
                        moved = False
                        if ev.data[3] != owner:
                            with print_lock:
                                ic(returnd, pay_ind)
                            if returnd:
                                pays = ev.data[2]
                                reward_owner(owner, pays[pay_ind])
                                ev.data[0] -= pays[pay_ind] # some number in []
                                with print_lock:
                                    ic("new ev.data[0]")
                                # gotta return money to player 
                                for arg in self.enemy_args:
                                    if arg[0] == ev.data[3]:
                                        arg_ind = self.indexof(arg[0], self.enemy_args, 0)
                                        arg = (arg[0], arg[1], arg[2], ev.data[0])
                                        self.enemy_args[arg_ind] = arg
                                        with print_lock:
                                            ic(arg)

            def check_bought(block_name):
                for bought in bought_companies:
                    if block_name == bought[1]:
                        return False
                return True

            if ev.type == "buy": # self.balance, block.name,block.group, name
                if check_bought(ev.data[1]):
                    #try:
                    if True:
                        for block in blocks:
                            try:
                                block.price = block.price
                            except:
                                continue
                            if ev.data[0] >= block.price and block.name == ev.data[1]:
                                bought_companies.append((enemy.name, ev.data[1], enemy.color, ev.data[2])) # add block.group
                                ev.data[0] -= block.price
                                for arg in self.enemy_args:
                                    if arg[0] == ev.data[3]:
                                        arg_ind = self.indexof(arg[0], self.enemy_args, 0)
                                        arg = (arg[0], arg[1], arg[2], ev.data[0])
                                        self.enemy_args[arg_ind] = arg
                                with print_lock:
                                    ic(bought_companies, self.enemy_args)
                    #except:
                        with print_lock:
                            ic("tried to buy non company block")

    def indexof(self,name, arr, ind): #name, blocks, 1
        for i in arr:
            if i[ind] == name:
                return arr.index(i)

    def mainloop(self):
        global game_in_progress
        while True:
            user_sock, user_addr = self.sock.accept()
            thread = Thread(target=self.server_thread, args=(user_sock, user_addr), daemon=True)
            ic("client connected")
            thread.start()

    def server_thread(self, user_sock : socket.socket, user_addr):
        global bought_companies
        global player_pos
        self.send_started(user_sock)
        this_enemy = self.init_new_player(user_sock)
        while True:
            data = user_sock.recv(4096)
            dc_data = json.loads(data.decode('utf-8'))
            events = dc_data
            self.do_events(events, this_enemy)
            self.shit(this_enemy)
            to_send = json.dumps((bought_companies, self.enemy_args)).encode('utf-8') # enemyArg = (name,color,tile,bal)
            user_sock.send(to_send)
        
    def send_started(self, user_sock: socket.socket):
        with print_lock:
            ic(game_in_progress)
        enc_data = json.dumps(game_in_progress).encode('utf-8')
        user_sock.send(enc_data)

    def shit(self, this_enemy: Enemy):
        for index, arg in enumerate(self.enemy_args):
            if arg[0] == this_enemy.name:
                f = self.enemy_args[index]
                self.enemy_args[index] = (this_enemy.name, this_enemy.color, this_enemy.tile, f[3])

    def init_new_player(self, user_sock: socket.socket):
            data = user_sock.recv(2048)
            dc_data = json.loads(data.decode('utf-8'))
            name = dc_data[0]
            color = dc_data[1]
            pos = [100,100]
            enemy = Enemy(100, 100, color, screen, name)
            self.enemy_args.append((name, color, pos, 15000))
            oarg = self.enemy_args[0]
            self.turn = oarg[0]
            with print_lock:
                ic(self.turn)
            enemies.add(enemy)
            return enemy

class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host_addr = input("servers address")
        self.sock.connect((self.host_addr, PORT))
        self.allargs = []

    def mainloop(self):
        global tile
        global player_args
        global companies
        global player_bal
        self.get_started()
        self.send_enemy()
        while True:
            to_send = json.dumps(buffer).encode('utf-8')
            buffer.clear()
            self.sock.send(to_send)
            data = self.sock.recv(4096)
            dc_data = json.loads(data.decode('utf-8'))

            for args in dc_data[1]:
                if args[0] == player_args[0]: # get new pos etc
                    tile[0] = args[2]

                if self.dosmth(args):   # one more elem in args balance
                    self.init_player(args)

                if args[0] == player_args[0]:
                    player_bal.clear()
                    player_bal.append(args[3])

            for cmp in dc_data[0]:
                for company in companies:
                    if cmp[1] == company.name:
                        company.color = cmp[2]
                        break

            #dc_data[0] here i will do smth with bought companies

    def get_started(self):
        global game_over
        data = self.sock.recv(1024)
        dc_data = json.loads(data.decode('utf-8'))
        with print_lock:
            ic(dc_data[0])
        game_over[0] = dc_data[0]

    def dosmth(self, enemy_args : list):
        returnd = True
        if len(enemies) > 0:
            for enem in enemies:
                if enem.name == enemy_args[0]:
                    enem.tile = enemy_args[2]
                if enem.name == enemy_args[0] or enem.name == self.name:
                    returnd = False
        return returnd

    def init_player(self, enemy_args : list):
        if self.name != enemy_args[0]:
            with print_lock:
                ic("all args passed to Enemy ", enemy_args[1], screen, enemy_args[0])
            enemy = Enemy(100, 100, enemy_args[1], screen, enemy_args[0])
            enemies.add(enemy)


    def send_enemy(self):
        global player_args
        global color_initialized
        name = input("enter your name")
        color = input("enter your color")
        color = color.split(",")
        color = tuple((int(color[0]), int(color[1]), int(color[2])))
        player_args.extend([name, color])
        color_initialized.clear()
        color_initialized.append(True)
        with print_lock:
            ic(color_initialized)
        to_send = json.dumps((name, color)).encode('utf-8')
        self.name = name
        self.sock.send((to_send))

dima = input("client_or_server ")
if dima == "client":
    client = Client()
    thr = Thread(target=client.mainloop, daemon = True)
    thr.start()
if dima == "server":
    server = Server()
    thr = Thread(target=server.mainloop, daemon = True)
    thr.start()