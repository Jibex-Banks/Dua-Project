import json


# function to re assign id's
def reassign_id(file_path,new_path="json/unique.json"):
    new_data = []
    if file_path == None :
        return "Invalid File"
    with open(file_path,'rb') as jf:
        current_file = json.load(jf)
        
        for index,item in enumerate(current_file):
            item.update({'id': index+1})
            new_data.append(item)

        
    with open(new_path,'w') as new_file:
        json.dump(new_data,new_file,ensure_ascii=True,indent=4)


# reassign_id("json/dua_api.json","json/dua_api.json")
    
# GETTING TRANSLITERATIONS FOR ARABIC TEXTS
from lang_trans.arabic import iso233

def get_transliteration(arabic_text):
    translated_text = iso233.transliterate(arabic_text)
    return translated_text


print(get_transliteration("بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ"))