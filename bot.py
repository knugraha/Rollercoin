import os
import random
import time
import datetime

import cv2
import keyboard
import pyautogui
import shutil
from PIL import ImageGrab
from MTM import matchTemplates

GAME_NUM = 0
START_TIME = datetime.datetime.now()


def mouse_click(x, y, wait=0.05):
    pyautogui.click(x, y)
    time.sleep(wait)


def screen_grab():
    im = ImageGrab.grab()
    img_name = os.getcwd() + "\\imgs\\full_snap__" + str(int(time.time())) + ".png"
    im.save(img_name, "PNG")
    return img_name


def find_image(image_path, root_image_path):
    matches = matchTemplates(
        [("img", cv2.imread(image_path))],
        cv2.imread(root_image_path),
        N_object=10,
        score_threshold=0.9,
        # maxOverlap=0.25,
        searchBox=None)
    if len(matches["BBox"]) == 0:
        return None, None
    else:
        box = matches["BBox"][0]
        return box[0], box[1]


def check_image(img):
    b, _ = find_image(img, screen_grab())
    return True if b is not None else False


def click_image(img):
    time.sleep(0.05)
    x, y = find_image(img, screen_grab())
    if x is None or y is None:
        return

    im = cv2.imread(img)
    t_cols, t_rows, _ = im.shape
    mouse_click(x + t_rows * (3 / 5), y + t_cols * (2 / 3))


def setup():
    try:
        os.mkdir('imgs')
    except FileExistsError:
        print("Program was not correctly closed last time. Make sure to exit the game with CTRL+C")


def start_game(start_img_path):
    click_image(start_img_path)
    time.sleep(2)
    if not check_image("rc_items/utils/start_game.png"):
        pyautogui.moveTo(100, 100)
        return True
    sx, sy = find_image("rc_items/utils/start_game.png", screen_grab())
    mouse_click(sx + 2, sy + 2, wait=0.05)
    time.sleep(3)
    return False


def start_game_msg(name):
    global GAME_NUM
    print("Starting Game #{!s}: '{}'@{!s}".format(GAME_NUM, name, datetime.datetime.now().time()))
    GAME_NUM += 1


def end_game():
    
    if check_image("rc_items/utils/gain_power.png"):
        click_image("rc_items/utils/gain_power.png")
        
    if check_image("rc_items/utils/gameover.png"):
        click_image("rc_items/utils/restart.png")
    
    keyboard.press_and_release("page up")
    if check_image("rc_items/utils/recaptha.png"):
        keyboard.press_and_release("f5")
        
    if check_image("rc_items/utils/error2.png"):
        keyboard.press_and_release("f5")

    if check_image("rc_items/utils/choose_game.png"):
        click_image("rc_items/utils/choose_game.png")

    if check_image("rc_items/utils/collect_pc.png"):
        click_image("rc_items/utils/collect_pc.png")
        
    while not check_image("rc_items/games/coinflip_gameimg.png"):
        return end_game();


class BotCoinFlip:
    def __init__(self):
        self.start_img_path = "rc_items/games/coinflip_gameimg.png"
        self.game = "CoinFlip"
        self.coin_pos = []
        self.coin_items = {
            "binance": [],
            "btc": [],
            "eth": [],
            "litecoin": [],
            "monero": [],
            "eos": [],
            "rlt": [],
            "xrp": [],
            "xml": [],
            "tether": [],
        }
        self.coin_images = [
            ("binance", cv2.imread("rc_items/coinflip/coinflip_item_binance.png")),
            ("btc", cv2.imread("rc_items/coinflip/coinflip_item_btc.png")),
            ("eth", cv2.imread("rc_items/coinflip/coinflip_item_eth.png")),
            ("litecoin", cv2.imread("rc_items/coinflip/coinflip_item_litecoin.png")),
            ("monero", cv2.imread("rc_items/coinflip/coinflip_item_monero.png")),
            ("eos", cv2.imread("rc_items/coinflip/coinflip_item_eos.png")),
            ("rlt", cv2.imread("rc_items/coinflip/coinflip_item_rlt.png")),
            ("xrp", cv2.imread("rc_items/coinflip/coinflip_item_xrp.png")),
            ("xml", cv2.imread("rc_items/coinflip/coinflip_item_xml.png")),
            ("tether", cv2.imread("rc_items/coinflip/coinflip_item_tether.png")),
        ]

    def can_start(self):
        return check_image(self.start_img_path)

    def play(self):
        err = start_game(self.start_img_path)
        if err:
            return False
        start_game_msg(self.game)
        self.get_coin_fields()
        self.check_coins()
        self.match_coins()
        end_game()
        return True

    def get_coin_fields(self):
        screen = cv2.imread(screen_grab())
        matches = matchTemplates(
            [("card", cv2.imread("rc_items/coinflip/coinflip_back.png"))],
            screen,
            N_object=float("inf"),
            score_threshold=0.5,
            #maxOverlap=0.25,
            searchBox=None)
        for i in range(len(matches['BBox'])):
            self.coin_pos.append(matches['BBox'][i])

    def check_coins(self):
        ind = 0
        max_index = len(self.coin_pos)
        while ind < max_index:
            coin1_pos = self.coin_pos[ind]
            coin2_pos = self.coin_pos[ind+1]

            mouse_click(coin1_pos[0] + coin1_pos[2]/2, coin1_pos[1] + coin1_pos[3]/2, wait=0.1)
            mouse_click(coin2_pos[0] + coin2_pos[2]/2, coin2_pos[1] + coin2_pos[3]/2, wait=0.3)
            screen = cv2.imread(screen_grab())
            matches = matchTemplates(
                self.coin_images,
                screen,
                N_object=2,
                score_threshold=.7,
                maxOverlap=.25,
                searchBox=None)

            coin1 = (matches["TemplateName"][0], matches["BBox"][0])
            coin2 = (matches["TemplateName"][1], matches["BBox"][1])

            if coin1[0] == coin2[0]:
                self.coin_items.pop(coin1[0])
            else:
                self.coin_items[coin1[0]].append(coin1[1])
                self.coin_items[coin2[0]].append(coin2[1])

            ind += 2

    def match_coins(self):
        for coin in self.coin_items.values():
            if len(coin) == 2:
                c1 = coin[0]
                mouse_click(c1[0] + c1[2] / 2, c1[1] + c1[3] / 2, wait=0.05)
                c2 = coin[1]
                mouse_click(c2[0] + c2[2] / 2, c2[1] + c2[3] / 2, wait=0.05)
                time.sleep(1)


def main():
    Bots = [BotCoinFlip]
    global GAME_NUM
    while True:
        for bot in Bots:
            if bot().can_start():
                bot().play()


if __name__ == "__main__":
    setup()
    try:
        main()

    except KeyboardInterrupt:
        print("Program closed by User!")

    finally:
        print("\nStatistics:\n",
              "Time running: {!s}\n".format(datetime.datetime.now()-START_TIME),
              "Played Games:  {!s}\n".format(GAME_NUM+1)
              )
        shutil.rmtree('imgs')
