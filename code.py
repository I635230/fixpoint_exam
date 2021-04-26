########################################
# setting
timeout_bound = 2 # 1～
overload_judge_threshold = 3 # 1～
overload_bound = 5 # 0～
adress_type = "subnet" # server adress, subnet
output_type = "failure" # failure, overload
#--------------------------------------#


########################################
# import
from datetime import datetime as dt
#--------------------------------------#


########################################
# sub definition

## 入力
def input_log() : 
    log_list = []
    log_append = log_list.append
    while(True) : 
        try : 
            log_append(input().split(","))
        except EOFError : 
            break
    return log_list


## ログファイルの整理
def arrange_log_list(log_list) : 
    server_adress_diclist, subnet_diclist = {}, {}
    
    for log in log_list : 
        date, server_adress, response = log  
        
        ### subnetの取得
        subnet = ".".join(server_adress.split(".")[:3])

        ### dateを文字列から日付情報へ変換
        date = date[:4] + "-" + date[4:6] + "-" + date[6:8] + " " + date[8:10] + ":" + date[10:12] + ":" + date[12:]
        date = dt.strptime(date, "%Y-%m-%d %H:%M:%S")
        
        ### server_adressをkeyとした辞書型リストの作成
        if server_adress_diclist.setdefault(server_adress) == None : 
            server_adress_diclist[server_adress] = [[date, response]]
        else : 
            server_adress_diclist[server_adress].append([date, response])

        ### subnetをkeyとした辞書型リストの作成   
        if subnet_diclist.setdefault(subnet) == None : 
            subnet_diclist[subnet] = [[date, response]]
        else : 
            subnet_diclist[subnet].append([date, response])

    ## 整理されたリストの確認            
    # for key in server_adress_diclist : 
    #     print(key)
    #     for adress in server_adress_diclist[key] : 
    #         print(*adress)
    #     print("----")

    # for key in subnet_diclist : 
    #     print(key)
    #     for adress in subnet_diclist[key] : 
    #         print(*adress)
    #     print("----")

    
    return [server_adress_diclist, subnet_diclist]
    
    
## 過負荷の判定
def deal_overload(adress_type, output_type, adress_diclist) : 
    overload_diclist = {}
    for adress in adress_diclist : 
        overload_flag = False # 過負荷になっているかのフラグ
        overload_list = [] # 過負荷の一時リストの初期化

        processing_count = 0 # 何個目のqueryを処理しているか

        ### adress の query listを取り出す
        query_list = adress_diclist[adress]
        for date, response in query_list : 
            processing_count += 1

            #### relate to overload
            if processing_count >= overload_judge_threshold : 
                if overload_flag == True : 
                    overload_flag = calculate_average_ping(query_list, processing_count)
                    if overload_flag == False : 
                        overload_end = date
                        overload_list.append([overload_start, overload_end])
                else : 
                    overload_flag = calculate_average_ping(query_list, processing_count)
                    overload_start = date
                    
        overload_diclist[adress] = overload_list
    show_the_term(adress_type, output_type, overload_diclist)


## 故障の判定
def deal_failure(adress_type, output_type, adress_diclist) : 
    failure_diclist = {}
    for adress in adress_diclist : 
        failure_flag = False # 故障になっているかのフラグ
        failure_list = [] # 故障の一時リストの初期化

        timeout_count = 0 # タイムアウトが連続何個目か

        ### adress の query listを取り出す
        query_list = adress_diclist[adress]
        for date, response in query_list : 

            #### relate to failure
            if response == "-" : 
                timeout_count += 1
                if timeout_count == 1 : 
                    failure_start = date
                    
                if failure_flag : 
                    pass
                else : 
                    if timeout_count >= timeout_bound : 
                        failure_flag = True
                    else : 
                        pass
            else : 
                timeout_count = 0
                if failure_flag : 
                    failure_end = date
                    failure_flag = False
                    failure_list.append([failure_start, failure_end])
                else : 
                    pass

        failure_diclist[adress] = failure_list
    show_the_term(adress_type, output_type, failure_diclist)


## 平均のpingの計算
def calculate_average_ping(query_list, processing_count) : 
    overload_flag = False
    valid_count = 0
    sum_val = 0
    for date, response in query_list[processing_count-overload_judge_threshold:processing_count] : 
        if response != "-" : 
            sum_val += int(response)
            valid_count += 1
    ### すべてのreponseが"-"のとき
    if valid_count == 0 : 
        pass

    elif sum_val/valid_count >= overload_bound : 
        overload_flag = True
    #     print(sum_val/valid_count)
    #     print(date)
    # print("---")
    
    return overload_flag


## 故障，過負荷期間の出力
def show_the_term(adress_type, output_type, tmp_diclist) : 
    if output_type == "failure" : 
        print("---------------------------")
        print("FAILURE TERM")
        print("---------------------------")
    elif output_type == "overload" : 
        print("---------------------------")
        print("OVERLOAD TERM")
        print("---------------------------")
        
    if adress_type == "server adress" : 
        adress = "server adress"
    elif adress_type == "subnet" : 
        adress = "subnet"
    
    for key in tmp_diclist : 
        print(adress+":", key)
        for start, end in tmp_diclist[key] : 
            print(start, end)
#--------------------------------------#


########################################
# main
def main() : 
    log_list = input_log()
    server_adress_diclist, subnet_diclist = arrange_log_list(log_list)
    if adress_type == "server adress" : 
        if output_type == "overload" : 
            deal_overload(adress_type, output_type, server_adress_diclist)
        elif output_type == "failure" : 
            deal_failure(adress_type, output_type, server_adress_diclist)
        else : 
            print("output type error!")
    elif adress_type == "subnet" : 
        if output_type == "overload" : 
            deal_overload(adress_type, output_type, subnet_diclist)
        elif output_type == "failure" : 
            deal_failure(adress_type, output_type, subnet_diclist)
        else : 
            print("output type error!")
    else : 
        print("adress type error!")
#--------------------------------------#
    

########################################
# introduction
if __name__ == "__main__" : 
    main()
#--------------------------------------#
