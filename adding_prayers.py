import requests
import json
import re
# from urllib.request import urlretrieve
from pathlib import Path
import os
from pydub import AudioSegment


# Converted te refrences to numbers by removing the brackets
def extract_the_digits(refrence):
    match = re.search(r'\d+:?(\s+)?\d+(?:-\d+)?',refrence)
    if match == None:
        ref = "empty"
    else:
        ref = match.group(0)
    return ref

# extracted the chapters and verses in each chapter
def chapter_and_verse(ref):
    verses = []
    match = re.match(r'^\d+:',ref)
    match2 = re.search(r'(?P<start>\d+)-(?P<stop>\d+)',ref)
    match3 = re.search(r':\d+$',ref)
    if match == None:
        chapter = "null"
    else:
        match = match.group(0).replace(':','')
        chapter = int(match)

    if match2 != None:
        try:
            for i in range(int(match2.group('start')),int(match2.group('stop'))+1):
                verses.append(i)
        except Exception as e:
            print(e)
    elif match3 != None:
        result = match3.group(0).replace(':','')
        verses.append(result)
    else:
        pass
    return (chapter,verses)
    

# compiling the prayer
def compile_prayer_audio(folder,id):
    prayer = None
    count = 1
    for file in os.listdir(folder):
        path = f'{folder}/{file}'
        if count == 1:
            prayer = AudioSegment.from_mp3(path)
        else:
            audio = AudioSegment.from_mp3(path) 
            prayer += audio
        count += 1
    with open(f"Prayer Audio/prayer_audio{id}.mp3",'wb') as prayer_audio:
        prayer.export(prayer_audio,format="mp3")


    
# Creating folders
try:
    os.mkdir("Prayer Audio")
except Exception as e:
    # print("Directory Error: ",e)
    pass

"""
This part might be a little clumsy because we would try to read a file and still rewrite the same file. And we would also be getting the arabic text using an external API: "https://quranapi.pages.dev/api/{chapter}/{verse}.json" to get the texts and audio there would be preprocessing in the audio because we would extract, concatenate and save the file after everything before adding to our api.
"""
with  open("test.json",'r',) as file:
    data = json.load(file)
for i in range(len(data)):
    id = data[i]['id']
    arabics = []
    refrence = data[i]['refrence']
    ref = extract_the_digits(refrence)
    chapter, verses = chapter_and_verse(ref)
    file =  open("new.json",'w')
    if chapter != "null":
        count = 0
        for verse in verses:
            chapter = int(chapter)
            verse = int(verse)
            request_url = f"https://quranapi.pages.dev/api/{chapter}/{verse}.json"
            response_data = requests.get(request_url)
            response_data = response_data.json()
            # getting the arabic text
            arabic = response_data['arabic1']
            # adding the arabic text to a list
            arabics.append(arabic)
            # getting verse audio url
            var = response_data["audio"]["1"]
            verse_audio_url = var["originalUrl"]
            # opening a new file for each verse and adding audio file to it
            try:
                os.mkdir("Extracted verses")
            except Exception as e:
                pass
            with open(f"Extracted verses/verse{count}.mp3",'wb') as verse_audio_file: 
                audio_response = requests.get(verse_audio_url,stream=True)
                audio_response = audio_response.content
                verse_audio_file.write(audio_response)
            count += 1
        compile_prayer_audio("Extracted verses/",id)
        # Codes to run after the for loop
        try:
            os.rmdir("Extracted verses")
        except Exception as e:
            pass
        data[i].update({"arabic":arabics})
        prayer_file = open("test.json",'w')
        json.dump(data,prayer_file,indent=4)
        break
    else:
        print("Chapter is null")
    break

prayer_file.close()