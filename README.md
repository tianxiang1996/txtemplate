#### 介绍

一个通过txt模板和Excel表格生成txt文件的小工具，可以用来生成网络设备配置脚本等
内置了一个IP地址计算的Jinja2插件，可以通过{% ip address , "+1" %}格式进行IP地址计算

#### 依赖库

- python3
- pandas >= 1.5.0
- Jinja2 >= 3.1.2
- openpyxl >= 3.0.10
- ~~IPy >= 1.1~~

#### 使用说明

> python xlsx2txt.py [-h] [-r | -x XLSX | -v] [-t TEMPLATE] [-p PREFIX | -a]

| 可选参数                         | 说明                                                                                                                                                                           |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| -h, --help                       | 查看帮助                                                                                                                                                                       |
| -r, --request                    | 进入交互模式                                                                                                                                                                   |
| -x XLSX, --xlsx XLSX             | XLSX文件名称，表格中每一列为一个变量，第一行为变量名称                                                                                                                         |
| -v, --version                    | 查看当前版本                                                                                                                                                                   |
| -t TEMPLATE, --template TEMPLATE | 模板文件名称默认为temp.txt，在模板中通过{{ 变量名称 }}定义变量，更多使用方法请参考jinja2模板语法，具体可参考：[模板设计者文档](http://docs.jinkan.org/docs/jinja2/templates.html) |
| -p PREFIX, --prefix PREFIX       | Prefix默认为XLSX文件第1列的值，输入值应为变量名称，该参数作为生成文件的文件名前缀，请确保前缀中不包含无法作为文件名的字符                                                      |
| -a, --add                        | 追加写入，模板内容会被写入同一个文件内                                                                                                                                         |

#### IP地址计算插件说明

该插件用于在jinja2模板中对IP地址进行计算，模板格式{% ip ***address***, ***argv*** %}

- argv为"+1"或者"-1"返回address+1或者-1，可以为任意数值
- - 例1：{% ip "192.168.1.1" , "+1" %}会返回192.168.1.2
  - 例2：{% ip "192.168.1.1" , "-1" %}会返回192.168.1.0
- argv为"netmask_24"或者"netmask_255.255.255.0"返回网络号
  - 例1：{% ip "192.168.1.1" , "netmask_24" %}会返回192.168.1.0
  - 例2：{% ip "192.168.1.1" , "netmask_255.255.255.0" %}会返回192.168.1.0
- argv为1-32的数值或者"255.255.255.0"掩码格式时，返回地址和掩码
  - 例1：{% ip "192.168.1.1" , 24 %}会返回192.168.1.1 255.255.255.0
  - 例2：{% ip "192.168.1.1" , "255.255.255.0" %}会返回192.168.1.1 24
- 无argv或argv为其他值直接返回address
  - 例：{% ip "192.168.1.1" %}会返回192.168.1.1
- 格式错误返回IPERROR或NETMASKERROR
  - 地址格式错误时返回IPERROR
  - 掩码格式错误时返回NETMASKERROR

#### 示例

正常情况下，工具会读取Excel表格的数据，逐行根据模板生成文件，本次示例使用的模板名称为temp.txt，表格名称为ip.xlsx

内容如下：

**ip.xlsx**

| 设备名及标签 | 带外IP       | 带外网关       | 接口IP       | 位置 |
| ------------ | ------------ | -------------- | ------------ | ---- |
| SW1          | 192.168.10.1 | 192.168.10.254 | 172.16.31.1  | 东   |
| SW2          | 192.168.10.2 | 192.168.10.254 | 172.16.31.5  | 东   |
| SW3          | 192.168.10.3 | 192.168.10.254 | 172.16.31.9  | 东   |
| SW4          | 192.168.10.4 | 192.168.10.254 | 172.16.31.13 | 西   |
| SW5          | 192.168.10.5 | 192.168.10.254 | 172.16.31.17 | 西   |
| SW6          | 192.168.10.6 | 192.168.10.254 | 172.16.31.21 | 西   |

**temp.txt**

```
#
 sysname {{设备名及标签}}
#
interface M-GigabitEthernet0/0/0
 description MGT
 ip address {{带外IP}} 255.255.255.0
#
interface GigabitEthernet1/0/1
 port link-mode route
 ip address {{接口IP}} 255.255.255.0
#
 ip route-static 0.0.0.0 0 {{带外网关}} description OB
 ip route-static 10.0.0.0 8 {% ip 接口IP , "+1" %} description OB
#
{% if 位置 == '东' %}
 info-center loghost 192.168.1.1
 info-center loghost 192.168.1.2
{% else %}
 info-center loghost 172.16.1.1
 info-center loghost 172.16.1.2
{% endif %}
```

使用命令生成配置，成的文件会在output目录下

`python xlsx2txt.py -x ip.xlsx -t temp.txt `

```
>tree output
output
├── SW1_line2.txt
├── SW2_line3.txt
├── SW3_line4.txt
├── SW4_line5.txt
├── SW5_line6.txt
└── SW6_line7.txt
```

```
>cat output/SW1_line2.txt
#
 sysname SW1
#
interface M-GigabitEthernet0/0/0
 description MGT
 ip address 192.168.10.1 255.255.255.0
#
interface GigabitEthernet1/0/1
 port link-mode route
 ip address 172.16.31.1 255.255.255.0
#
 ip route-static 0.0.0.0 0 192.168.10.254 description OB
 ip route-static 10.0.0.0 8 172.16.31.2 description OB
#
 info-center loghost 192.168.1.1
 info-center loghost 192.168.1.2
```

##### 文件前缀

默认情况下使用Excel文件的第一列作为文件名，但是某些字符串可能无法作为文件名使用，此时可以使用prefix选项指定列作为文件名

`python xlsx2txt.py -x ip.xlsx -t temp.txt -p "带外IP" `

```
>tree output
output
├── 192.168.10.1_line2.txt
├── 192.168.10.2_line3.txt
├── 192.168.10.3_line4.txt
├── 192.168.10.4_line5.txt
├── 192.168.10.5_line6.txt
└── 192.168.10.6_line7.txt
```

##### 输出到单个文件

使用追加写入时，根据模板生成的所有数据会循环写入一个output.txt文件中，使用方式如下

temp.txt文件内容为

```
network {% ip 接口IP , "netmask_30" %} 0.0.0.3
```

`python xlsx2txt.py -x ip.xlsx -t temp.txt -a `

```
>cat output/output.txt
network 172.16.31.0 0.0.0.3
network 172.16.31.4 0.0.0.3
network 172.16.31.8 0.0.0.3
network 172.16.31.12 0.0.0.3
network 172.16.31.16 0.0.0.3
network 172.16.31.20 0.0.0.3
```

##### 循环

有时在处理网络设备接口配置时，需要对多个接口输出相同的配置，此时可以使用模板的for循环

temp.txt文件内容为

```
{% for i in range(1, 10) %}
#
interface Ten-GigabitEthernet1/0/{{i}}
 port link-mode bridge
 port link-type trunk
 undo port trunk permit vlan 1
 port trunk permit vlan 2 to 4094
 port link-aggregation group {{i}}
{% endfor %}
```

输出效果如下：

```
#
interface Ten-GigabitEthernet1/0/1
 port link-mode bridge
 port link-type trunk
 undo port trunk permit vlan 1
 port trunk permit vlan 2 to 4094
 port link-aggregation group 1
#
interface Ten-GigabitEthernet1/0/2
 port link-mode bridge
 port link-type trunk
 undo port trunk permit vlan 1
 port trunk permit vlan 2 to 4094
 port link-aggregation group 2
#
.....
interface Ten-GigabitEthernet1/0/9
 port link-mode bridge
 port link-type trunk
 undo port trunk permit vlan 1
 port trunk permit vlan 2 to 4094
 port link-aggregation group 9

```
