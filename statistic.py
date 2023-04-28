import json
import re
#dataset1表示label不为空的，dataset2表示label和evidence都不为空的
# new_file_list=["dataset_1.json", "dataset_2.json"]

def read_file(path):
    with open(path,"r") as file_obj:
        return json.load(file_obj)

def write_file(path,data):
    with open(path,"a+") as file_obj:
        json.dump(data,file_obj)

def write_fileline(path, data):
    with open(path, "a+") as file_obj:
        file_obj.write("[")
        for i, _ in enumerate(data):
            json.dump(_, file_obj)
            if i < len(data)-1:
                file_obj.write(",\n")
        file_obj.write("]")
        file_obj.close()

def statistic_blank_label(data_src):
    l_num=0
    e_num=0
    le_num=0
    for data_item in data_src:
        useful_label=[]
        if data_item["labels"]==[]:
            l_num+=1
        #标签不为空的
        else:
            # write_file("./DocREDdata/train_annotated1.json", data_item)
            # write_file("./DocREDdata/train_distant1.json", data_item)
            # write_file("./DocREDdata/dev1.json",data_item)
            for label in data_item["labels"]:
                if label["evidence"]==[]:
                    e_num+=1
                #标签和证据不为空的
                else:
                    useful_label.append(label)
            if useful_label==[]:
                le_num+=1
            else:
                data_item["labels"]=useful_label
                # write_file("./DocREDdata/train_annotated2.json", data_item)
                # write_file("./DocREDdata/dev2.json", data_item)
    return l_num,le_num

def statistic_evidence(data_src):
    evidence0=0
    evidence1=0
    evidence2=0
    evidence3=0
    evidence4=0
    evidence5=0
    evidence6=0
    evidence7=0
    evidence8=0
    for data_item in data_src:
        for label in data_item["labels"]:
            if len(label["evidence"])==0:
                evidence0+= 1
            if len(label["evidence"])==1:
                evidence1+=1
            if len(label["evidence"])==2:
                evidence2+=1
            if len(label["evidence"])==3:
                evidence3+=1
            if len(label["evidence"])==4:
                evidence4+=1
            if len(label["evidence"])==5:
                evidence5+=1
            if len(label["evidence"])==6:
                evidence6+=1
            if len(label["evidence"])==7:
                evidence7+=1
            if len(label["evidence"])>=8:
                # print(">8:", label)
                evidence8+=1
    evidence=evidence0+evidence1+evidence2+evidence3+evidence4+evidence5+evidence6+evidence7+evidence8
    print(evidence0,evidence1,evidence2,evidence3,evidence4,evidence5,evidence6,evidence7,evidence8,evidence)
    # print("1個證據佔比%.2f,2個證據佔比%.2f,3個證據佔比%.2f,4個證據佔比%.2f,5個證據佔比%.2f,5個以上證據佔比%.2f" % (evidence1/evidence,evidence2/evidence,evidence3/evidence,evidence4/evidence,evidence5/evidence,evidence6/evidence))

def statistic_entity_type(data_src):
    type_lib = []
    for data_item in data_src:
        for item in data_item["vertexSet"]:
            for i in item:
                if i["type"] not in type_lib:
                    type_lib.append(i["type"])
    return type_lib

def statistic_vertexset(data_src):
    sum=[]
    for data_item in data_src:
        sum1 = 0
        for item in data_item["vertexSet"]:
            if item!=[]:
                sum1+=1
        sum.append(sum1)
    return sum

def get_keys(dct,value):
    return [k for (k,v) in dct.items() if v==value]

def acronym(phrase):
    new_phrase=[]
    phrase=str(phrase)
    phrase_list=phrase.split(" ")
    for i in phrase_list:
        if i.isupper()==True:
            new_phrase.append(i)
        else:
            if i!="" and i[0].isupper()==True:
                new_phrase.append(i[0])
            else:
                new_phrase.append("")
    s="".join(j for j in new_phrase)
    return s

def delete_wrongname(data_src,data_src1):
    item_num=[]
    data = []
    for data_item in data_src:
        useful_name_all = []
        item=0 # 用于统计数据集的每一条的顶点数
        for subdata_item in data_item["vertexSet"]:
            item+=1
            name = {}
            useful_name=[]
            key1 = []
            current1 = []
            item_list=sorted(subdata_item,key=lambda x:len(x['name']),reverse=True)
            for i in item_list:
                current=i["name"]
                flag=True
                for key in name:
                    reg="[^0-9A-Za-z\u4e00-\u9fa5]"
                    key1.append([re.sub(reg,'',w1) for w1 in key.split()])
                    current1.append([re.sub(reg,'',w2) for w2 in current.split()])
                    if key.startswith(current) or key.endswith(current) or len([x for x in key1[0] if x in current1[0]])>0:
                        name[key].append(i)
                        flag=False
                        break
                    else:
                        if acronym(key).isupper() == True and acronym(current).isupper() == True :
                            if len([x1 for x1 in acronym(key) if x1 in acronym(current)]) > 0:
                                name[key].append(i)
                                flag = False
                                break
                if flag:
                    name[current]=[i]
            sort_names=sorted(name.values(),key=lambda x: len(x), reverse=True)
            if len(sort_names[0])==1:
                useful_name=item_list
            else:
                useful_name=sort_names[0]
            useful_name_all.append(useful_name)
        item_num.append(item)
        data_item["vertexSet"] = useful_name_all
        data.append(data_item)
    write_fileline(data_src1, data)
    data_src2= read_file(data_src1)
    item_num1 = statistic_vertexset(data_src2)
    return item_num,item_num1


def List_Cp_List(list1,list2):
    if list1==list2:
        print("两个列表中数据一致！")
    elif len(list1)==len(list2):
        for i in range(len(list1)):
            if list1[i]!=list2[i]:
                print("表I中第%s位元素[%s]!=表II中第%s位[%s]"%(i+1,list1[i],i+1,list2[i]))
    elif len(list1)>len(list2):
        for i in range(len(list2)):
            if list1[i]!=list2[i]:
                print("表I中第%s位元素[%s]!=表II中第%s位[%s]" % (i + 1, list1[i], i + 1, list2[i]))
        for i in range(len(list2),len(list1)):
            print("表I中第%s位元素[%s]不在表II中" % (i + 1, list1[i]))
    else:
        for i in range(len(list1)):
            if list1[i]!= list2[i]:
                print ("表I中第%s位元素[%s]!=表II中第%s位[%s]" % (i + 1, list1[i], i + 1, list2[i]))
    for i in range(len(list2), len(list1)):
        print("表I中第%s位元素[%s]不在表II中" % (i + 1, list2[i]))

def verify_wrongname(data_src):
    null="__NULL__"
    item1=[]
    for data_item in data_src:
        err_cnt = 0
        for item in data_item["vertexSet"]:
            name=null
            for i in item:
                if name==null:
                    name=i["name"]
                    continue
                if name!=null and name!=i["name"]:
                    err_cnt+=1
                    print(name)
        item1.append(err_cnt)
    print(item1)
    for i in range(len(item1)):
        if item1[i]!=0:
            print("Dataset中第%sline元素[%s]err" % (i + 1, item1[i]))

if __name__=="__main__":
    # #原始文件
    # train_annotated_set=read_file("./data/train_annotated.json")
    # train_distant_set=read_file("./data/train_distant.json")
    # dev_set=read_file("./data/dev.json")
    # test_set=read_file("./data/test.json")
    #
    # #去掉空label文件
    # train_annotated_set1 = read_file("./data/train_annotated1.json")
    # train_distant_set1 = read_file("./data/train_distant1.json")
    # dev_set1 = read_file("./data/dev1.json")
    #
    # #去掉错误name文件
    # train_annotated_set2 = read_file("./data/train_annotated2.json")
    # train_distant_set2 = read_file("./data/train_distant2.json")
    # dev_set2 = read_file("./data/dev2.json")
    # test_set2 = read_file("./data/test2.json")

    # #任务一 统计空label和存储处理后的数据集
    # t1_l,t1_le=statistic_blank_label(train_annotated_set)
    # t2_l,t2_le = statistic_blank_label(train_distant_set)
    # d_l,d_le=statistic_blank_label(dev_set)
    # print("人工标准训练集空label个数为:%d\n远程监督训练集空label个数为:%d\n验证集空label个数为:%d"%(t1_l,t2_l,d_l))
    # print("人工标准训练集空label,非空label全空证据个数为:%d\n验证集空label,非空label，全空证据个数为:%d"%(t1_le,d_le))

    # #任务二 统计实体类型
    # entity_label1=statistic_entity_type(train_annotated_set)
    # entity_label2=statistic_entity_type(train_distant_set)
    # entity_label3=statistic_entity_type(dev_set)
    # entity_label4=statistic_entity_type(test_set)
    # print("人工标准训练集实体类型:%s\n远程监督训练集实体类型:%s\n验证集实体类型:%s\n测试集实体类型:%s"%(entity_label1,entity_label2,entity_label3,entity_label4))

    # #任务三 去除vertexset中name不一致 #任务四 验证去除name歧义之后,数据条数是否发生变化
    # item_num,item_num1=delete_wrongname(train_annotated_set1,"/home/htt/Desktop/gnn/data/train_annotated2.json")
    # print("数据集原有数据条数:%d\n另存之后数据条数%d"%(len(item_num),len(item_num1)))
    # List_Cp_List(item_num, item_num1)
    #
    # item_num2, item_num3 = delete_wrongname(train_distant_set1, "/home/htt/Desktop/gnn/data/train_distant2.json")
    # print("数据集原有数据条数:%d\n另存之后数据条数%d" % (len(item_num2), len(item_num3)))
    # List_Cp_List(item_num2, item_num3)
    #
    # item_num4, item_num5 = delete_wrongname(dev_set1, "/home/htt/Desktop/gnn/data/dev2.json")
    # print("数据集原有数据条数:%d\n另存之后数据条数%d" % (len(item_num4), len(item_num5)))
    # List_Cp_List(item_num4, item_num5)
    # #
    # item_num6, item_num7 = delete_wrongname(test_set, "/home/htt/Desktop/gnn/data/test2.json")
    # print("数据集原有数据条数:%d\n另存之后数据条数%d"%(len(item_num6), len(item_num7)))
    # List_Cp_List(item_num6, item_num7)

    #任务四：統計不同證據個數佔比
    # statistic_evidence(dev_set2)

    #任务五：数据集统计信息
    # f = open('./data/dev.json', 'r', encoding='utf-8')
    # data = json.load(f)
    # num_sents = 0
    # len_sents = 0
    # num_evidences = 0
    # num_mentions = 0
    # for slice in data:
    #     mention_list=slice['vertexSet']
    #     num_mention=sum([len(mention) for mention in mention_list])
    #
    #     sent_list = slice['sents']
    #     num_sent = len(sent_list)
    #
    #     len_sent = 0
    #     num_evidence=0
    #     evidence_list=slice['labels']
    #     for sent in sent_list:
    #         len_sent += len(sent)
    #
    #     len_sent /= num_sent
    #     num_sents += num_sent
    #     num_mention/=num_sent
    #     num_mentions += num_mention
    #     len_sents += len_sent
    #     for evidence in evidence_list:
    #         num_evidence+=len(evidence["evidence"])
    #     num_evidence/=num_sent
    #     num_evidences += num_evidence
    # ave_mention=num_mentions/len(data)
    # ave_num = num_sents / len(data)
    # ave_len = len_sents / len(data)
    # ave_evidence=num_evidences/ len(data)
    # print('ave mention:', ave_mention)
    # print('ave num:', ave_num)
    # print('ave len:', ave_len)
    # print('ave evidence:', ave_evidence)