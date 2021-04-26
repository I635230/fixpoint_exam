# 監視システム

## 使用方法

説明/手動設定にある各パラメータを適切に設定し，入力データを渡すことで出力が得られる．

## 説明

### 手動設定

- timeout_bound : 何個連続でタイムアウトしたときに故障と判定するか
- overload_judge_threshold : 何個の平均をとってバウンドを超えていたときに過負荷と判定するか
- overload_bound : 何msを超えたときに過負荷と判定するか
- adress_type : "server adress" or "subnet", どちらについての出力を得たいかで設定
- output_type : "failure" or "overload", どちらについての出力を得たいかで設定

```python
timeout_bound = 1 # 1～
overload_judge_threshold = 3 # 1～
overload_bound = 5 # 0～
adress_type = "server adress" # server adress, subnet
output_type = "overload" # failure, overload
```



### 大まかな流れ

- 監視ログファイルの読み込み
- 監視ログファイルをサーバーアドレス，サブネットごとに整理
- 整理したファイルに対して，故障と過負荷状態についての判定を行う

```python
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
```



### 入力

＜確認日時＞,＜サーバアドレス＞,＜応答結果＞という入力データが複数行与えられるので，カンマ区切りでリスト化し，log_listという名称でmain関数にreturnする．

```python
def input_log() : 
    log_list = []
    log_append = log_list.append
    while(True) : 
        try : 
            log_append(input().split(","))
        except EOFError : 
            break
    return log_list
```



### 入力ファイルの整理

date, server_adress, response = ＜確認日時＞,＜サーバアドレス＞,＜応答結果＞と代入し，datetimeモジュールを用いてdateを文字列から日付情報へ変換．

また，server_adress, subnetをそれぞれkeyとした辞書型リストを作成．

```python
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
            server_adress_diclist[server_adress] = []
        else : 
            server_adress_diclist[server_adress].append([date, response])

        ### subnetをkeyとした辞書型リストの作成   
        if subnet_diclist.setdefault(subnet) == None : 
            subnet_diclist[subnet] = []
        else : 
            subnet_diclist[subnet].append([date, response])

    ## 整理されたリストの確認            
    # for key in server_adress_diclist : 
    #     print(key)
    #     for server_adress in server_adress_diclist[key] : 
    #         print(*server_adress)
    #     print("----")
    
    return [server_adress_diclist, subnet_diclist]
```



### 故障判定

adress_type = "server_adress" or "subnet"
output_type = "failure" or "overload"
adress_diclist = server_adress_diclist or subnet_diclist

アドレス毎に故障の一時リストを空で作成し，条件を満たしたときにその中に[failure_start, failure_end]を追加していく．

そのアドレスのquery_listを取り出し，responseが連続で"-"の場合はresponse_countを増加させていく．それがtimeout_boundを超えたとき，failure_startにそのときの日付を代入．また，その状態でresponseが"-"でなくなったらfailure_endにその日付を代入し，一時リストに[failure_start, failure_end]を追加する．

最後にアドレス毎にfailure_diclistに一時リストを代入し，show_the_termで期間を表示．

```python
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
                if failure_flag : 
                    pass
                else : 
                    if timeout_count >= timeout_bound : 
                        failure_start = date
                        failure_flag = True
                    else : 
                        pass
            else : 
                if failure_flag : 
                    failure_end = date
                    failure_flag = False
                    failure_list.append([failure_start, failure_end])
                    timeout_count = 0
                else : 
                    pass
            
        failure_diclist[adress] = failure_list
    show_the_term(adress_type, output_type, failure_diclist)
```



### 過負荷判定

アドレス毎に過負荷の一時リストを空で作成し，条件を満たしたときにその中に[overload_start, overload_end]を追加していく．

何個目のqueryを処理しているかを表すprocessing_countがoverload_judge_thresholdを超えてからoverloadかどうかの判定をはじめる．

直近のoverload_judge_threshold個のresponse(ping値)を確認し，平均値をとったときにoverload_boundを超えていたら過負荷と判定し，overload_startに日付を代入する．※ただし，rsponseが"-"のときは，それ以外の残りのresponseの平均値を計算する．すべてのresponseが"-"のときは過負荷とは判定しない．

また，その状態でresponseの平均値がoverload_boundを下回ったら，overload_endにそのときの日付を代入し，一時リストに[overload_start, overload_end]を追加する．

最後にアドレス毎にoverload_diclistに一時リストを代入し，show_the_termで期間を表示．

```python
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
```



### 平均のpingの計算

responseが"-"でない有効なカウントvalid_countを数えて，合計値sumval/valid_countがoverload_boundが超えていれば過負荷と判定．※ただし，すべてのresponseが"-"のときは，過負荷でないと判定する．(この辺りの細かい仕様が特にどうして良いかわからなかった)

```python
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
    
    return overload_flag
```



### 出力

adress_type, output_typeに応じて出力．

```python
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
```



## テストについて

各設問とinput, outputが対応しています．例えば，設問1ならinput_1を使用してoutput_1を得ています．

以下は各inputに対して最初の手動設定の部分をどのようにおいたかです．

### input_1

```python
timeout_bound = 1 # 1～
adress_type = "server adress" # server adress, subnet
output_type = "failure" # failure, overload
```

### input_2

```python
timeout_bound = 2 # 1～
adress_type = "server adress" # server adress, subnet
output_type = "failure" # failure, overload
```

### input_3

```python
overload_judge_threshold = 3 # 1～
overload_bound = 5 # 0～
adress_type = "server adress" # server adress, subnet
output_type = "overload" # failure, overload
```


### input_4

```python
timeout_bound = 2 # 1～
adress_type = "subnet" # server adress, subnet
output_type = "failure" # failure, overload
```
