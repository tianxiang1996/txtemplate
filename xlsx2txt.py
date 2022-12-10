# -*- coding: utf-8 -*-
'''--------------------------------
Time    :   2022.12.10
Author  :   Tixanxiang.yin
Version :   1.3
Desc    :   通过XLSX生成TXT文件
--------------------------------'''
try:
    import pandas as pd
    import openpyxl, ipaddress
    from jinja2 import nodes, Environment
    from jinja2.ext import Extension
except ModuleNotFoundError:
    print("使用本工具需要：")
    print("\tpandas >= 1.5.0")
    print("\tJinja2 >= 3.1.2")
    print("\topenpyxl >= 3.0.10")
    print("请使用pip安装")
    exit(1)
else:
    import sys, os, argparse

class Jinja2IPyExtension(Extension):
    # 定义该扩展的语句关键字，这里表示模板中的{% ip %}语句会由该扩展处理
    tags = set(['ip'])
    def __init__(self, environment):
        super(Jinja2IPyExtension, self).__init__(environment)

    def parse(self, parser):
        # 这是处理模板中{% ip %}语句的主程序，进入此函数时，即表示{% ip %}标签被找到了
        # 下面的代码会获取当前{% ip %}语句在模板文件中的行号
        lineno = next(parser.stream).lineno
        # 获取{% ip %}语句中的参数，比如我们调用{% ip '192.168.1.1' %}
        # 这里就会返回一个jinja2.nodes.Const类型的对象，值为'192.168.1.1'，并封装为列表
        args = [parser.parse_expression()]
        # 下面的代码可以支持两个参数，参数之间用逗号分隔
        # 这里先检查当前处理流的位置是不是个逗号，是的话就再获取一个参数
        if parser.stream.skip_if('comma'):
            args.append(parser.parse_expression())
        else:
            # 不是的话，就在参数列表最后加个空值对象
            args.append(nodes.Const(None))
        # 返回一个CallBlock类型的节点，并将其之前取得的行号设置在该节点中
        # 初始化CallBlock节点时，传入我们自定义的“_ipy_support”方法的调用，
        return nodes.CallBlock(self.call_method('_ipy_support', args), [], [], []).set_lineno(lineno)
    def _ipy_support(self, ip, argv, caller):
        # 这个自定义的内部函数，包含了本扩展的主要逻辑。
        try:
            rv = ipaddress.ip_address(ip)
        except Exception:
            return 'IPERROR'

        if type(argv) == str:
            if argv.startswith("+") or argv.startswith("-"):
                # 地址计算
                prefix = argv[0]
                num = argv[1:]
                if num.isdigit():
                    # 用eval计算数值的加减，然后对ip数值进行加减
                    result = rv + eval(f"0{prefix}{num}")
                return str(result)
            elif argv.startswith("netmask"):
                # 根据长度或掩码返回掩码或长度
                prefix = argv.split("_")[-1]
                try:
                    result = ipaddress.IPv4Network(f"{rv}/{prefix}", False)
                except Exception:
                    return 'NETMASKERROR'
                else:
                    if "." in prefix: return str(result.prefixlen)
                    else: return str(result.netmask)
            elif argv.isdigit() or "." in argv:
                # 根据长度或掩码返回地址与掩码或地址与长度
                try:
                    result = ipaddress.IPv4Network(f"{rv}/{argv}", False)
                except Exception:
                    return 'VALUEERROR'
                else:
                    if "." in argv: return f"{rv} {result.prefixlen}"
                    else: return f"{rv} {result.netmask}"

        return str(rv)

class xlsx2txt:
    def __init__(self, xlsfile) -> None:
        self.data = pd.ExcelFile(xlsfile)
        self.__xlsx_serialize()

    def __xlsx_serialize(self) -> None:
        self.line = []
        sheet = self.data.parse(sheet_name=0)
        for i in range(len(sheet)):
            row = sheet.iloc[i].to_dict() #逐行序列化
            self.line.append(row)

    def to_txt(self, source:str, prefix:str=None, writemode:str="w") -> None:
        if not os.access("output", os.F_OK): os.mkdir("output")
        os.chdir("output")
        for i in self.line:
            try:
                if prefix: filename = f"{i[prefix]}"
                else: filename = f"{i[list(i.keys())[0]]}"
                if writemode == "a": filename = "output.txt"
                else: filename += f"_line{self.line.index(i)+1}.txt"
                out = open(filename, writemode, encoding='utf8')
            except KeyError:
                print("前缀无效，请重新选择")
                break
            except FileNotFoundError:
                print(f"前缀无效，该名称无法在{sys.platform}平台下创建文件，请重新选择")
                break
            except Exception as e:
                print(type(e))
                print(e)
                break
            else:
                if writemode == "a": print(f"line{self.line.index(i)+1} >> {filename}")
                else: print(filename)
                jinjaenv = Environment(extensions=[Jinja2IPyExtension])
                result = jinjaenv.from_string(source).render(**i).split("\n")
                for line in result:
                    if line: out.write(line + "\n")
                out.close()

def request_mode():
    xlsxfile = input("XLSX文件名称（默认为1.xlsx）：")
    tempfile = input("模板文件名称（默认为temp.txt）：")
    prefix = input("结果文件名称前缀为（请输入表格列名称，不输入默认为第一列）：")
    writemode = input("输入a使用追加写入：")
    if not xlsxfile: xlsxfile = "1.xlsx"
    if not tempfile: tempfile = "temp.txt"
    if writemode != "a": writemode = "w"
    a = xlsx2txt(xlsxfile)
    with open(tempfile, encoding='utf8') as f:
        a.to_txt(f.read(), prefix, writemode=writemode)

def main():
    parser = argparse.ArgumentParser(description="通过XLSX生成TXT文件")
    megroup = parser.add_mutually_exclusive_group()
    megroup.add_argument("-r", "--request", help="进入交互模式", action="store_true")
    megroup.add_argument("-x", "--xlsx", help="XLSX文件名称，表格中每一列为一个变量，第一行为变量名称")
    megroup.add_argument("-v", "--version", help="查看当前版本", action="store_true")
    parser.add_argument("-t", "--template", help="模板文件名称默认为temp.txt，在模板中通过{{ 变量名称 }}定义变量，更多使用方法请参考jinja2模板语法", default="temp.txt")
    megroup2 = parser.add_mutually_exclusive_group()
    megroup2.add_argument("-p", "--prefix", help="Prefix默认为XLSX文件第1列的值，输入值应为变量名称，该参数作为生成文件的文件名前缀，请确保前缀中不包含无法作为文件名的字符")
    megroup2.add_argument("-a", "--add", help="追加写入，模板内容会被写入同一个文件内", action="store_true")
    argv = parser.parse_args()
    try:
        if argv.xlsx:
            a = xlsx2txt(argv.xlsx)
            writemode = "w"
            if argv.add: writemode = "a"
            with open(argv.template, encoding='utf8') as f:
                a.to_txt(f.read(), argv.prefix, writemode=writemode)
        elif argv.request:
            print("XLSX文件未指定，进入交互模式，按Ctrl-C退出")
            request_mode()
        elif argv.version:
            print(__doc__)
        else: parser.print_help()
    except KeyboardInterrupt:
        print("Exit")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
