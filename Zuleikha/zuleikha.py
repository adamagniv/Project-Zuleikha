import openai
import socket
from time import sleep
from uuid import uuid4
from random import randint
from queue import Queue

QUIT_MSG = 'ZQUIT'
WELCOME = ("Hello, my name is Zuleikha. I'm inviting you to play a game :)\n"
        "Don't worry, the rules are simple, I know how you humans might be confused rather quickly...\n"
        "The Rules:\n"
        "\t1. You are going to have a conversation with the other person behind the blinds.\n"
        "\t2. You are NOT ALLOWED TO SPEAK OUTLOUD! use only the prompt you have.\n"
        "\t3. You are going to choose a pre-defined scene to take a part of. Please stay in character.\n"
        "\t4. If you want to quit please enter '" + QUIT_MSG + "' to shut me down.")

SCENE_INFO = [  ("",{True: "", False: ""}), 
                ("couple.scene", {True: "Or", False: "Nina"})
             ]
SCENE_AMOUNT = len(SCENE_INFO) - 1
CHOICE = ("Please Choose a Scene [press the scene number]:\n"
        "\t[1] Couple Relationship.")
WAIT = ("Please wait while the other side will decide what scene to play.\n"
        "His options are:\n"
        "\t[1] Couple Relationship.")
EMOTION = ["We are both very angry.",
            "We are both very afraid.",
            "We are both in love.",
            "We are both depressed.",
            "We are both very frustrated.",
            "We are both very happy.",
            "We are both out of our minds.",
            "We don't know what to do.",
            "We both want to make it better."]

SERV_IP_ADDR = "127.0.0.1"
PORT = 9001

def print_banner():
    print('\n@@@@@@@   @@@@@@@    @@@@@@        @@@  @@@@@@@@   @@@@@@@  @@@@@@@            @@@@@@@@  @@@  @@@  @@@       @@@@@@@@  @@@  @@@  @@@  @@@  @@@   @@@@@@ ')
    print('@@@@@@@@  @@@@@@@@  @@@@@@@@       @@@  @@@@@@@@  @@@@@@@@  @@@@@@@            @@@@@@@@  @@@  @@@  @@@       @@@@@@@@  @@@  @@@  @@@  @@@  @@@  @@@@@@@@')
    print('@@!  @@@  @@!  @@@  @@!  @@@       @@!  @@!       !@@         @@!                   @@!  @@!  @@@  @@!       @@!       @@!  @@!  !@@  @@!  @@@  @@!  @@@')
    print('@@!  @@@  @@!  @@@  @@!  @@@       @@!  @@!       !@@         @@!                   @@!  @@!  @@@  @@!       @@!       @@!  @@!  !@@  @@!  @@@  @@!  @@@')
    print('@!@@!@!   @!@!!@!   @!@  !@!       !!@  @!!!:!    !@!         @!!                 @!!    @!@  !@!  @!!       @!!!:!    !!@  @!@@!@!   @!@!@!@!  @!@!@!@!')
    print('!!@!!!    !!@!@!    !@!  !!!       !!!  !!!!!:    !!!         !!!                !!!     !@!  !!!  !!!       !!!!!:    !!!  !!@!!!    !!!@!!!!  !!!@!!!!')
    print('!!:       !!: :!!   !!:  !!!       !!:  !!:       :!!         !!:               !!:      !!:  !!!  !!:       !!:       !!:  !!: :!!   !!:  !!!  !!:  !!!')
    print(':!:       :!:  !:!  :!:  !:!  !!:  :!:  :!:       :!:         :!:              :!:       :!:  !:!   :!:      :!:       :!:  :!:  !:!  :!:  !:!  :!:  !:!')
    print(' ::       ::   :::  ::::: ::  ::: : ::   :: ::::   ::: :::     ::               :: ::::  ::::: ::   :: ::::   :: ::::   ::   ::  :::  ::   :::  ::   :::')
    print(' :         :   : :   : :  :    : :::    : :: ::    :: :: :     :               : :: : :   : :  :   : :: : :  : :: ::   :     :   :::   :   : :   :   : :\n')

    def loop_dots(msg):
        print(msg, end="", flush=True)
        for i in range(0, 3):
            sleep(0.7)
            print(".", end="", flush=True)
        print("", flush=True)
    loop_dots("WELCOME!\n\tInitializing")
    loop_dots("\tEstablishing Connection")
    loop_dots("\tWasting Your Time")
    print("", flush=True)

def ZSend(sock, msg):
    try:
        sock.send(msg.encode())
    except:
        sock.close()

def ZRecv(sock):
    try:
        msg = sock.recv(256).decode()
    except:
        sock.close()
    return msg


class Zuleikha:
    def __init__(self, key = None, log = False, is_master = False):
        self.server = ''
        self.conn = ''
        self.ctx_q = Queue(7)
        self.disrupt = randint(3,7)
        self.is_master = is_master
        self.should_log = log
        self.log_path = "conv_logs/" + str(uuid4()) + ".txt"
        self.log = ''
        self.scene_info = ''
        self.local_name = ''
        self.remote_name = ''
        self.gpt_engine = "davinci"
        openai.api_key = key
        if (self.should_log):
            self.log = open(self.log_path, "w")

    def __del__(self):
        if (self.should_log):
            self.log.close()
            self.server.close()
        self.conn.close()

    def connection(self):
        if (self.should_log):
            # setting up the server for connections on the master
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((SERV_IP_ADDR, PORT))
            self.server.listen(1)
            # accept connection from remote client
            self.conn, _ = self.server.accept()
        else:
            # connect to remote server
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((SERV_IP_ADDR, PORT))

        return

    def set_scene(self, scene_index):
        with open("scenes/" + SCENE_INFO[scene_index][0], "r") as f:
            self.scene_info = f.read()
        self.local_name = SCENE_INFO[scene_index][1][self.is_master]
        self.remote_name = SCENE_INFO[scene_index][1][not self.is_master]

    def master_choose(self):
        print(CHOICE)
        valid = False
        scene_choice = 0
        while (not valid):
            scene_choice = input("enter choice: ")
            scene_choice = int(scene_choice)
            if (scene_choice > SCENE_AMOUNT or scene_choice == 0):
                print("invalid option! try again")
                continue
            valid = True
        
        print("sending request to play scene: [" + str(scene_choice) + "] to other side.\nplease wait for response.")
        ZSend(self.conn, str(scene_choice))

        resp = ZRecv(self.conn).strip()       
        if (resp == 'Y'):
            self.set_scene(scene_choice)
            return True

        return False

    def slave_wait(self):
        print(WAIT)
        scene_choice = int(ZRecv(self.conn).strip())
        print("The other side chose scene: " + str(scene_choice))
        valid = False
        while(not valid):
            resp = input("Do you accept? [Y/N] : ").upper()
            if (resp != 'Y' and resp != 'N'):
                print("invalid option! try again")
                continue
            valid = True
        
        print("sending response to other side.")
        ZSend(self.conn, resp)

        if (resp == 'Y'):
            self.set_scene(scene_choice)
            return True

        return False
    
    def create_gpt_response(self, text = ''):
        completion = openai.Completion.create(engine=self.gpt_engine,
                                                prompt=text,
                                                temperature=0.8,
                                                max_tokens=64,
                                                top_p=0.98,
                                                frequency_penalty=0.1,
                                                presence_penalty=0,
                                                stop="\n")

        return completion.choices[0].text

    def disrupt_msg(self):
        msg = 'BLABLA'
        prompt = self.scene_info + " " + EMOTION[randint(0, len(EMOTION) -1)] + "\n\n" + \
                "\n".join(str(x) for x in list(self.ctx_q.queue)) + "\n" + \
                self.local_name + ":"
        msg = self.create_gpt_response(prompt)

        return msg.strip()

    def game(self):
        print(WELCOME)
        sleep(3)
        print("Let us begin.")
        self.choose_game()

        # Starting Finally...
        quit = False
        if (self.is_master):
            print("You are starting the conversation.\n")
            quit = not self.send_message()
            if quit:
                return
        else:
            print("Please wait for the other side to start the conversation.\n")
        
        while (True):
            quit = not self.recv_message()
            if quit:
                break
            
            quit = not self.send_message()
            if quit:
                break        
        return

    def choose_game(self):
        while (True):
            ret = False
            if(self.is_master):
                ret = self.master_choose()
            else:
                ret = self.slave_wait()
            
            if (ret):
                print("\nBoth sides agreed!")
                print("\nSCENE INFO:\n" + self.scene_info.replace(". ",".\n"))
                print("\nyou will play as: " + self.local_name)
                break
            
            print("\nDisagreed... lets try again...")
            self.is_master = not self.is_master

        return

    def update_ctx(self, msg):
        if self.ctx_q.full():
            # remove oldest item
            self.ctx_q.get()
        self.ctx_q.put(msg)

        return

    def recv_message(self):
        msg = ZRecv(self.conn)
        if msg == QUIT_MSG:
            print("[Zuleikha]: your partner shut me down. I will never understand humans...")
            return False
        
        logged_msg = self.remote_name + ": " + msg
        if (self.should_log):
            self.log.write(logged_msg + "\n")
        print(logged_msg)
        self.update_ctx(logged_msg)
        self.disrupt -= 1

        return True

    def send_message(self):
        while (True):
            msg = input(self.local_name + ": ")
            if msg.strip() != '':
                break
            print("[Zuleikha]: psssssst, hey! write something!")
        
        quit = False
        if msg == QUIT_MSG:
            quit = True
        elif msg != QUIT_MSG and self.disrupt <= 0:
            # Zuleikha will disrupt the message, the sender won't know ATM
            msg = self.disrupt_msg()
            self.disrupt = randint(3,7)

        logged_msg = self.local_name + ": " + msg
        if (self.should_log):
            self.log.write(logged_msg + "\n")
        ZSend(self.conn, msg)
        self.update_ctx(logged_msg)

        if quit:
            print("[Zuleikha]: I will never understand humans...")
            sleep(1)
            return False            
        self.disrupt -= 1

        return True

    def run(self):
        self.connection()
        print_banner()
        self.game()

        return

