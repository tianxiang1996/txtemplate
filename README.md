#### 介绍

一个通过txt模板和Excel表格生成txt文件的小工具  
可以用来生成网络设备配置脚本等


#### 使用说明

python xlsx2txt_v2215.py [-h] [-r | -x XLSX | -v] [-t TEMPLATE] [-p PREFIX | -a]

 **可选参数:** 
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

