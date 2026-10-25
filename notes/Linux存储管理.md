---
title: Linux 本地存储管理 · 分区、LVM、文件系统与挂载
subject: 操作系统/Linux
category: 课程笔记
source: 豆包对话 · Linux本地存储管理知识点总结
summary: 以「磁盘—分区—LVM—格式化—挂载—权限与配额—备份」为主线，系统整理 Linux 本地存储管理：MBR 512 字节引导扇区结构与 GPT 对比、fdisk/gdisk/parted 与 mkfs 系列、LVM 全流程（pvcreate、vgcreate、lvcreate、lvextend 加 resize2fs，PE 默认 4MB）、fstab 六字段与 mount -a 验证、fuser 解除占用、df 与 du 分工、八进制与符号两种权限写法及 umask 推算（含 666 减 033 不等于 633 的实测订正）、quota 软硬限额六步配置、tar 与 crontab 定时备份实操。
---

# Linux 本地存储管理 · 分区、LVM、文件系统与挂载

## 一、概述

本文是 Linux 本地存储管理课程的系统笔记。存储管理是 Linux 运维中最成体系的一条操作链：

```
物理磁盘 → 分区（MBR/GPT） → PV → VG → LV → 格式化（mkfs） → 挂载（mount/fstab） → 权限与配额（chmod/quota） → 备份（tar/dd/crontab）
```

笔记覆盖课程的全部模块：磁盘物理结构与设备命名、MBR 与 GPT 分区表、分区与格式化工具、LVM 逻辑卷的创建与扩缩容、文件系统检查与参数调整、手动挂载与开机自动挂载、容量查看命令、权限归属与 umask、磁盘限额 quota，以及围绕磁盘备份的 Shell 脚本实操。原料包含课程讲义与大量自测模拟题，本文按知识逻辑重排，题目只保留有订正价值的典型易错点，其余整理为操作要点。最实用、考试与运维出现频率最高的几条命令是：`lvextend` 后必须接 `resize2fs`、`mount -a` 验证 fstab、`fuser -ck` 解除挂载点占用、`df -Th` 与 `du -sh` 定位空间问题。

## 二、磁盘基础与核心概念

### 2.1 物理结构与性能指标

硬盘的技术指标包括主轴转速、平均寻道时间、数据传输率、高速缓存与单碟容量。物理层面的最小寻址单位是**扇区**（512 B 或 4 KB）；同一盘片上同心的扇区集合构成**磁道**；所有盘片上同一位置的磁道构成**柱面**。

接口方面，常用 SATA、SAS、SCSI，IDE（PATA）已淘汰，虚拟机中常见 Virtio 磁盘。Linux 将磁盘抽象为 `/dev` 下的设备文件：

| 设备类型 | 设备文件名 | 示例 |
|---|---|---|
| SATA / SCSI / U 盘 | `/dev/sd[a-p]` | 第一块盘 `/dev/sda`，其第 2 个分区 `/dev/sda2` |
| IDE 硬盘（旧） | `/dev/hd[a-d]` | 第二块 IDE 硬盘 `/dev/hdb`，其上第 3 个主分区 `/dev/hdb3` |
| 虚拟机 Virtio | `/dev/vd*` | `/dev/vda1` |

分区编号规则独立于盘符：主分区编号 1–4，逻辑分区从 5 开始，因此「第二块 SCSI 盘的第 1 个逻辑分区」写作 `/dev/sdb5`。

### 2.2 文件系统的三大核心数据

文件系统是磁盘上的目录组织方法，解决在存储设备上组织、命名、存储、读取文件的问题。ext 系列文件系统内部有三类核心数据：

- **数据区块（block）**：实际存储文件内容，大文件占用多个 block；
- **inode（索引节点）**：记录文件属性与数据所在 block 的号码，**一个文件对应一个 inode**；
- **超级块（superblock）**：记录整个文件系统的全局信息（inode 与 block 总量、使用量、剩余量、格式）。

超级块描述文件系统整体，inode 描述单个文件，这一区分是填空题高频考点。目录树中进入某个文件系统必须通过**挂载**：挂载点是进入点目录，必须是已存在的目录。

## 三、磁盘分区：MBR 与 GPT

### 3.1 MBR 结构与分区规则

MBR（Master Boot Record）位于硬盘**第一个扇区，共 512 字节**，内部结构是必背数据：

| 区段 | 字节数 | 作用 |
|---|---|---|
| 引导程序 | 446 | 加载操作系统引导 |
| 分区表 | 64 | 记录分区信息，每项 16 字节 |
| 结束标志 | 2 | 魔数标记，校验扇区有效 |

分区规则：主分区与扩展分区总数**不超过 4 个**；扩展分区**最多 1 个且不能直接格式化使用**；在扩展分区内划分逻辑分区，编号从 5 起。

### 3.2 GPT 与两者对比

GPT（GUID Partition Table）基于 LBA 寻址，除主分区表外还保留**备份分区表**，容量与安全性都优于 MBR，可突破 4 个主分区的限制并支持大容量硬盘。

| 维度 | MBR | GPT |
|---|---|---|
| 分区表位置 | 第 1 个扇区（512 B） | 多处存放，含备份分区表 |
| 主分区数量 | 最多 4 个（或 3 主 + 1 扩展） | 不受 4 个限制 |
| 容量支持 | 不适合超大容量硬盘 | 支持大容量硬盘 |
| 寻址方式 | CHS 与 LBA 混合 | 基于 LBA |
| 可靠性 | 分区表单点存放，损坏即丢失 | 有备份，安全性更高 |

### 3.3 分区工具与刷新

| 工具 | 适用分区表 | 说明 |
|---|---|---|
| `fdisk` | MBR | 经典交互式分区工具 |
| `gdisk` | GPT | GPT 环境的对应工具 |
| `parted` | 通用 | 可直接完成 MBR 与 GPT 两类操作 |
| `partprobe` | 任意 | 分区修改后不重启刷新内核分区表 |

供 LVM 使用的分区需在分区类型中标识为 **8e（Linux LVM）**，这是创建 PV 前的准备步骤。

### 3.4 格式化：mkfs 系列

格式化即在分区或逻辑卷上创建文件系统。`mkfs` 是前端统一命令：

```bash
mkfs -t ext4 /dev/sda1      # -t 指定文件系统类型
mkfs -t ext3 -c /dev/hda2   # -c 格式化前检测坏块
mkfs.ext4 /dev/sdb1
mkfs.xfs /dev/sdb1
mkfs.vfat /dev/sdb1         # FAT32
mkswap /dev/sdb1            # 交换空间专用，不走 mkfs
```

`mke2fs` 是 ext 系列的底层命令，`mkfs.ext4` 等专用命令是其后端封装。

### 3.5 文件系统检查与参数调整

`fsck` 与 `e2fsck` 用于扫描并修复目录链接中断、时间标记错误、inode 指向错误等问题：

```bash
fsck -t ext4 /dev/sda1
e2fsck -f /dev/vg_data/lv_home   # 缩容前的强制检查
```

系统启动时会自动执行检查；手动执行必须在**单用户模式且文件系统已卸载**的状态下进行，带病挂载运行中的文件系统会造成二次损坏。

查看与调整文件系统属性：

```bash
tune2fs -l /dev/sda1      # 查看属性
dumpe2fs -h /dev/sda1     # 查看超级块概要
tune2fs -L DATA /dev/sda1 # 设置卷标
tune2fs -j /dev/sda1      # ext2 转 ext3（添加日志）
```

选项 `-c`（挂载次数检查阈值）、`-i`（检查间隔）、`-m`（保留块百分比）、`-L`（卷标）、`-j`（添加日志）覆盖了 tune2fs 的全部常考点，具体数值按实验机需求给出即可。

文件系统除设备名外还有两种标识：**LABEL**（手动设置的卷标）与 **UUID**（创建文件系统时自动生成的唯一标识）：

```bash
e2label /dev/sda1          # 查看卷标
blkid /dev/sda1            # 查看 UUID 等信息
findfs LABEL=DATA          # 按标识反查设备
mount -L DATA /mnt/data    # 按卷标挂载
```

按 UUID 挂载用 `mount -U`，后接 `blkid` 输出的 UUID 串；挂载 fstab 时同样可以把设备名换成 `UUID=...` 或 `LABEL=...` 写法。在 fstab 中用 UUID 代替设备名，可避免插拔磁盘导致盘符漂移引发的挂载错误。

## 四、LVM 逻辑卷

### 4.1 四层结构

LVM（Logical Volume Manager）让分区可以在线扩大缩小、跨盘拼接，解决普通分区「定死大小、满了只能备份重建并停机」的痛点。四层结构从上到下为：**文件系统 → LV 逻辑卷 → VG 卷组 → PV 物理卷**，其中 PV 由 PE、LV 由 LE 构成，PE 是 PV 的最小分配单元，默认 **4 MB**，LE 与 PE 一一对应，扩缩容的本质就是移动 PE/LE 数量。一个便于记忆的类比：PV 是砖头，VG 是仓库，LV 是从仓库切出的房间，扩容相当于往仓库里补砖头，而不是拆房重盖。

### 4.2 创建全流程

```bash
fdisk /dev/sdb                      # 划分分区并将类型置为 8e
pvcreate /dev/sdb1                  # 1. 建物理卷
vgcreate vg_data /dev/sdb1          # 2. 建卷组（可一次放入多个 PV）
lvcreate -L 10G -n lv_home vg_data  # 3. 建逻辑卷，-L 大小、-n 名称
mkfs.ext4 /dev/vg_data/lv_home      # 4. 格式化
mount /dev/vg_data/lv_home /home    # 5. 挂载使用
```

LV 的设备路径固定为 `/dev/卷组名/逻辑卷名`。卷组空间不足时用 `vgextend vg_data /dev/sdb2` 动态补充 PV。

### 4.3 在线扩容

扩容分两步，**两步缺一不可**：

```bash
lvextend -L +5G /dev/vg_data/lv_home    # 第一步：扩大逻辑卷
resize2fs /dev/vg_data/lv_home          # 第二步：刷新文件系统，必须执行
```

只执行 `lvextend` 而不执行 `resize2fs`，块设备虽然变大，文件系统并不感知，`df` 看到的可用容量不变——这是实验中最容易踩的坑。

### 4.4 缩容

缩容与扩容顺序相反，且**必须先卸载**，文件系统先缩、逻辑卷后缩：

```bash
umount /home                                # 1. 卸载
e2fsck -f /dev/vg_data/lv_home              # 2. 强制检查
resize2fs /dev/vg_data/lv_home 10G          # 3. 先缩文件系统
lvreduce -L 10G /dev/vg_data/lv_home        # 4. 再缩逻辑卷
```

若顺序颠倒（先 `lvreduce`），被裁掉的块可能正存放文件数据，直接造成数据丢失。另需注意：XFS 文件系统**只支持扩容、不支持缩容**，ext 系列才可缩可扩。

### 4.5 查看命令与禁忌

```bash
pvs / vgs / lvs            # 简明列表
pvdisplay / vgdisplay / lvdisplay   # 详细信息
```

/boot 分区不能放在 LVM 上，引导程序无法识别逻辑卷；安装系统时根分区与交换分区是必须单独划分的两个分区。

## 五、文件系统类型速览

日志文件系统（ext3/ext4、XFS、JFS、Btrfs）先写日志再写数据，断电崩溃后可快速恢复、避免全盘扫描；无日志文件系统（ext2、FAT32）结构简单但恢复慢。常用类型对比：

| 类型 | 日志 | 关键特性与限制 | 典型场景 |
|---|---|---|---|
| ext4 | 有 | extent 分配，兼容 ext2/ext3，单文件上限约 16 TB | 通用根分区与数据分区 |
| XFS | 有 | 高并发、延迟分配，可扩不可缩 | 数据库与高 I/O 服务器 |
| ext2 | 无 | 崩溃后恢复慢 | 只读存储、小容量介质 |
| FAT32（vfat） | 无 | 单文件最大 4 GB，Windows 默认格式化下分区限 32 GB | U 盘跨平台共享 |
| NTFS | — | Linux 下经 ntfs-3g 驱动访问，性能略低 | 与 Windows 双系统共享 |
| iso9660 | — | 光盘标准，只读 | CD/DVD 与 ISO 镜像 |
| swap | — | 虚拟内存，无需挂载 | 交换分区或交换文件 |
| tmpfs / proc / sysfs | — | 驻留内存或内核接口，不占磁盘 | /tmp、/proc、/sys |

## 六、挂载与自动挂载

### 6.1 mount 与 umount

```bash
mount /dev/sda1 /mnt/usb              # 基本挂载
mount -t ext4 -o ro /dev/sdb1 /mnt    # 指定类型、只读
mount -o loop rhel.iso /mnt/cdrom     # 挂载 ISO 镜像
umount /mnt/usb                       # 按挂载点或设备名卸载
```

常用选项：`-t` 指定文件系统类型，`-r` 只读挂载，`-a` 挂载 fstab 中全部设备，`-o loop` 挂载镜像文件，挂载 vfat 时可用 `-o iocharset=cp936` 支持中文文件名。fstab 中 `defaults` 包含 rw、suid、dev、exec、auto、nouser、async 七项；按需还可用 ro、noauto、noexec、nosuid、remount、noatime（提升性能）等。

挂载注意事项：挂载点必须提前创建且为空目录；同一挂载点不能同时挂载两个文件系统；有进程正在访问（busy）时无法卸载。

### 6.2 解除占用与强制卸载

```bash
fuser -cu /mnt/usb     # 查看哪些进程占用了挂载点
fuser -ck /mnt/usb     # 终止全部占用进程后再卸载
lsof /mnt/usb          # 另一种排查占用进程的手段
umount -f /mnt/usb     # NFS 假死等场景强制卸载
```

卸载失败的报错并不说明设备故障，而是「目录正被使用」，先找到占用者再处理是标准流程。

### 6.3 可移动介质

光盘可自动挂载，也可 `mount /media/cdrom` 手动挂载，弹出用 `eject`；U 盘按 `/dev/sd[a-p]` 规则识别，常见操作为 `mount -t vfat /dev/sda1 /mnt/usb`；软盘需手动挂载；镜像文件一律走 `-o loop`。

### 6.4 /etc/fstab 开机自动挂载

系统开机读取 `/etc/fstab` 自动完成挂载，每行六个字段，顺序必背：

| 字段 | 名称 | 含义 |
|---|---|---|
| 1 | fs_spec | 设备名、UUID 或 LABEL |
| 2 | fs_file | 挂载点 |
| 3 | fs_type | 文件系统类型 |
| 4 | fs_options | 挂载选项 |
| 5 | fs_dump | 备份频率，0 表示不备份 |
| 6 | fs_pass | 开机 fsck 检查顺序，0 表示不检查 |

新增分区 `/dev/sdc1` 挂载到 `/mnt/data_disk` 的完整实操：

```bash
mkdir -p /mnt/data_disk
mount /dev/sdc1 /mnt/data_disk
vi /etc/fstab
# 写入一行：
/dev/sdc1  /mnt/data_disk  ext4  defaults  0 0
mount -a
```

**写 fstab 后必须用 `mount -a` 验证**：该命令会尝试挂载 fstab 中所有尚未挂载的条目，配置有误会当场报错，比重启后才发现系统起不来代价小得多。

### 6.5 交换空间

swap 实现虚拟内存、补充物理内存，是唯一不需要挂载的空间类型。流程：

```bash
dd if=/dev/zero of=/swapfile bs=1024 count=2097152   # 创建交换文件：bs×count 即总容量
mkswap /swapfile        # 创建交换文件系统
swapon /swapfile        # 激活；swapon -a 按 fstab 全部激活
swapoff                 # 禁用
```

持久化同样写入 fstab，开机自动启用。

## 七、容量查看命令

查看「还剩多少空间」与「空间被谁占用」是两组不同的命令：

| 命令 | 对象 | 典型用法 |
|---|---|---|
| `df` | 磁盘分区整体 | `df -Th` 显示容量、使用率与文件系统类型，`df -h` 人性化单位 |
| `du` | 单个文件/目录 | `du -sh /var/log` 统计目录实际占用 |
| `lsblk` | 块设备结构 | `lsblk -f` 查看设备、挂载点与 UUID |
| `free` | 内存与 swap | `free -h` 查看物理内存与交换区使用 |

`df` 面向分区、`du` 面向文件目录，排查磁盘满告警的工作流即「先 `df -Th` 定位哪个分区满，再 `du -sh` 逐层下钻找大目录」。

## 八、权限、归属与 umask

### 8.1 八进制与符号两种写法

`ls -l` 输出的权限串由九位 r（读）、w（写）、x（执行）组成，依次对应所有者、同组用户、其他用户，八进制对照为 $r=4$、$w=2$、$x=1$：

| 权限串 | 八进制 | 含义 |
|---|---|---|
| rwxr-xr-x | 755 | 所有者全部，组与其他用户读加执行 |
| rw-r--r-- | 644 | 所有者读写，组与其他用户只读 |
| rwxr-xr-- | 754 | 其他用户无任何权限 |
| rwxrwxrwx | 777 | 所有用户读写执行 |
| rw-rw-r-- | 664 | 组内可写，其他只读 |

符号写法用「谁、做什么、改什么」表达：

```bash
chmod 755 /home/user/file.txt     # 八进制方式整体赋值
chmod a+w /home/user/file.txt     # 给所有用户(a)增加写权限
chmod o+w /home/test_dir/info.txt # 给其他用户(o)增加写权限
chmod o+r /opt/app                # 给其他用户增加读权限
chmod +x backup.sh                # 给脚本赋予执行权限
find /opt/app -type f -exec chmod 644 {} \;   # 批量修改目录内普通文件
```

归属修改由 `chown` 完成，与 `chmod` 职责严格区分——chmod 改权限、chown 改所有者与所属组，这是模拟卷里出现频率最高的一组干扰项：

```bash
chown user01 /home/test_dir/info.txt   # 只改属主
chown test:testgroup file.txt          # 同时改属主与属组
chown :dev_group /data/dev_share       # 只改属组
```

权限调整只允许文件所有者与 root 执行，普通用户无法修改 root 创建文件的权限。给组规划共享目录的标准组合是「建组、建用户入组、目录赋 770、属组指向该组」。

### 8.2 硬链接与软链接

链接命令 `ln` 的两个方向在属性上有本质差异，「给目录创建链接只能用软链接」：

| 维度 | 硬链接 | 软链接（符号链接） |
|---|---|---|
| inode | 与原文件共用同一 inode | 拥有独立 inode，仅记录原文件路径 |
| 跨分区 | 不能跨磁盘/分区 | 可以跨分区、跨设备 |
| 目录 | 系统禁止对目录建硬链接 | 可对目录创建 |
| 删除原文件 | 链接仍可用 | 变为无效链接 |
| 附加效果 | 每建一个硬链接，原文件链接计数加 1 | 不改变原文件计数 |

### 8.3 umask 推算及其边界

`umask` 是权限掩码，决定新建文件与目录的默认权限。课程讲义与模拟卷使用的减法推算法则是：普通文件基准权限 $666$，目录基准权限 $777$，用基准减去 umask 得默认权限。默认 `umask=022` 时：

$$666-022=644,\qquad 777-022=755$$

`umask=027` 时，讲义把新建文件默认权限给成 **640**——该值已无法逐位「减」出来（其他位上 6 减 7 并不成立），恰是按位规则的结果。笔者在核对模拟卷答案时发现了减法快捷方法的边界：一卷中给 `umask=033`，按减法算出新建文件 $666-033=633$，而在实验机以 `umask 033` 新建文件实测，权限是 **644** 而非 633。原因在于：严格规则是**基准权限按位与上 umask 的取反**——每个八进制位的三个权限位独立做「基准位 ∧ 非掩码位」；033 要掩掉 wx，而基准 6（rw）本就不含 x，减法把并不存在的 x 也当作可扣项，结果连应当保留的 r 一并错扣。结论：只有当 umask 各位表示的权限位全部落在对应基准位内（如 022、027 之于目录）时，减法才与按位规则一致；遇到 033 这类含「基准中不存在的位」的掩码，必须回到按位运算。

## 九、磁盘限额 quota

quota 用于限制用户或用户组的磁盘用量，防止空间滥用，作用在两个维度：**磁盘块**（容量）与 **inode**（文件个数）。三种限制策略：

| 策略 | 行为 |
|---|---|
| 硬限额 | 绝对上限，超过后无法再写入 |
| 软限额 | 告警阈值，超过后仍可写入但收到警告 |
| 宽限时间 | 软限额超期后强制执行硬限额，默认 7 天 |

配置时必须保证硬限额大于软限额。完整六步配置：

```bash
vi /etc/fstab                          # 1. 对应行选项追加 usrquota,grpquota
mount -o remount /home                 # 2. 重新挂载使选项生效
quotacheck -cmvug /home                # 3. 创建配额数据库
quotaon -avug                          # 4. 开启配额
edquota student                        # 5a. 交互式设置某用户限额
# 5b. 命令式 setquota 可在一条命令中直接给出软硬限额数值，适合脚本调用
edquota -p model_user new_user         # 6. 按模板用户复制限额
```

查看与汇总：

```bash
quota -vu student          # 查看单个用户限额与用量
repquota -augv             # 全文件系统配额汇总
```

前提是内核支持 quota、安装 quota 软件包并开机启动 quota 服务。

## 十、Shell 脚本与磁盘备份实操

### 10.1 脚本执行权限与 Shebang

Shell 脚本**创建后默认没有执行权限**，必须 `chmod +x script.sh` 后才能以 `./script.sh` 运行；操作系统只有对可执行文件才解析首行 Shebang。若直接 `bash script.sh` 执行，Shebang 会被忽略。Shebang 两种写法的取舍：`#!/bin/bash` 用绝对路径、效率直接但依赖解释器位置，`#!/usr/bin/env bash` 从 PATH 查找、兼容性更好。Shebang 必须位于第一行，前面不得有任何内容。

### 10.2 打包、压缩与拷贝备份

`tar` 同时完成打包与压缩，参数按功能记忆：

| 参数组合 | 作用 |
|---|---|
| `tar -zcvf 包名.tar.gz 源目录` | 打包并用 gzip 压缩（c 创建、v 显示过程、f 指定包名、z 走 gzip） |
| `tar -zxvf 包名.tar.gz -C /opt` | 解压（x 解出），`-C` 指定解压目标目录 |
| `tar -jcvf 包名.tar.bz2 源目录` | 打包并用 bzip2 压缩，`-j` 对应 bz2 |
| `cp -a 源目录 目标` | 归档式复制，保留权限、属主与软链接属性，课程说明其等价于 r、p、l 组合 |
| `dd if=/dev/sda of=boot.bin bs=512 count=1` | 按扇区读取，备份磁盘首扇区（MBR） |

`dd` 的核心选项为 if（输入文件或设备）、of（输出文件或设备）、bs（块大小）、count（块数），既能做设备级备份恢复，也用于制作交换文件与镜像文件。

### 10.3 菜单式备份脚本

实验环节用一个交互式备份菜单把函数、`select`、`case` 与 `source` 串在一起：函数库脚本只定义 `sql_bak`、`sync_bak`、`tar_bak` 等备份函数（内部对应 mysqldump、rsync、tar 命令），主程序脚本以 `source` 导入函数库后，用 `select` 生成菜单、`case` 匹配选择。要点有四：`PS3` 变量定制 select 的提示符；`select` 默认无限循环，需 `break` 或 `exit` 退出；`case` 分支用竖线连接多个模式，序号、全拼、大小写都能命中；`source 路径` 与「点号加空格」写法等价，把函数库内容导入当前 Shell 环境而非另起进程。函数库与主程序分离的价值在于同一组备份工具逻辑可被多个脚本复用，路径放在约定的项目目录内即可。

### 10.4 定时备份

磁盘挂载、fstab 自启与定时备份可合成一条完整运维链。每天凌晨 1:00 备份挂载目录的 crontab 写法：

```bash
crontab -e
# 五段时间字段依次为：分 时 日 月 周
0 1 * * * tar -zcvf /backup/data_back.tar.gz /mnt/data_disk
```

时间取值范围：分 0–59、时 0–23、日 1–31、月 1–12、周 0–7（0 与 7 均指周日），`*` 表示该单位每一值都命中。无人值守任务常把输出屏蔽并放后台：

```bash
tar -zcvf test.tar.gz /test > /dev/null 2>&1 &
```

其中 `/dev/null` 是丢弃一切的「黑洞文件」，`2>&1` 把标准错误并入标准输出，末尾 `&` 放入后台——长耗时备份不占用终端。

## 十一、常见误区

以下条目多由自测卷错题订正而来，按主题归档：

1. **逻辑分区编号**：主分区占 1–4，第一个逻辑分区从 **5** 开始，写作 `/dev/sda5`，不存在 sda1–4 之外的第四主分区编号竞争。
2. **扩展分区不能直接格式化**：它只是容纳逻辑分区的外壳，且最多一个。
3. **lvextend 之后忘记 resize2fs**：逻辑卷变大而文件系统未刷新，`df` 容量不变，扩容视为未完成。
4. **缩容顺序与卸载**：必须先 umount、再缩文件系统、最后缩 LV；XFS 根本不支持缩容。
5. **/boot 与 LVM**：引导程序不识别逻辑卷，/boot 不能放 LVM；装机必须单独划分的是根分区与交换分区。
6. **fstab 改完直接重启**：应先 `mount -a` 验证，字段顺序为设备、挂载点、类型、选项、dump、fsck 顺序，后两位常写 0 0 但要明白其含义。
7. **umount 报 busy**：问题在占用进程而非设备，`fuser -cu` 查看、`fuser -ck` 清除，或 `lsof` 定位后再卸载。
8. **chmod 与 chown 混淆**：chmod 管权限，chown 管属主属组；「chown 可修改文件的所有者和所属组」正确，「chmod 可修改所有者」错误。
9. **权限串判型**：`drwxrw-r--` 首字符 d 表示目录，所有者权限看第 2–4 位（rwx），八进制转换按 r=4、w=2、x=1 逐段求和。
10. **umask 减法陷阱**：`umask=033` 时新建文件默认权限实测为 644，而非按减法得到的 633；减法只在掩码位包含于基准位时成立，通则永远是按位与掩码取反。
11. **硬链接边界**：硬链接共用 inode、不能跨分区、不能对目录创建；删除原文件后仍有效的链接是硬链接，软链接删除原文件即失效。
12. **quota 阈值倒置**：软限额必须低于硬限额，否则告警逻辑失去意义；fstab 未加 usrquota/grpquota 并 remount 时，quotacheck 无从生效。
13. **脚本没加执行权限**：`Permission denied` 时先 `chmod +x`；用 `bash script.sh` 方式运行则无需执行位，同时 Shebang 不生效。
14. **备份目录忘用 -a**：普通 `cp -r` 会丢失权限与属主信息并跟穿软链接，含属性的整目录备份应使用 `cp -a`。

## 十二、总结要点

存储管理知识链可以压缩为四句话。**分区层**：MBR 首扇区 446+64+2 的结构决定 4 个主分区上限，GPT 以备份分区表和 LBA 寻址突破限制；fdisk 对 MBR、gdisk 对 GPT、parted 通用。**卷管理层**：PV→VG→LV 三层加默认 4 MB 的 PE 是在线扩缩容的基础，扩容两条命令 `lvextend` 与 `resize2fs` 缺一不可，缩容则须卸载在先、文件系统先缩。**挂载层**：手动 mount/umount，开机靠 fstab 六字段并以 `mount -a` 当场验证，busy 时 `fuser -ck` 解占用；查看容量 df 管分区、du 管目录。**权限与运维层**：八进制与符号两套写法分别对应 chmod 与整体赋值、增量调整，chown 管归属，umask 决定新对象默认权限但减法有边界、以按位取反为准；quota 以「软告警、硬封顶、宽限 7 天」约束用量；备份链条上 tar 打包压缩、cp -a 保属性、dd 到扇区、crontab 定时驱动脚本，构成日常运维的完整闭环。
