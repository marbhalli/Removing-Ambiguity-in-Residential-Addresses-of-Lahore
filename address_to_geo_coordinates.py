from audioop import add
import pandas as pd
import numpy as np
from nltk import ngrams
import regex as re
import Levenshtein
import json
import sys
sys.path.append('/Users/muhammadabdul/Desktop/Work/FINAL_address_togeo_coordinates/pythonProject')

def get_dictionary(locality_name,loc_names):
    dict_locality_blocks={}
    for locality in locality_name:
        if locality=='al noor' or locality=='chauburji' or locality=='larechs colony' :
            temp_lst=list(loc_names[loc_names.str.contains(f'^{locality} block')])
            temp_lst=[x for x in temp_lst if 'commercial' not in x and 'center' not in x and 'centre' not in x]
            temp_lst=[x[x.index(locality)+len(locality):].strip() for x in temp_lst]
        elif locality=='chauburji quarters':
            temp_lst=['chauburji quarters']
            dict_locality_blocks[locality]=temp_lst
            continue
        else:
            temp_lst=list(loc_names[loc_names.str.contains(f'^{locality} ')])
            temp_lst=[x for x in temp_lst if 'commercial' not in x and 'center' not in x and 'centre' not in x]
            temp_lst=[x[x.index(locality)+len(locality):].strip() for x in temp_lst]
        if len(temp_lst)>1:
            try:
                temp_lst.remove(locality)
            except:
                pass
        elif len(temp_lst)==0:
            temp_lst=[locality]
        dict_locality_blocks[locality]=temp_lst
    return dict_locality_blocks

def roman_numerals(string):
    lst_numerals=['i','ii','iii','iv','v','vi','vii','viii','ix','x','xi','xii','xiii']
    for numeral in lst_numerals:
        if bool(re.search(f'\s{numeral}\s',string)) or bool(re.search(f'^{numeral}\s',string)) or  bool(re.search(f'\s{numeral}$',string)):
            replaced=str(lst_numerals.index(numeral)+1)
            string= re.sub(f"\s{numeral}\s", f' {replaced} ', string)
            string= re.sub(f"^{numeral}\s", f'{replaced} ', string)
            string= re.sub(f"\s{numeral}$", f' {replaced}', string)
    return string

def get_house(address):
    #     for block in blocks:
    #         address=address.replace(f' {block} ',' ')
    lst_key_words = ['house', 'no', 'h', 'number']
    house_number = ''
    lst_ints_and_first_words = re.findall('([a-zA-Z]+)\s+([0-9]+)', address)
    first_int_from_left = re.findall('^([0-9]+)', address)
    all_ints_from_left = re.findall('([0-9]+)', address)
    temp = address.split()
    if len(first_int_from_left) != 0:
        house_number = first_int_from_left[0]

    if house_number != '':
        if int(house_number) > 10000 and len(all_ints_from_left) >= 2:
            index = 1
            while int(house_number) > 10000 and index <= len(all_ints_from_left) - 1:
                house_number = all_ints_from_left[index]
                index = index + 1
        house_number = str(int(house_number))
        for x in temp:
            if house_number in x:
                house_number = x
                return house_number

    for int_first_word in lst_ints_and_first_words:
        if int_first_word[0] in lst_key_words:
            house_number = int_first_word[1]
            house_number = str(int(house_number))
            for x in temp:
                if house_number in x:
                    house_number = x
                    return house_number

    if len(all_ints_from_left) == 0:
        house_number = '-1'
    else:
        house_number = all_ints_from_left[0]
    house_number = str(int(house_number))
    for x in temp:
        if house_number in x:
            house_number = x
            return house_number
    return '-1'

def key_word_LD(address,key_words):
    key_words_min_LD={}
    for key_word in key_words:
        temp_key_word=key_word
#         key_word=key_word.replace('sector','').strip()
        if len(address.split())<len(key_word.split()):
            continue
        if type(key_word)==float:
            continue
        if '/' in key_word:
            new_key_words=key_word.split('/')
            LD=[]
            for new_key_word in new_key_words:
                if len(new_key_word)==1 or 'phase' in key_word:
                    n_gram=ngrams(address.split(),len(new_key_word.split()))
                    grams=[" ".join(gram) for gram in n_gram]
                    for gram in grams:
                        LD.append(Levenshtein.distance(new_key_word,gram))
                    if 0 in LD:
                        key_words_min_LD[temp_key_word]=0
                    else:
                        pass
                else:
                    n_gram=ngrams(address.split(),len(new_key_word.split()))
                    grams=[" ".join(gram) for gram in n_gram]
                    for gram in grams:
                        LD.append(Levenshtein.distance(new_key_word,gram))
                    key_words_min_LD[temp_key_word]=min(LD)
        else:
            if len(key_word)==1 or 'phase' in key_word:
                LD=[]
                n_gram=ngrams(address.split(),len(key_word.split()))
                grams=[" ".join(gram) for gram in n_gram]
                for gram in grams:
                    LD.append(Levenshtein.distance(key_word,gram))
                if 0 in LD:
                    key_words_min_LD[temp_key_word]=0
                else:
                    pass
            else:
                LD=[]
                n_gram=ngrams(address.split(),len(key_word.split()))
                grams=[" ".join(gram) for gram in n_gram]
                for gram in grams:
                    LD.append(Levenshtein.distance(key_word,gram))
                key_words_min_LD[temp_key_word]=min(LD)
    if len(key_words_min_LD.values())==0:
        return [],1000,''
    minval = min(key_words_min_LD.values())
# =============================================================================
#     if minval>0.0:
#         return [],1000
# =============================================================================
    possible = [k for k, v in key_words_min_LD.items() if v==minval]
    word_used=''
    if len(possible)>1:
        sub_strings=[]
        for soc in possible:
            if '/' in soc:
                sub_strings = []
                new_key_words=soc.split('/')
                LD = {}
                for key_word in new_key_words:
                    LD_key_word=[]
                    n_gram=ngrams(address.split(),len(key_word.split()))
                    grams=[" ".join(gram) for gram in n_gram]
                    for gram in grams:
                        LD_key_word.append(Levenshtein.distance(key_word,gram))
                    index_sub_string_min_LD=LD_key_word.index(min(LD_key_word))
                    LD[grams[index_sub_string_min_LD] ] = min(LD_key_word)
                minval_key_word = min(LD.values())
                possible_key_word = [k for k, v in LD.items() if v==minval_key_word ]
                sub_strings.append(possible_key_word[0])
            else:
                n_gram=ngrams(address.split(),len(soc.split()))
                grams=[" ".join(gram) for gram in n_gram]
                LD=[]
                for gram in grams:
                    LD.append(Levenshtein.distance(soc,gram))
                sub_strings.append(grams[LD.index(min(LD))])
        index_sub_strings=[address.index(x) for x in sub_strings]
        possible=[possible[index_sub_strings.index(min(index_sub_strings))]]
    for key_word in possible:
        if '/' in key_word:
            new_key_words=key_word.split('/')
            for new_key_word in new_key_words:
                n_gram=ngrams(address.split(),len(new_key_word.split()))
                grams=[" ".join(gram) for gram in n_gram]
                for gram in grams:
                    if Levenshtein.distance(new_key_word,gram)==minval:
                        word_used=gram
                        return possible,minval,word_used
        else:
            n_gram=ngrams(address.split(),len(key_word.split()))
            grams=[" ".join(gram) for gram in n_gram]
            for gram in grams:
                if Levenshtein.distance(key_word,gram)==minval:
                    word_used=gram
                    return possible,minval,word_used

def locality(address,locality_name):
    original_address = address
    address=roman_numerals(address)
    # if 'near' in address:
    #     address=address[0:address.index('near')]
    # elif 'opposite' in address:
    #     address=address[0:address.index('opposite')]
    if len(address.split())<=1:
        return '-1'
    address=' '.join(address.split()).replace('^house ',' ').replace(' house ',' ').strip()
    society_key_words=locality_name['society key word']
    address_locality=''
    key_word_LD_=key_word_LD(address,society_key_words)
    society=key_word_LD_[0]

    
    minval_society=key_word_LD_[1]
    minval_locality=np.nan
    minval_add=np.nan
    
    word_used_society=key_word_LD_[2]
    word_used_locality=np.nan
    word_used_add=np.nan

    if 'gechs' and 'pgechs' in society:
        society=[x for x in society if x!='gechs']

    society_len = []
    for x in society:
        if '/' in x:
            split=x.split('/')
            for _ in split:
                n_gram=ngrams(address.split(),len(_.split()))
                grams=[" ".join(gram) for gram in n_gram]
                for gram in grams:
                    if Levenshtein.distance(_,gram)==minval_society and gram==word_used_society:
                        society_len.append(len(_))
                        break
        else:
            society_len.append(len(x))
    min_standard=2
    if len(society)==0:
        return '-1',(np.nan,np.nan),(np.nan,np.nan),(np.nan,np.nan)
    elif (max(society_len)<=3) and minval_society>0:
        return '-1',(np.nan,np.nan),(np.nan,np.nan),(np.nan,np.nan)
    elif max(society_len)>3 and minval_society>min_standard:
        return '-1',(np.nan,np.nan),(np.nan,np.nan),(np.nan,np.nan)

    locality_key_words=locality_name.query(f'`society key word`=="{society[0]}"')['locality key word']
    if len(locality_key_words.dropna())<=1 :
        address_locality=locality_name.query(f'`society key word`=="{society[0]}"')['name'].iloc[0]
        return address_locality,(minval_society,word_used_society),(minval_locality,word_used_locality),(minval_add,word_used_add)
    else:
        locality,minval_locality,word_used_locality=key_word_LD(address,locality_key_words.dropna())
        locality_len =[]
        for x in locality:
            if '/' in x:
                split=x.split('/')
                for _ in split:
                    n_gram=ngrams(address.split(),len(_.split()))
                    grams=[" ".join(gram) for gram in n_gram]
                    for gram in grams:
                        if Levenshtein.distance(_,gram)==minval_locality and gram==word_used_locality:
                            locality_len.append(len(_))
                            break
            else:
                locality_len.append(len(x))
        if len(locality_len)==0:
            min_standard = 0
        elif max(locality_len)<=3:
            min_standard = 0
        else:
            min_standard=2
        if minval_locality>min_standard:
            minval_locality=np.nan
            word_used_locality=np.nan
            address_locality=locality_name.query(f'`society key word`=="{society[0]}"')['last_resort_locality'].iloc[0]
            return address_locality,(minval_society,word_used_society),(minval_locality,word_used_locality),(minval_add,word_used_add)
        else:
            pass
        if len(locality)>1:
            locality_len=[len(x) for x in locality]
            locality=[locality[locality_len.index(max(locality_len))]]
        add_key_words=locality_name.query(f'`society key word`=="{society[0]}" and `locality key word`=="{locality[0]}"')['add. key word']
        if len(add_key_words.dropna())<=1:
            address_locality=locality_name.query(f'`society key word`=="{society[0]}" and `locality key word`=="{locality[0]}"')['name'].iloc[0]
            return address_locality,(minval_society,word_used_society),(minval_locality,word_used_locality),(minval_add,word_used_add)
        else:
            address_locality=locality_name.query(f'`society key word`=="{society[0]}" and `locality key word`=="{locality[0]}"')['last_resort_add'].iloc[0]
            if address_locality == 'dha phase 8':
                add_,minval_add,word_used_add=key_word_LD(original_address,add_key_words)
            else:
                add_,minval_add,word_used_add=key_word_LD(address,add_key_words)
            add__len =[]
            for x in add_:
                if '/' in x:
                    split=x.split('/')
                    for _ in split:
                        n_gram=ngrams(address.split(),len(_.split()))
                        grams=[" ".join(gram) for gram in n_gram]
                        for gram in grams:
                            if Levenshtein.distance(_,gram)==minval_add and gram==word_used_add:
                                add__len.append(len(_))
                                break
                else:
                    add__len.append(len(x))
            if len(add__len)==0:
                min_standard = 0
            elif max(add__len)<=3:
                min_standard = 0
            else:
                min_standard=2
            if minval_add>min_standard:
                minval_add=np.nan
                word_used_add=np.nan
                address_locality=locality_name.query(f'`society key word`=="{society[0]}" and `locality key word`=="{locality[0]}"')['last_resort_add'].iloc[0]
                return address_locality,(minval_society,word_used_society),(minval_locality,word_used_locality),(minval_add,word_used_add)
            if len(add_)>1:
                add__len=[len(x) for x in add_]
                add_=[add_[add__len.index(max(add__len))]]
            address_locality=locality_name.query(f'`society key word`=="{society[0]}" and `locality key word`=="{locality[0]}" and `add. key word`=="{add_[0]}"')['name'].iloc[0]
            return address_locality,(minval_society,word_used_society),(minval_locality,word_used_locality),(minval_add,word_used_add)



def get_block(address,blocks):
    len_block_lst=[len(x.replace('block','').replace('sector','').strip()) for x in blocks]
    address=address.replace('phase',' ').replace('scheme',' ')
    non_roman_address=roman_numerals(address)
    if all(i == 1 for i in len_block_lst):
        block_pred=''
        for block in blocks:
            temp_block_pred=''
            if 'sector' in block and 'block' in block:
                block_pred_lst=[]
                block=block.replace('block','').replace('sector','').strip()
                block_and_sector=block.split()
                for i in block_and_sector:
                    _1grams=ngrams(address.split(),1)
                    grams=[" ".join(gram) for gram in _1grams]
                    distance=int
                    if len(i)<=3:
                        distance=0
                    else:
                        distance=2
                    for gram in grams:
                        if Levenshtein.distance(i,gram)<=distance:
                            if i not in block_pred_lst:
                                block_pred_lst.append(i)
                temp_block_pred=' '.join(block_pred_lst)
                if temp_block_pred!='' and len(block_pred_lst)>=2:
                    block_pred=temp_block_pred
                    return block_pred
            else:
                block=block.replace('block','').replace('sector','').strip()
                _1grams=ngrams(address.split(),1)
                grams=[" ".join(gram) for gram in _1grams]
                if len(block.split())==2:
                    _2grams=ngrams(address.split(),2)
                    grams=[" ".join(gram) for gram in _2grams]
                    if len(block)<=3:
                        distance = 0
                    else:
                        distance = 2
                    for gram in grams:
                        if Levenshtein.distance(block,gram)<=distance:
                            temp_block_pred=block
    #                         return block_pred
                elif len(block.split())==1:
                    distance=int
                    if len(block)<=3:
                        distance = 0
                    else:
                        distance = 2
                    for gram in grams:
                        if Levenshtein.distance(block,gram)<=distance:
                            temp_block_pred=block
    #                         return block_pred
            if temp_block_pred.strip()!='':
                block_pred=temp_block_pred

            if block_pred=='':
                continue
            else:
                return block_pred
        return '-1'
    else:
        block_pred=''
        lst_non_roman_address=[x for x in non_roman_address if x!=' ']
        pointer=''
        for block in blocks:
            if len(block_pred.split())>=2:
                pointer='no'
            temp_block_pred=''
            if 'sector' in block and 'block' in block:
                block_pred_lst=[]
                block=block.replace('block','').replace('sector','').strip()
                block_and_sector=block.split()
                for i in block_and_sector:
                    try:
                        int(i)
                        _=True
                    except:
                        _=False
                    if len(i)<=1 or _:
                        _1grams=ngrams(address.split(),1)
                        grams=[" ".join(gram) for gram in _1grams]
                        if len(i)<=3:
                            distance = 0
                        else:
                            distance = 2
                        for gram in grams:
                            if Levenshtein.distance(i,gram)<=distance:
                                if i not in block_pred_lst:
                                    block_pred_lst.append(i)
                    else:
                        _1grams=ngrams(lst_non_roman_address,len(i))
                        grams=["".join(gram) for gram in _1grams]
                        distance=int
                        if len(i)<=3:
                            distance = 0
                        else:
                            distance = 2
                        for gram in grams:
                            if Levenshtein.distance(i,gram)<=distance:
                                if i not in block_pred_lst:
                                    block_pred_lst.append(i)
                                    if len(gram)==2:
                                        address=address.replace(f'{gram[0]} {gram[1]}',' ')
                temp_block_pred=' '.join(block_pred_lst)
                if temp_block_pred!='' and len(block_pred_lst)>=2:
                    block_pred=temp_block_pred
#                     return block_pred
            elif pointer!='no':
                block=block.replace('block','').replace('sector','').strip()
                _1grams=ngrams(address.split(),1)
                grams=[" ".join(gram) for gram in _1grams]
                if len(block)==2 and (block[0]!=block[1]):
                    _2grams=ngrams(lst_non_roman_address,len(block))
                    grams=["".join(gram) for gram in _2grams]
                    distance=int
                    if len(block)<=3:
                        distance = 0
                    else:
                        distance = 2
                    for gram in grams:
                        if Levenshtein.distance(block,gram)<=distance:
                            temp_block_pred=block
    #                         return block_pred
                else:
                    if len(block)<=3:
                        distance = 0
                    else:
                        distance = 2
                    for gram in grams:
                        if Levenshtein.distance(block,gram)<=distance:
                            temp_block_pred=block
    #                         return block_pred
            min_val_temp_block_pred =[]
            min_val_block_pred = []

            n_gram=ngrams(address.split(),len(temp_block_pred.split()))
            temp_block_pred_grams=[" ".join(gram) for gram in n_gram]

            for gram in temp_block_pred_grams:
                min_val_temp_block_pred.append(Levenshtein.distance(temp_block_pred,gram))

            n_gram=ngrams(address.split(),len(block_pred.split()))
            block_pred_grams=[" ".join(gram) for gram in n_gram]

            for gram in block_pred_grams:
                min_val_block_pred.append(Levenshtein.distance(block_pred,gram))
            
            if block_pred=='':
                block_pred=temp_block_pred
            elif min_val_temp_block_pred==[] or min_val_block_pred==[]:
                continue
            elif temp_block_pred.strip()!='' and len(block_pred.split())<=1 and min(min_val_temp_block_pred)<=min(min_val_block_pred) and min(min_val_temp_block_pred)<=2:
                block_pred=temp_block_pred

        if block_pred=='':
            return '-1'
        else:
            return block_pred


def block(address, locality, dict_locality_blocks, house_number, locality_with_e):
    if locality == '-1':
        return '-1'
    keys = pd.Series(dict_locality_blocks.keys())
    localities_to_search_for_block = keys[keys.str.contains(locality)]
    lst_address = address.split()
    
    for index in range(0,len(lst_address) - 1):
        if len(lst_address[index]) == 1 and lst_address[index + 1] in locality_with_e:
            lst_address.pop(index)
            break
    address = ' '.join(lst_address)
    for locality in localities_to_search_for_block:
        blocks = dict_locality_blocks[locality]
        blocks.sort()
        if len(blocks) == 1 and blocks[0] == locality and len(localities_to_search_for_block) == 1:
            return '-2'
        elif len(blocks) == 1 and blocks[0] == locality and len(localities_to_search_for_block) > 1:
            continue
        if house_number not in address:
            pred_block = get_block(address, blocks)
            if pred_block != '-1':
                return pred_block
        else:
            index1 = address.index(house_number) + len(house_number)
            pred_block = get_block(address[index1:], blocks)
            if pred_block != '-1':
                return pred_block
            else:
                index2 = address.index(house_number) - 1
                pred_block = get_block(address[0:index2], blocks)
                if pred_block != '-1':
                    return pred_block
    pred_block = '-1'
    return pred_block



def address_predict(roman_numerals,get_house,address,locality,block,locality_name,dict_locality_blocks,locality_with_e):
    try:
        lst_puntuation=['`','!','@','#','$','%','^','&','*','(',')','-','_','+','=','{','}','[',']',
                       '|',':',';','"',',','<','>',',','.','?','~','lahore']
        address=address.lower()
        address=address.replace('p-',' ').replace('h-no',' ').strip()
        for punctuation in lst_puntuation:
            address=address.replace(punctuation,' ').strip()
        to_locality_address=address.replace('house',' ').replace(' no ',' ').strip()
        house_number=get_house(address)
        locality_=locality(to_locality_address,locality_name)
        block_=block(address,locality_[0],dict_locality_blocks,house_number,locality_with_e)
        if block_=='-1' and '/' in house_number:
            address=address.replace('/',' ').strip()
            block_=block(address,locality_[0],dict_locality_blocks,house_number,locality_with_e)
        if block_ in house_number and block_!='-1':
            house_number=re.findall(r'(\d+)',house_number)[0]
        wordslist = list(locality_[0].split())
        if block_ in locality_[0] and wordslist.count(block_)==1:
            address=address.replace(block_,' ')
            block_=block(address,locality_[0],dict_locality_blocks,house_number,locality_with_e)
        if locality_=='-1':
            to_geo_coordinates='-1'
        else:
            to_geo_coordinates=locality_[0]
        try:
            if len(house_number.split('/'))==2:
                house_number = str(int(house_number.split('/')[0])) + '/' + str(int(house_number.split('/')[1]))
            else:
                house_number = str(int(house_number))
        except:
            pass
        prediction_str=house_number + ',' + block_ +','+ to_geo_coordinates
        return house_number,block_,locality_,prediction_str
    except:
        return 'faced some error','faced some error','faced some error','faced some error'


def get_url(index, x, zameen_data):
    url = 'https://www.zameen.com/plotfinder/Lahore-28/'
    soc_name = zameen_data[index]['plots'][x]['hierarchy'][3]['name']
    soc_id = zameen_data[index]['plots'][x]['hierarchy'][3]['id']
    plot_id = zameen_data[index]['plots'][x]['id']
    if len(soc_name.split()) > 1:
        soc_name = '-'.join(soc_name.split())
    url = url + soc_name + '-' + str(soc_id) + '/' + str(plot_id)

    return url


def get_geo_coordintaes(locality,block,house,zameen_data,dict_locality_blocks):
    keys=pd.Series(dict_locality_blocks.keys())
    localities_to_search_for_block=list(keys[keys.str.contains(locality)])
    len_block_lst=[]
    counter=0
    if len(localities_to_search_for_block)>1:
        for _ in localities_to_search_for_block:
            if _==locality:
                localities_to_search_for_block=[locality]
    for i in range(len(localities_to_search_for_block)):
            blocks_i=dict_locality_blocks[localities_to_search_for_block[i]]
            series_block_i=pd.Series(blocks_i).str.replace('block',' ').str.replace('sector',' ').str.strip()
            for j in range(i+1,len(localities_to_search_for_block)):
                blocks_j=dict_locality_blocks[localities_to_search_for_block[j]]
                series_block_j=pd.Series(blocks_j).str.replace('block',' ').str.replace('sector',' ').str.strip()
                truth_value=[True for block_i in series_block_i for block_j in series_block_j if block_i==block_j]
                if sum(truth_value)>=1:
                    counter=counter+1
                    break
            if counter>0:
                break
    if counter>0:
        return '',"could not find geo coordinates,block was not unique",''
    for x in localities_to_search_for_block:
        blocks=dict_locality_blocks[x]
        len_block_lst.append([len(x.replace('block','').replace('sector','').strip()) for x in blocks])
    len_block_lst = [item for sublist in len_block_lst for item in sublist]
    off_set=np.array([-0.07379573,  0.0154113 ])
    if locality=='-1':
        return '',"could not find geo coordinates,locality not mentioned",''
    else:
        lst_possible_places=[]
        list_localities=list(dict_locality_blocks.keys())
        for i in range(len(zameen_data)):
            if bool(re.findall(f'{locality}',zameen_data[i]['name'].lower())) or bool(re.findall(f'^{locality}$',zameen_data[i]['name'].lower())):
                lst_possible_places.append((i,zameen_data[i]['name']))
            else:
                continue
        for index,place in lst_possible_places:
            modified_str=' '.join(place.lower().replace('sector','').replace('block','').split())
            if len(zameen_data[index]['plots'])==0:
                continue
            if all(i == 1 for i in len_block_lst):
                if bool(re.findall(f' {block}$',modified_str)) or block=='-2':
                    for x in range(len(zameen_data[index]['plots'])):
                        if zameen_data[index]['plots'][x]['plot_number']==house:
                            return 'accurate upto house',np.array(zameen_data[index]['plots'][x]['geometry']['coordinates'])+off_set,get_url(index,x,zameen_data)
                    return 'accurate upto block',zameen_data[index]['plots'][0]['geometry']['coordinates']+off_set,get_url(index,0,zameen_data)
                else:
                    continue
            else:
                if (bool(re.findall(f' .{{2}} {block}$',modified_str)) or bool(re.findall(f' {block} {{1}}.$',modified_str))):
                    for x in range(len(zameen_data[index]['plots'])):
                        if zameen_data[index]['plots'][x]['plot_number']==house:
                            return 'accurate upto house,block compromised',np.array(zameen_data[index]['plots'][x]['geometry']['coordinates'])+off_set,get_url(index,x,zameen_data)
                    return 'accurate upto block,block compromised',np.array(zameen_data[index]['plots'][x]['geometry']['coordinates'])+off_set,get_url(index,x,zameen_data)
                elif bool(re.findall(f' {block}$',modified_str)) or block=='-2':
                    for x in range(len(zameen_data[index]['plots'])):
                        if zameen_data[index]['plots'][x]['plot_number']==house:
                            return 'accurate upto house',np.array(zameen_data[index]['plots'][x]['geometry']['coordinates'])+off_set,get_url(index,x,zameen_data)
                    return 'accurate upto block',zameen_data[index]['plots'][0]['geometry']['coordinates']+off_set,get_url(index,0,zameen_data)
                else:
                    continue

        if len(lst_possible_places)!=0 and (len(zameen_data[lst_possible_places[0][0]]['plots'])!=0 or len(zameen_data[lst_possible_places[1][0]]['plots'])!=0):
            index=lst_possible_places[0][0]
            return 'accurate upto locality',np.array(zameen_data[index]['plots'][0]['geometry']['coordinates'])+off_set,get_url(index,0,zameen_data)
        else:
            return '','could not find geo coordinates',''

def initialize_files():
    locality_name = pd.read_csv('/Users/muhammadabdul/Desktop/Work/FINAL_address_togeo_coordinates/pythonProject/locality_name.csv').loc[:, 'name':]
    df_obj = locality_name.select_dtypes(['object'])
    locality_name[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())
    loc_names = pd.read_csv('/Users/muhammadabdul/Desktop/Work/FINAL_address_togeo_coordinates/pythonProject/loc_names.csv', header=None)[0]
    loc_names = loc_names.str.lower()
    loc_names = loc_names.str.strip()

    f = open('/Users/muhammadabdul/Desktop/Work/FINAL_address_togeo_coordinates/pythonProject/PlotFinderFinal-Complete-Cleaned.json', )
    zameen_data = json.load(f)

    return locality_name, loc_names, zameen_data


locality_name,loc_names,zameen_data=initialize_files()
dict_locality_blocks=get_dictionary(locality_name['name'],loc_names)
locality_with_e=[
    
'ahbab',
'iram',
'quaid',
'daman',
'ahbab',
'aiwan',
'habib',
'jinnah',
'lahore',
'madina',
'mehrab',
'mustafa',
'rail',
'ravi',
'sardar',
'shalimar',
'amin',
'ameen']

def import_functions():
    roman_numerals_ = roman_numerals
    get_house_ = get_house
    locality_ = locality
    block_ = block
    locality_name_ = locality_name
    dict_locality_blocks_ = dict_locality_blocks
    locality_with_e_ = locality_with_e
    return roman_numerals_,get_house_,locality_,block_,locality_name_,dict_locality_blocks_,locality_with_e_

def single_address(address_input):

    roman_numerals,get_house,locality,block,locality_name,dict_locality_blocks,locality_with_e = import_functions()
    address=address_input
    temp_series=pd.Series(dict_locality_blocks.keys())
    house_number,block_,locality_,prediction_str=address_predict(roman_numerals,get_house,address,locality,block,locality_name,dict_locality_blocks,locality_with_e)
    if locality_=='-1':
        to_geo_coordinates='-1'
    else:
        to_geo_coordinates=locality_[0]
    geo_coordinates=get_geo_coordintaes(to_geo_coordinates,block_,house_number,zameen_data,dict_locality_blocks)
    print(f'address: {address}')
    print('house:',house_number)
    print('block:',block_,)
    print('locality:',locality_[0])
    print(f'prediction: {prediction_str}')
    print(f'geo coordinates:{geo_coordinates[1]}')
    print(f'accuracy: {geo_coordinates[0]}')
    print(f'zameen url: {geo_coordinates[2]}')


def predict(df_address):
    roman_numerals,get_house,locality,block,locality_name,dict_locality_blocks,locality_with_e = import_functions()
    index=0
    prediction=[]
    geo_coordinates_lst=[]
    geo_coordinates_accuracy_lst=[]
    zameen_link=[]
    society_LD=[]
    society_gram=[]
    locality_LD=[]
    locality_gram=[]
    add_LD=[]
    add_gram=[]
    match_=[]
    for address in df_address.dropna():
        if type(address)==float:
            continue
        print(f'address: {address}')
        house_number,block_,locality_,prediction_str=address_predict(roman_numerals,get_house,address,locality,block,locality_name,dict_locality_blocks,locality_with_e)
        if locality_=='-1':
            to_geo_coordinates='-1'
            society_LD.append(np.nan)
            society_gram.append(np.nan)
            
            locality_LD.append(np.nan)
            locality_gram.append(np.nan)
            
            add_LD.append(np.nan)
            add_gram.append(np.nan)
        else:
            to_geo_coordinates=locality_[0]
            society_LD.append(locality_[1][0])
            society_gram.append(locality_[1][1])

            locality_LD.append(locality_[2][0])
            locality_gram.append(locality_[2][1])
            
            add_LD.append(locality_[3][0])
            add_gram.append(locality_[3][1])
        if locality_[1][0]==0 and locality_[2][0]==0 and locality_[3][0]==0:
            match_.append('exact match')
        elif locality_[1][0]==0 and locality_[2][0]==0 and type(locality_[3][0])==float:
            match_.append('exact match')
        elif locality_[1][0]==0 and type(locality_[2][0])==float and type(locality_[3][0])==float:
            match_.append('exact match')
        else:
            match_.append('not exact match')
        print('house:',house_number)
        print('block:',block_)
        print('locality:',to_geo_coordinates)
        print(f'prediction: {prediction_str}')
        prediction.append(prediction_str)
        geo_coordinates=get_geo_coordintaes(to_geo_coordinates,block_,house_number,zameen_data,dict_locality_blocks)
        print(f'geo coordinates:{geo_coordinates[1]}')
        print(f'accuracy: {geo_coordinates[0]}')
        geo_coordinates_lst.append(geo_coordinates[1])
        geo_coordinates_accuracy_lst.append(geo_coordinates[0])
        print(f'zameen url: {geo_coordinates[2]}')
        zameen_link.append(geo_coordinates[2])
        index=index+1
        print()
    
    prediction_df=pd.DataFrame({'prediction':prediction,
                                'geo_coordinates':geo_coordinates_lst,
                                'geo_coordinates_accuracy':geo_coordinates_accuracy_lst,
                                'address':df_address.dropna(),
                                'zameen link':zameen_link,
                                'society LD':society_LD,
                                'society_gram':society_gram,
                                'locality_LD':locality_LD,
                                'locality_gram':locality_gram,
                                'add_LD':add_LD,
                                'add_gram':add_gram,
                                'match':match_
                                })
    return  prediction_df

