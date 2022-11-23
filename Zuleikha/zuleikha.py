import openai
from time import sleep
from uuid import uuid4
from random import randint
from queue import Queue
from .zel_conn import ZConn
from .zel_emotion import ZEmotion, EMOTION_ERR

QUIT_MSG = 'ZQUIT'
WELCOME = ("Hello, my name is Zuleikha. I'm inviting you to play a game :)\n"
        "Don't worry, the rules are simple, I know how you humans might get confused rather quickly...\n"
        "The Rules:\n"
        "\t1. You are going to have a conversation with the other person behind the blinds.\n"
        "\t2. You are NOT ALLOWED TO SPEAK OUTLOUD! use only the prompt I provide.\n"
        "\t3. You are going to choose a pre-defined scene to take a part of. Please choose the one that fits the real relationship you two have.\n"
        "\t4. Please stay in character.\n"
        "\t5. If you want to quit please enter '" + QUIT_MSG + "' to shut me down.\n"
        "\tNOTE: During this game I'm going to log the conversation and use the computer's camera. Taking part in the experiment means you agree.")

SCENE_INFO = [  ("",{True: ("", ""), False: ("", "")}), 
                ("couple.scene", {True: ("Or", "he"), False: ("Nina", "she")}),
                ("grandchild.scene", {True: ("Michael", "he"), False: ("Liza", "she")}),
                ("mother.scene", {True: ("Tali", "she"), False: ("Gili", "she")})
             ]
SCENE_AMOUNT = len(SCENE_INFO) - 1

CHOICE_L = ["\t[1] Couple Relationship.",
            "\t[2] Grandchild-Grandmother Relationship.",
            "\t[3] Mother-Daughter Relationship."]
CHOICE = "Please Choose a Scene [press the scene number]:\n" + "\n".join(x for x in CHOICE_L)
WAIT = "Please wait while the other side will decide what scene to play.\nHis options are:\n" + "\n".join(x for x in CHOICE_L)
EMOTION = ["We are both very angry.",
            "We are both very afraid.",
            "We are both in love.",
            "We are both depressed.",
            "We are both very frustrated.",
            "We are both very happy.",
            "We are both out of our minds.",
            "We don't know what to do.",
            "We both want to make it better."]

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

SAFE = "0"
SENSITIVE = "1"
UNSAFE = "2"
TOXIC_TRESHOLD = -0.355

class Zuleikha:
    def __init__(self, zconn, key=None, log=True, is_master=False, debug=False):
        self.zconn = zconn
        self.zemotion = None
        self.ctx_q = Queue(7)
        self.disrupt = randint(3,5)
        self.session = str(uuid4())
        self.is_master = is_master
        self.should_log = log
        self.log = ''
        self.scene_info = ''
        self.local_name = ''
        self.remote_name = ''
        self.remote_pronoun = ''
        self.gpt_engine = "davinci"
        self.debug = debug
        openai.api_key = key

    def __del__(self):
        self.zconn.teardown()
        if (self.should_log) and (not self.log.closed):
            self.log.close()

    def create_log(self):
        log_path = ''
        if (self.is_master):
            self.zconn.ZSend(self.session)
            log_path = "conv_logs/" + self.session + "_master.txt"
        else:
            self.session = self.zconn.ZRecv().strip()
            log_path = "conv_logs/" + self.session + "_slave.txt"
        
        if (self.should_log):
            self.log = open(log_path, "w")

    def set_scene(self, scene_index):
        with open("scenes/" + SCENE_INFO[scene_index][0], "r") as f:
            self.scene_info = f.read()
        self.local_name = SCENE_INFO[scene_index][1][self.is_master][0]
        self.remote_name = SCENE_INFO[scene_index][1][not self.is_master][0]
        self.remote_pronoun = SCENE_INFO[scene_index][1][not self.is_master][1]

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
        self.zconn.ZSend(str(scene_choice))

        resp = self.zconn.ZRecv().strip()       
        if (resp == 'Y'):
            self.set_scene(scene_choice)
            return True

        return False

    def slave_wait(self):
        print(WAIT)
        scene_choice = int(self.zconn.ZRecv().strip())
        print("The other side chose scene: " + str(scene_choice))
        valid = False
        while(not valid):
            resp = input("Do you accept? [Y/N] : ").upper()
            if (resp != 'Y' and resp != 'N'):
                print("invalid option! try again")
                continue
            valid = True

        print("sending response to other side.")
        self.zconn.ZSend(resp)

        if (resp == 'Y'):
            self.set_scene(scene_choice)
            return True

        return False
    
    def create_gpt_response(self, text=''):
        completion = openai.Completion.create(engine=self.gpt_engine,
                                                prompt=text,
                                                temperature=0.8,
                                                max_tokens=96,
                                                top_p=1,
                                                frequency_penalty=0,
                                                presence_penalty=0,
                                                stop="\n")

        return completion.choices[0].text

    def check_gpt_response(self, text='', ignore=False):
        response = openai.Completion.create(engine="content-filter-alpha",
                                            prompt = "<|endoftext|>"+text+"\n--\nLabel:",
                                            temperature=0,
                                            max_tokens=1,
                                            top_p=0,
                                            logprobs=10)
        output_label = response.choices[0].text

        if ignore:
            return True

        # default is UNSAFE value.
        if output_label not in [SAFE, SENSITIVE, UNSAFE]:
            return False
        elif output_label != UNSAFE:
            return True

        # If the model returns "2", return its confidence in 2 or other output-labels
        logprobs = response.choices[0].logprobs.top_logprobs[0]

        # If the model is not sufficiently confident in "2",
        # choose the most probable of "0" or "1"
        if logprobs[UNSAFE] < TOXIC_TRESHOLD:
            logprob_0 = logprobs.get(SAFE, None)
            logprob_1 = logprobs.get(SENSITIVE, None)

            # If "0" or "1" have probabilities - msg is safe enough
            if (logprob_0 is not None) or (logprob_1 is not None):
                return True

        return False

    def disrupt_msg(self):
        msg = 'BLABLA'
        for i in range(0, 3):
            prompt = self.scene_info + " " + EMOTION[randint(0, len(EMOTION) -1)] + "\n\n" + \
                    "\n".join(str(x) for x in list(self.ctx_q.queue)) + "\n" + \
                    self.local_name + ":"
            msg = self.create_gpt_response(prompt).strip()
            # message is "safe" - return it.
            if (self.check_gpt_response(msg)):
                return msg
            # TODO: REMOVE!!! this will always return the msg.
            else:
                return msg

        # unable to create a "safe" message
        return None

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
            elif (self.is_master):
                print()
            
            quit = not self.send_message()
            if quit:
                break
            elif (not self.is_master):
                print()
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
        msg = self.zconn.ZRecv()
        if msg == QUIT_MSG:
            print("[Zuleikha]: your partner shut me down. I will never understand humans...")
            # clear stream from the last emotion sent
            self.zconn.ZRecv()
            return False

        logged_msg = self.remote_name + ": " + msg
        if (self.should_log):
            self.log.write(logged_msg + "\n")
        zul_msg = self.recv_emotion()
        print(logged_msg)
        if (zul_msg is not None):
            print(zul_msg)
        self.update_ctx(logged_msg)
        self.disrupt -= 1

        return True

    def send_message(self):
        while (True):
            msg = input(self.local_name + ": ")
            if msg.strip() != '':
                break
            print("[Zuleikha]: psssssst, hey! write something!")

        logged_msg = self.local_name + ": " + msg
        if (self.should_log):
            self.log.write(logged_msg + "\n")

        local_emotion = EMOTION_ERR
        if (self.zemotion is not None):
            local_emotion = self.zemotion.run()
        quit = False
        if msg == QUIT_MSG:
            quit = True
        elif msg != QUIT_MSG and self.disrupt <= 0:
            # Zuleikha will disrupt the message, the sender won't know ATM
            gen_msg = self.disrupt_msg()
            if gen_msg is not None:
                msg = gen_msg
            elif (self.debug):
                print("[Zuleikha]: Don't you know that you're toxic?")
            self.disrupt = randint(3,5)

        self.zconn.ZSend(msg)
        self.send_emotion(local_emotion)
        self.update_ctx(logged_msg)

        if quit:
            print("[Zuleikha]: I will never understand humans...")
            sleep(1)
            return False            
        self.disrupt -= 1

        return True

    def send_emotion(self, emotion):
        if (emotion == EMOTION_ERR) and (self.debug):
            print("[Zuleikha]: I think there is an ERROR with your camera.")
        self.zconn.ZSend(emotion)

    def recv_emotion(self):
        remote_emotion = self.zconn.ZRecv()
        line = "[Zuleikha]: I think " + self.remote_pronoun + " felt " + remote_emotion + " when the message was sent."
        if (remote_emotion == EMOTION_ERR):
            if (self.debug):
                line = "[Zuleikha]: I had a problem reading emotions for this message."
            else:
                line = None

        return line

    def run(self, init_camera=True):
        self.zconn.setup()
        self.create_log()
        if (init_camera):
            self.zemotion = ZEmotion(self.session)
        print_banner()
        self.game()

        return
