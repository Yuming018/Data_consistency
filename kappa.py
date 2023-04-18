import numpy as np
from copy import deepcopy
from collections import defaultdict 
from sklearn.metrics import cohen_kappa_score
from google_sheet import GoogleSheets
import time
import json

with open('data_index.json', 'r',encoding="utf-8") as f:
    data = json.load(f)
tag = data['tag']
type = data['type']
sub_type = data['sub_type']
old_employee = data['old_employee']
new_employee = data['new_employee']

def read_data(name):
    myWorksheet = GoogleSheets()
    data = myWorksheet.getWorksheet(
        spreadsheetId='1XVYC4OpOh0ghcbjt5UE8Qy_41BCvgD36AD3FJRzKkeY',
        range = name,
    )
    return data.values

def process_repeat(data_1, data_2):
    flag = True
    repeat_label_story = set()
    for _ in range(2):
        if flag:
            sotry_list = set([story[0] for story in data_1])
            repeat_label_story = count_paragraph(data_1, repeat_label_story)
            flag = False     
        else:
            sotry_list2 = set([story[0] for story in data_2])
            repeat_label_story = count_paragraph(data_2, repeat_label_story)
    
    return repeat_label_story, sotry_list.intersection(sotry_list2)

def count_paragraph(data, repeat_label_story):
    temp = set()
    for i in range(len(data)):
        if data[i][1]:
            label = data[i][0] + ' ' + data[i][1].split(' - ')[0]
        elif data[i][2]:
            label = data[i][0] + ' ' + data[i][2].split(' - ')[0]
        if label in temp:
            repeat_label_story.add(data[i][0])
        temp.add(label)
    return repeat_label_story

def make_union(data, repeat_label_story, Union_set, intersection_story):
    for i in range(len(data)):
        if data[i][0] in repeat_label_story or data[i][0] not in intersection_story:
            continue
        if data[i][1]:
            label = data[i][0] + '_' + data[i][1].split(' - ')[0]
        elif data[i][2]:
            label = data[i][0] + '_' + data[i][2].split(' - ')[0]
        if label not in Union_set:
            Union_set[label] = [-1, -1, -1]
    return Union_set

def decide_label(data, repeat_label_story, Union_set, intersection_story):
    for i in range(len(data)):
        if data[i][0] in repeat_label_story or data[i][0] not in intersection_story:
            continue
        temp = []
        if data[i][1]:
            tagging = data[i][1].split(' - ')
            temp.append(0)
            temp.append(type.index(tagging[0]))
            temp.append(sub_type.index(tagging[1]))
            Union_set[data[i][0] + '_' + tagging[0]] = temp
        elif data[i][2]:
            tagging = data[i][2].split(' - ')
            temp.append(1)
            try:
                temp.append(type.index(tagging[0]))
            except:
                print(i, tagging)
                input()
            temp.append(sub_type.index(tagging[1]))
            Union_set[data[i][0] + '_' + tagging[0]] = temp
    return Union_set

def cal_kappa(label_1, label_2):
    first = True
    context = ""
    score, count = 0, 0
    for key in sorted(label_1):
        kappa_score = cohen_kappa_score(label_1[key], label_2[key])
        if context != key.split("_")[0] and context != "":
            print("Kappa相似度為：", score/count, '\n')
            score = kappa_score
            count = 1
            first = True
        else:
            score += kappa_score
            count += 1
        context = key.split("_")[0]
        if first :
            print(context)
            first = not first  
        print(key.split("_")[1], ":", kappa_score)
        
    print("Kappa相似度為：", score/count, '\n')

if __name__ == '__main__':
    for old_e in old_employee :
        for new_e in new_employee:
            print(old_e, " ", new_employee[new_e])
            data_1 = read_data(old_e) 
            data_2 = read_data(new_employee[new_e]) 

            repeat_label_story, intersection_story = process_repeat(data_1, data_2)

            if not intersection_story:
                continue
            
            Union_set = defaultdict(list)
            Union_set = make_union(data_1, repeat_label_story, Union_set, intersection_story)
            Union_set = make_union(data_2, repeat_label_story, Union_set, intersection_story)
            
            label_1 = decide_label(data_1, repeat_label_story, deepcopy(Union_set), intersection_story)
            label_2 = decide_label(data_2, repeat_label_story, deepcopy(Union_set), intersection_story)
            
            cal_kappa(label_1, label_2)
        time.sleep(1000)