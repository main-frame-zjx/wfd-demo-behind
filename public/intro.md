# 使用文档

该文档介绍如何使用该GPU数据流可视化项目

## 1.GPU数据流可视化操作流程

### 操作步骤

- Step1：注册、登录
- Step2：上传代码文件
- Step3：选择dump数据（.model_vec数据）
- Step4：生成结构图
- Step5：动态播放
- Step6：保存工作区

### Step1 注册登录

点击左侧工具栏**账户操作**，完成注册和登录。注册的账户**需要管理员审批通过**后才能够登录。

登录后才能够正常使用项目功能

<img src=".\images\step1.png" style="zoom: 67%;" />

### Step2 上传代码文件

点击左侧工具栏 **上传代码文件**->**上传代码文件**

把所有用于分析GPU结构的代码放到一个**文件夹**中，然后选中该文件夹上传

等待上传并解析代码文件，直到提示**“代码文件上传解析成功！”**

<img src=".\images\step2.png" style="zoom: 67%;" />



### Step3 选择dump数据（.model_vec数据）

如果是第一次使用该项目（即以前并未上传过dump数据），需要先上传数据到服务器。

点击左侧工具栏 **管理dump数据集**->**上传dump数据集**。所有需要分析的GPU运行时产生的 **.model_vec** 文件放到一个**文件夹**中，然后选中该文件夹上传。推荐1次上传的数据**不要超过20GB**。如果数据量太大，可以分多次上传。

<img src=".\images\step3_1.png" style="zoom: 67%;" />

数据上传成功后，会提示直到提示**“数据文件上传解析成功！”**

然后可以选择对应的dump数据集进行本次GPU数据流可视化。点击左侧工具栏 **管理dump数据集**->**下载dump数据集**，会看到如下图所示的表格，选择需要可视化的数据集，点击**使用该数据**。

<img src=".\images\step3_3.png" style="zoom:75%;" />



### Step4 生成结构图

完成Step1~Step3后，点击左侧工具栏 **生成结构图**->**生成结构图**。会以Module为结点，Port为边，得到一个GPU数据流的有向图。

结点的默认排布方式为：均匀排布。建议通过**手动拖拽**得到合适的结点排布。

<img src=".\images\step4.png" style="zoom:75%;" />





### Step5 动态播放

项目会根据解析**.model_vec** 数据得到的**cycle**信息为时间进度条。可以点击下方的**“播放”**按钮来逐帧查看GPU数据流。也可以暂停后，使用左右两个按钮来手动控制cycle的选择。或者直接点击进度条来跳转相应的位置。

图中边的颜色对应port上数据传输的频率（频率 = 在连续N个**cycle**中有数据传输的**cycle**数/N），一般借助可视化得到的结果分析哪些**port**存在堵塞。

项目的效果如下图所示：

<img src=".\images\dataflow1.png" style="zoom:80%;" />





### Step6 保存工作区

如果当前分析的代码需要保存，便于下次继续分析，或者为了保存当前拖拽得到的顶点位置，可以点击左侧工具栏 **工作区**->**管理工作区**，进行上传或者覆盖。将目前正在分析的代码（GPU结构）进行保存。下次登录时可以点击 **工作区**->**加载工作区**->**下载** 来获得上次保存的内容。

<img src=".\images\step6.png" style="zoom:80%;" />

****

## 2.右侧详细信息面板介绍

#### 全局信息面板

唤起方式：点击画布的空白处

<img src=".\images\global_detail.png" style="zoom:80%;" />

**速率窗口大小**：计算port数据传输频率的参数N，数据传输的频率 = 在连续N个**cycle**中有数据传输的**cycle**数/N）

**播放步长**：动态播放时，每1帧增加的cycle

**帧率上限**：动态播放时的最大帧率

**dpc_id**：当前流程图中数据对应的**dpc**序号，范围为0~3。对应的是代码中**宏定义#define MAX_DPC_NUM**的值，目前只支持**MAX_DPC_NUM=4**的情况

**显示合并后的边**：勾选后，不再区分不同**dpc**的数据，统一进行计算。

**显示有效数据**：勾选后，会考虑**.model_vec**文件中的**send**信号和**valid**信号，如果数据为“0”则不计入**port**的传输频率计算。例如以下文件中的第一位信号是send信号。

```txt
class xgfss_dsd_gsd_draw 
send [1]
clken [1]
free [1]
op [2]
data [127]
head [1]
tail [1]
endclass 

1 1 0 0 00000000_088e8417_f0000000_00010000 0 0 @ 0000008074
1 1 0 0 00000000_088e8417_f0000000_00030002 0 0 @ 0000008075
```

****

#### Module信息面板

唤起方式：点击结点

<img src=".\images\module_detail.png" style="zoom:80%;" />

**名称**：当前结点在代码中对应module的变量

**相关信息**：暂时无内容，等待后续开发

****

#### Port信息面板

唤起方式：点击边

<img src=".\images\port_detail.png" style="zoom:80%;" />

**Port变量名**：当前边在代码中对应port的变量

**文件名**：解析代码后，得到的当前port对应的dump数据文件

**传输速率**：当前cycle到后续N个cycle统计得到的port上数据传输频率



****

## 3.代码文件格式要求

**文件名**：以.cpp .c .h 为后缀

本项目使用**正则表达式**解析项目中存在的module和port。

建议将需要解析的代码文件拷贝到单独的文件夹，然后按照以下格式要求进行修改：

##### ①module和port数组的声明要直接使用数字，而不是变量

推荐对**MAX_DPC_NUM**这一宏变量进行全局替换，要求所有的port变量的变量名以`_port`结尾

```C++
//正确声明module
CGfdBlock *pGfdBlock;
CGfdBlock *gia_module[4];
CGfdBlock *vsd_module[4];

//正确声明port
Port *GFD_GIA_draw_cmd_port[4] = {nullptr};
Port *GIA_GFD_drawdone_port[4];
Port *CE_XGF_draw_cmd_port = nullptr;

//错误声明module
CGfdBlock *gia_module[MAX_DPC_NUM];
CGfdBlock *vsd_module[3*2];

//错误声明port
Port *GFD_GIA_draw_cmd[4] = {nullptr}; //没有以_port结尾
Port *GFD_GIA_draw_cmd_port[MAX_DPC_NUM] = {nullptr};
Port *GIA_GFD_drawdone_port[3*2];
```



****

##### ②Module的类型声明为CxxxBlock，Port的类型声明为Port，要求为指针类型 

以下给出**Module**和**Port**识别的正则表达式，程序会识别代码中的`CxxxBlock *xxxxxx[]`和`CxxxBlock *xxxxxx`作为**Module**，识别代码中的`Port *xxxx[]`和`Port *xxxx`作为**Port**

```javascript
// Module识别1.正则表达式用于寻找所有形如 CxxxBlock *xxxxxx[]; 的代码
const multiModuleRegex = /(C\w*?Block)\s*\*\s*(\w+)\[(\d+)\];/g;
// Module识别2.正则表达式用于寻找所有形如 CxxxxBlock *xxxx; 的代码
const singleModuleRegex = /(C\w*?Block)\s*\*\s*(\w+)\s*;/g;

// Port识别1.正则表达式用于寻找所有形如 Port *xxxx[4]; 的代码
const multiModuleRegex = /Port\s*\*\s*(\w+)\[(\d+)\];/g;
// Port识别2.正则表达式用于寻找所有形如 Port *xxxx; 的代码
const singleModuleRegex = /Port\s*\*\s*(\w+)\s*;/g;
```



****

##### ③可以使用简单的for循环，但不能有多重for嵌套

项目的解析代码会将简单的for循环（for起点和终点作为常数直接写在代码中）直接展开，但**无法解析多重for嵌套**。

```cmd
#可以被解析的for循环
for (int i = 0; i < 4; i++)
{
    Xgf_ptr_obj.GFD_GIA_draw_cmd_port[i] = new Port(128, "dpc" + to_string(i) + "_gfd_gia_draw_cmd.model_vec");
    Xgf_ptr_obj.DSD_GSD_draw_port[i] = new Port(128, "dpc" + to_string(i) + "_dsd_gsd_draw.model_vec");
}
for (int i = 0; i < 4; i++)
{
    ptr_obj->pGfdBlock->ConnectPort(ptr_obj->GFD_GIA_draw_cmd_port[i],
    ptr_obj->pGfdBlock->GFD_GFP_draw_cmd_Tx[i],
    ptr_obj->gia_module[i]->GFD_GFP_draw_cmd_Rx);
}

#无法解析的for循环
for (int i = 0; i < MAX_DPC_NUM; i++)
{
    Xgf_ptr_obj.GFD_GIA_draw_cmd_port[i] = new Port(128, "dpc" + to_string(i) + "_gfd_gia_draw_cmd.model_vec");
    Xgf_ptr_obj.DSD_GSD_draw_port[i] = new Port(128, "dpc" + to_string(i) + "_dsd_gsd_draw.model_vec");
}
```



****

##### ④为每个Port设置对应的.model_vec文件名

```c++
代码格式要求如下：
xxx.Port变量名 = new Port(xxx, "dumpfile_name");

例如：
Xgf_ptr_obj.GFD_GIA_draw_cmd_port[i] = new Port(128, "dpc" + to_string(i) + "_gfd_gia_draw_cmd.model_vec");
Xgf_ptr_obj.DSD_GSD_draw_port[i] = new Port(128, "dpc" + to_string(i) + "_dsd_gsd_draw.model_vec");
```

`dumpfile_name`可以是多个简单字符串相加得到，允许使用`to_string(i)`。



****

##### ⑤为每个Port设置连接的Module

```C++
代码格式要求如下：
xxx->ConnectPort(XXXX->Portname,XXXX->Modulename->xxxx_Tx,XXXX->Modulename->xxxx_Rx);

例如：
ptr_obj->pGfdBlock->ConnectPort(ptr_obj->GFD_GIA_draw_cmd_port[i],
    ptr_obj->pGfdBlock->GFD_GFP_draw_cmd_Tx[i],
    ptr_obj->gia_module[i]->GFD_GFP_draw_cmd_Rx);
```

其中`xxxx->`是可以省略的

```C++
//无前缀，也可以正常解析
ConnectPort(GFD_GIA_draw_cmd_port[i], pGfdBlock->GFD_GFP_draw_cmd_Tx[i], gia_module[i]->GFD_GFP_draw_cmd_Rx);
```

以Tx结尾表示对应的module为port的输入端，以Rx结尾表示对应的module为port的输出端。借助此处的信息，port作为边会连接数据流图中的两个module。



****

#### 文件举例

```c++
struct Xgf_ptr_object
{
    CGfdBlock *pGfdBlock;
    CGfdBlock *gia_module[4];
    CGfdBlock *vsd_module[4];
    CGfdBlock *hsd_module[4];
    CGfdBlock *gtf_module[4];
    CGfdBlock *dsd_module[4];
    CGfdBlock *gsd_module[4];
    CGfdBlock *lsd_module[4];
    CGfdBlock *pai_module[4];
    CGfdBlock *gff_module[4];

    Port *GFD_GIA_draw_cmd_port[4] = {nullptr};
    Port *GIA_GFD_drawdone_port[4] = {nullptr};
    Port *CE_XGF_draw_cmd_port = nullptr;

    void xmodel_connect()
    {
        for (int i = 0; i < 4; i++)
        {
            Xgf_ptr_obj.GFD_GIA_draw_cmd_port[i] = new Port(128, "dpc" + to_string(i) + "_gfd_gia_draw_cmd.model_vec");
            Xgf_ptr_obj.DSD_GSD_draw_port[i] = new Port(128, "dpc" + to_string(i) + "_dsd_gsd_draw.model_vec");
        }
        for (int i = 0; i < 4; i++)
        {
            ptr_obj->pGfdBlock->ConnectPort(ptr_obj->GFD_GIA_draw_cmd_port[i],
                                            ptr_obj->pGfdBlock->GFD_GFP_draw_cmd_Tx[i],
                                            ptr_obj->gia_module[i]->GFD_GFP_draw_cmd_Rx);

            ptr_obj->pGfdBlock->ConnectPort(ptr_obj->DSD_GSD_draw_cmd_port[i],
                                            ptr_obj->dsd_module[i]->GFD_GFP_draw_cmd_Tx,
                                            ptr_obj->gsd_module[i]->GFD_GFP_draw_cmd_Rx);
        }
    }
};
```



****

#### 数据大小限制

上传的代码文件，建议小于20MB，程序中并无限制。



****

## 4.model_vec文件格式要求

**文件名**：以.model_vec为后缀

#### **内容格式要求**：

要求以class开头，endclass作为中间分割。中间的信息表示每一个信号的bit数，如果有send信号或者valid信号，则认为代表着数据有效性。

对于后续的每一行具体数据，要求以10进制的方式记录对应的cycle，并位于结尾。

```txt
class 'class_name'
'signal_name' [signal]
、、、
endclass

、、、 、、、 0000011111（每一行数据以cycle值结尾）
```



#### **文件举例**：

```txt
class xgfss_dsd_gsd_draw 
send [1]
clken [1]
free [1]
op [2]
data [127]
head [1]
tail [1]
endclass 

1 1 0 0 00000000_088e8417_f0000000_00010000 0 0 @ 0000008074
1 1 0 0 00000000_088e8417_f0000000_00030002 0 0 @ 0000008075
1 1 0 0 00000000_088e8417_f0000000_00050004 0 0 @ 0000008076
1 1 0 0 00000000_088e8417_f0000000_00070006 0 0 @ 0000008077
1 1 0 0 00000000_088e8417_f0000000_00090008 0 0 @ 0000008078
1 1 0 0 00000000_088e8417_f0000000_000b000a 0 0 @ 0000008079
```

**数据大小限制**：推荐单次上传的所有文件总和**小于10GB**
