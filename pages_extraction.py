import pdfplumber as pfb
import re
import json

prayers = []
""" 
{
   "id":0,
   "title":"",
    "background":"",
    "refrence":"",
    "meaning":""
}
"""
collecting_title = True
id = None
title = ""
background =""
refrence = ""
meaning = ""
title_font = ""
background_font = ""
meaning_font = ""

with pfb.open("Treasure_House_of_Prayers.pdf") as file:
    for page in file.pages[18:56]:
            for line in page.extract_text_lines():
                font = line.get("chars",[])
                fontname = font[0]["fontname"]
                if re.match(r'^(PRAYERS)$',line["text"]):
                    pass
                else:
                     if re.match(r'^\d+.\s+\w+',line["text"]):
                        prayers.append(
                                {
                                    "id":id,
                                    "title":title.strip(),
                                    "background":background.strip(),
                                    "refrence":refrence.strip(),
                                    "meaning":meaning.strip()
                                }
                        )
                        id = None
                        title = ""
                        background = ""
                        refrence = ""
                        meaning = ""
                        background_font = ""
                        meaning_font =""
                        title_font = fontname
                        matchs = re.match(r'^(\d+).(\s+\w+)',line["text"])
                        id = int(matchs.group(1))
                        title = re.sub(r'\d+.\s','',str(line["text"]))
                     elif fontname == title_font :
                        title += " "+line['text'] 
                     elif fontname != title_font and title_font != "":
                        title_font = ""
                        background_font = fontname
                        text = str(line["text"]).replace('tsa','t (S.A.W) ')
                        background += re.sub(r'\d+','',text)
                     elif fontname == background_font :
                        text = str(line["text"]).replace('tsa','t (S.A.W) ')
                        background += " " + re.sub(r'\d+','',text)
                     elif fontname != background and background != "":
                        background_font = ""
                        match = re.match(r'\(\w.+\d+:(?:\s+)?\d+(?:-\d+)?\)',line["text"])
                        if match != None:
                            refrence = match.group(0)
                            meaning_font = fontname
                        elif refrence != "" and meaning_font == fontname:
                            text = str(line["text"]).replace('tsa','t (S.A.W) ')
                            meaning += " " + re.sub(r'\d+','',text)
test = open("test2.json",'w')
json.dump(prayers,test,indent=4)