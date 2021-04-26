########################################
# setting
timeout_bound = 1
overload_judge_threshold = 3
overload_bound = 5
#--------------------------------------#


########################################
# import
from datetime import datetime as dt
#--------------------------------------#


########################################
# input
def input_log() : 
    log_list = []
    log_append = log_list.append
    while(True) : 
        try : 
            log_append(input().split(","))
        except EOFError : 
            break
    return log_list
#--------------------------------------#


########################################
# preliminary
def arrange_log_list(log_list) : 
    server_adress_diclist = {}
    subnet_diclist = {}
    
    for log in log_list : 
        date, server_adress, response_time = log  
        subnet = ".".join(server_adress.split(".")[:3])
        date = date[:4] + "-" + date[4:6] + "-" + date[6:8] + " " + date[8:10] + ":" + date[10:12] + ":" + date[12:]
        date = dt.strptime(date, "%Y-%m-%d %H:%M:%S")
        if server_adress_diclist.setdefault(server_adress) == None : 
            server_adress_diclist[server_adress] = []
        else : 
            server_adress_diclist[server_adress].append([date, response_time])
            
        if subnet_diclist.setdefault(subnet) == None : 
            subnet_diclist[subnet] = []
        else : 
            subnet_diclist[subnet].append([date, response_time])

    # confirm            
    # for key in server_adress_diclist : 
    #     print(key)
    #     for server_adress in server_adress_diclist[key] : 
    #         print(*server_adress)
    #     print("----")
    
    return [server_adress_diclist, subnet_diclist]
    
def deal_server(adress_type, server_adress_diclist) : 
    failure_diclist = {}
    overload_diclist = {}
    for server_name in server_adress_diclist : 
        failure_flag = False
        overload_flag = False
        timeout_count = 0
        processing_count = 0
        failure_list = []
        overload_list = []
        
        ### sever name の query listを取り出す
        server_query_list = server_adress_diclist[server_name]
        for date, response in server_query_list : 
            processing_count += 1

            #### relate to overload
            if processing_count >= overload_judge_threshold : 
                if overload_flag == True : 
                    overload_flag = calculate_average_ping(server_query_list, processing_count)
                    if overload_flag == False : 
                        overload_end = date
                        overload_list.append([overload_start, overload_end])
                else : 
                    overload_flag = calculate_average_ping(server_query_list, processing_count)
                    overload_start = date
            
            #### relate to timeout
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
        
        failure_diclist[server_name] = failure_list
        overload_diclist[server_name] = overload_list
    show_the_term(adress_type, "failure", failure_diclist)
    show_the_term(adress_type, "overload", overload_diclist)

def calculate_average_ping(server_query_list, processing_count) : 
    overload_flag = False
    valid_count = 0
    sum_val = 0
    for date, response in server_query_list[processing_count-overload_judge_threshold:processing_count] : 
        if response != "-" : 
            sum_val += int(response)
            valid_count += 1
    if sum_val/valid_count >= overload_bound : 
        overload_flag = True
    #     print(sum_val/valid_count)
    #     print(date)
    # print("---")
    
    return overload_flag


def show_the_term(adress_type, condition, tmp_diclist) : 
    if condition == "failure" : 
        print("---------------------------")
        print("server failure term")
    elif condition == "overload" : 
        print("---------------------------")
        print("server overload term")
        
    if adress_type == "server adress" : 
        name = "server name"
    elif adress_type == "subnet" : 
        name = "subet"
    
    for key in tmp_diclist : 
        print(name+":", key)
        for start, end in tmp_diclist[key] : 
            print(start, end)

#--------------------------------------#


########################################
# definition
def main() : 
    log_list = input_log()
    server_adress_diclist, subnet_diclist = arrange_log_list(log_list)
    # deal_server("server adress", server_adress_diclist)
    deal_server("subnet", subnet_diclist)

#--------------------------------------#
    

########################################
# main
if __name__ == "__main__" : 
    main()
#--------------------------------------#
