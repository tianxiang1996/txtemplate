#### 介绍

一个通过txt模板和Excel表格生成txt文件的小工具
可以用来生成网络设备配置脚本等

#### 依赖库

**使用本工具需要**

- python3
- pandas >= 1.5.0
- Jinja2 >= 3.1.2
- openpyxl >= 3.0.10
- IPy >= 1.1

#### 使用说明

> python xlsx2txt.py [-h] [-r | -x XLSX | -v] [-t TEMPLATE] [-p PREFIX | -a]

 **可选参数**

| col1       | col2     | col3 |
| ---------- | -------- | ---- |
| -h, --help | 查看帮助 |      |
|            |          |      |

<table>
<tr><td>-h, --help</td><td>查看帮助</td></tr>
<tr><td>-r, --request</td><td>进入交互模式</td></tr>
<tr><td>-x XLSX, --xlsx XLSX</td><td>XLSX文件名称，表格中每一列为一个变量，第一行为变量名称</td></tr>
<tr><td>-v, --version</td><td>查看当前版本</td></tr>
<tr><td>-t TEMPLATE, --template TEMPLATE</td><td>模板文件名称默认为temp.txt，在模板中通过{{ 变量名称 }}定义变量，更多使用方法请参考jinja2模板语法</td></tr>
<tr><td>-p PREFIX, --prefix PREFIX</td><td>Prefix默认为XLSX文件第1列的值，输入值应为变量名称，该参数作为生成文件的文件名前缀，请确保前缀中不包含无法作为文件名的字符</td></tr>
<tr><td>-a, --add</td><td>追加写入，模板内容会被写入同一个文件内</td></tr>
</table>

#### 示例

本次示例使用的模板名称为temp.txt，表格名称为ip.xlsx

内容如下：

ip.xlsx

| 设备名及标签 | 带外IP       | 带外网关       | 接口IP       | 位置 |
| ------------ | ------------ | -------------- | ------------ | ---- |
| SW1          | 192.168.10.1 | 192.168.10.254 | 172.16.31.1  | 东   |
| SW2          | 192.168.10.2 | 192.168.10.254 | 172.16.31.5  | 东   |
| SW3          | 192.168.10.3 | 192.168.10.254 | 172.16.31.9  | 东   |
| SW4          | 192.168.10.4 | 192.168.10.254 | 172.16.31.13 | 西   |
| SW5          | 192.168.10.5 | 192.168.10.254 | 172.16.31.17 | 西   |
| SW6          | 192.168.10.6 | 192.168.10.254 | 172.16.31.21 | 西   |

```
#temp.txt
 sysname {{设备名及标签}}
#  
 ip vpn-instance MGT
#
interface M-GigabitEthernet0/0/0
 description MGT
 ip binding vpn-instance OOB
 ip address {{带外IP}} 255.255.255.0
#
interface GigabitEthernet1/0/1
 port link-mode route
 ip address {{接口IP}} 255.255.255.0
#
 ip route-static vpn-instance MGT 0.0.0.0 0 {{带外网关}} description OB
 ip route-static 10.0.0.0 8 {% ip 接口IP , "+1" %} description OB
#
{% if 位置 == '东' %}
 info-center loghost vpn-instance MGT 192.168.1.1
 info-center loghost vpn-instance MGT 192.168.1.2
{% else %}
 info-center loghost vpn-instance MGT 172.16.1.1
 info-center loghost vpn-instance MGT 172.16.1.2
{% endif %}
```
