def Mapping
    xlsx = xlrd.open_workbook(filename_ydata)  # read the file
        temp_array = []
        before_datetime = None
        for sh in xlsx.sheets():  # Traversing data to save to an array
            for r in range(sh.nrows):
                temp_data = sh.row_values(r)
                try:
                    # Convert time to datetime format
                    temp_data[ARRAYID['pubdate']] = xlrd.xldate.xldate_as_datetime(temp_data[ARRAYID['pubdate']], 0)
                    before_datetime = temp_data[ARRAYID['pubdate']]


if i < len(ydata):
    now_date = ydata[i][ARRAYID['pubdate']]
    # Determine if it is a time type
if isinstance(now_date, datetime.datetime):
    # print(i,now_date)
    if first_date is None:  # First time assignment
        temp_date = str(now_date.year) + "-" + str(now_date.month) + "-" + str(now_date.day)
        first_date = datetime.datetime.strptime(temp_date, "%Y-%m-%d")
        second_date = datetime.datetime.strptime(temp_date, "%Y-%m-%d") + dt
        # print(first_date, second_date)
    # Determine time range
    if i < len(ydata) and first_date <= now_date <= second_date:
        type = ydata[i][coolid]
        if type == '':
            type = "匿名"
        data_num_dict[type] += 1
        data_id_dict[type].append(ydata[i][ARRAYID['docid']])
    else:
        temp_num = []
        temp_id = []
        for one in data_list:
            temp_num.append(data_num_dict[one])  # Guarantee order
            temp_id.append(data_id_dict[one])
        time_data_list.append(temp_num)
        time_id_list.append(temp_id)
        day_list.append(str(second_date)[0:4] + str(second_date)[5:7] + str(second_date)[8:10])
        # Init the dict of data numbers。
        data_num_dict = {}
        data_id_dict = {}
        for each in data_list:
            data_num_dict[each] = 0
            data_id_dict[each] = []
        first_date = second_date
        second_date = second_date + dt
        # print(second_date, "--------", dt)
        if i < len(ydata) and first_date <= now_date <= second_date:
            i -= 1

return day_list, time_data_list, time_id_list

Customized.dataSaveTocsv(headers, values, folderpath + os.sep + onekey + CUS_CSVFILENAME)