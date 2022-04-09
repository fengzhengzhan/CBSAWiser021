import datetime
import os
import xlrd
import csv

KEY_TIME_INTERVAL = 1


def xlsx_to_csv(filename):
    workbook = xlrd.open_workbook(filename)
    table = workbook.sheet_by_index(0)
    with open(filename + ".csv", "w", newline='', encoding='utf-8_sig') as fp:
        write = csv.writer(fp)
        for row_num in range(table.nrows):
            row_value = table.row_values(row_num)
            write.writerow(row_value)


def selectsort(content):
    for i in range(0, len(content)):
        minIdx = i
        for j in range(i + 1, len(content)):
            if content[j][0] < content[minIdx][0]:
                minIdx = j
        content[i], content[minIdx] = content[minIdx], content[i]
    return content


def Mapping():
    filename = "departure_total.xlsx"

def Mapping(filename):
    # 判断后缀，并将excel转换为csv
    if os.path.splitext(filename)[-1] == ".xlsx" or os.path.splitext(filename)[-1] == ".xls":
        xlsx_to_csv(filename)
        filename = filename + ".csv"
    # 读取csv文件
    csv_reader = csv.reader(open(filename))
    # 将文件保存成[datetime格式时间, y数据]的样式
    content = []
    # 参数根据给定数据集灵活调整
    for line in csv_reader:
        try:
            temp_date = str(int(float(line[0]))) + "-" + str(int(float(line[1]))) + "-" + str(int(float(line[2])))
            content.append([datetime.datetime.strptime(temp_date, "%Y-%m-%d"), float(line[3])])
        except Exception as e:
            pass

    # 根据时间排序 为了方便理解使用选择排序法
    content = selectsort(content)
    # print(content)

    first_date = None
    second_date = None
    dt = datetime.timedelta(days=KEY_TIME_INTERVAL)
    day_list = []
    y_data = []
    nums = 0
    idx = -1
    while idx < len(content) + 1:  # Leave one left
        idx += 1
        # Time analysis
        if idx < len(content):
            now_date = content[idx][0]
        # Determine if it is a time type
        if isinstance(now_date, datetime.datetime):
            # print(idx,now_date)
            if first_date is None:  # First time assignment
                temp_date = str(now_date.year) + "-" + str(now_date.month) + "-" + str(now_date.day)
                first_date = datetime.datetime.strptime(temp_date, "%Y-%m-%d")
                second_date = datetime.datetime.strptime(temp_date, "%Y-%m-%d") + dt
                # print(first_date, second_date)
            # Determine time range
            if idx < len(content) and first_date <= now_date < second_date:
                nums += content[idx][1]
            else:
                day_list.append(str(second_date)[0:4] + str(second_date)[5:7] + str(second_date)[8:10])
                y_data.append(nums)

                # Init the dict of data numbers.
                nums = 0
                first_date = second_date
                second_date = second_date + dt
                # print(second_date, "--------", dt)
                if idx < len(content) and first_date <= now_date <= second_date:
                    idx -= 1

    print(len(day_list), len(y_data))
    return day_list, y_data

if __name__ == "__main__":
    filename = "arrival_total2.xlsx"
    day_list, y_data = Mapping(filename)
    print(day_list)
    print(y_data)