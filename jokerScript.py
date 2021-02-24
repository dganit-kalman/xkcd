import pyPdf
from StringIO import StringIO

# import numpy as np
# import pandas as pd
# from os import path
# from PIL import Image
# from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from bs4 import BeautifulSoup
# from urllib import request
import requests
import re


def getPDFContent(path):
    """
    gets path to a script in PDF form and extract it to a text form
    """
    content = ""
    p = file(path, "rb")
    f = open("text2.txt", "w+")
    pdf = pyPdf.PdfFileReader(p)
    j = 0
    for i in range(0, pdf.getNumPages()):
        print(str(j) + ": " + pdf.getPage(i).extractText())
        j += 1
        content += pdf.getPage(i).extractText() + "\n"
        f.write(re.sub("\d+", " ", pdf.getPage(i).extractText()).replace("INT.", "\nSCENE "
            "").replace("EXT.", "\nSCENE ").replace(".", ". ").encode("ascii", "ignore") + "\n")
    content = " ".join(content.replace(u"\xa0", " ").strip().split())
    # print(type(content))
    return content


def get_characters(url):
    """
    gets url of web with all the characters in the movie and extract them into a list
    """
    characters = []
    final_characters = []
    source_code = requests.get(url, )
    bs = BeautifulSoup(source_code.text, 'html.parser')
    bullets = bs.find("table", class_="cast_list")
    num_char = 0
    for link in bullets.findAll("tr"):
        character = link.find("td", class_="character")
        if character is None:
            continue
        name1 = []
        # print(character)
        for name in character.findAll("a"):
            # print(str(name)[48:-4])
            name1.append(str(name)[48:-4])

        if len(name1) == 0:
            # print(character)
            end = str(character)[35:].find("  ") + 35
            name1.append(str(character)[35:end - 2])
        # for name in name1:
        characters.append(name1[0].replace(">", "").upper())
        num_char += 1
        if num_char > 19:
            break
    for char in characters:
        if char.startswith('ON-SET'):
            char = char[7:]
            # print (char)
        if char not in final_characters:
            final_characters.append(char)
        # idx = char.find(" ")
        # if idx != -1:
        #     final_characters.append(char[:idx])
        # else:
        #     final_characters.append(char)
    # print(final_characters)
    return final_characters


def get_scenes():
    """
    separate the scenes in the script's text into list to every scene
    """
    scenes = []
    full_line = ""
    start = True
    f = open("text2.txt")
    for line in f.readlines():
        if line.startswith('SCENE'):
            scenes.append([full_line])
            full_line = ""
            full_line += line
        else:
            full_line += line

    # print(scenes)
    return scenes


def get_characters_in_scenes():
    """
    find all characters that exist in every scene
    """
    scenes = get_scenes()
    characters = get_characters("https://www.imdb.com/title/tt4154796/fullcredits")
    characters_scenes = []
    ch = ""
    empty = True
    f = open("scenes.txt", "w+")
    c = open("char.txt", "w+")
    for char1 in characters:
        ch = char1 + ', '
        c.write(ch)
    for scene in scenes:
        sc = []
        for char in characters:
            check_all = True
            p = char.find(" ")
            if p == -1 or char[0][p:].find(" ") != -1:
                check_all = False
            if (check_all and (scene[0].find(char) != -1 or scene[0].find(char[:p]) != -1 or
                              scene[0].find(char[p:]) != -1)) or (not check_all and scene[0].find(
                                char) != -1):
                sc.append(char)
                ch += ", "
                ch += char
                empty = False
        if empty:
            continue
        characters_scenes.append(sc)
        f.write(ch)
    # print(scenes)
    # print ()
    # print(characters_scenes)
    return characters_scenes


def translate_char_to_num():
    """
    translate all the characters' names to numbers
    """
    characters = get_characters("https://www.imdb.com/title/tt4154796/fullcredits")
    char_scene = get_characters_in_scenes()[:-1]
    scenes = []
    active_scene = []
    vanished_scenes = []
    death_tony_scene = 0
    death_natasha_scene = 0
    for j, scene in enumerate(char_scene):
        sc = []
        active = []
        for i, character in enumerate(characters):
            # print character
            # print char_scene
            if character in scene:
                active.append(i)
            else:
                sc.append([i])
        if not active or len(active) <= 2:
            vanished_scenes.append(j)
            continue
        sc.append(active)
        scenes.append(sc)
        active_scene.append(active)
    # find in which scenes natasha and tony dying
    for idx, sc in enumerate(active_scene):
        if 0 in sc:
            death_tony_scene = idx
        if 4 in sc:
            death_natasha_scene = idx
    for i in range(death_natasha_scene + 1, len(scenes)):
        scenes[i].remove([4])
    for i in range(death_tony_scene + 1, len(scenes)):
        scenes[i].remove([0])
    # print scenes
    return scenes, active_scene, death_tony_scene, death_natasha_scene, vanished_scenes


def interesting_scene():
    scenes = get_scenes()[1:-1]
    final_scenes = []
    name_places = ["AVENGERS COMPOUND", "STARK ECO-COMPOUND", "TOKYO", "NEW YORK CITY", "MORAG",
                   "STARK TOWER", "SANCTUARY"]
    places = {place: [] for place in name_places}
    scene, active_scene, d1, d2, vanished_scenes = translate_char_to_num()
    for i, sc in enumerate(scenes):
        if i not in vanished_scenes:
            final_scenes.append(sc)
    for j, sce in enumerate(final_scenes):
        # print j, sce
        for pl in name_places:
            if pl in sce[0]:
                places[pl].append(j)
    # print places
    return places

# # Read each line of the PDF
# pdfContent = StringIO(getPDFContent(
#     "C:\Users\dganit.kalman\Desktop\\needle\project\Avengers_Endgame.pdf").encode("ascii", "ignore"))

# translate_char_to_num()
