---
title: 医学影像实验室上机路线 · DICOM 转换、FSL、CUDA、Slurm 与 nnUNet
subject: 虚拟染色/科研
category: 研究
source: 豆包对话 · 医学影像实验室 Linux 学习路线
summary: 面向实验室共享 GPU 服务器的上机操作路线，按「账号与环境准备 → DICOM 转 NIfTI → 预处理与配准 → GPU 侧依赖 → 排队与训练 → 容器化」的顺序，整理 dcm2niix 与 find 批量转换写法、FSL 的 bet/flirt/fast 分工、CUDA 与 cuDNN、PyTorch 安装通道的版本对应、Slurm 的 sbatch 关键参数、nnUNet 规划预处理与训练的命令顺序，以及 Docker/Singularity 镜像片段，并保留权限、软件源、pip 受限等真实卡点。
---

# 医学影像实验室上机路线 · DICOM 转换、FSL、CUDA、Slurm 与 nnUNet

## 一、概述：这条路线要解决什么

本文整理的是一条**上机工具链路线**，而不是一条算法结论。它回答的问题很具体：当实验室只有一台共享的 GPU 服务器、数据以 DICOM 形式堆放、训练框架要求特定的 CUDA 版本、训练任务需要排队才能拿到卡时，一名刚接触 Linux 的研究生应当按什么顺序把这些环节逐个打通。

材料来自一段以「医学影像实验室 Linux 学习路线」为题的长对话（162 条消息）。该对话的前半部分给出了一份按工具链展开的路线，涉及 dcm2niix、FSL、ITK、CUDA/cuDNN、Slurm、nnUNet、Docker 与 Singularity；中段退化为对单条基础命令的零散追问；尾部约六分之一已转向 HTTP 状态码、后端框架与容器编排等另一主题域，与本文无关，另有专篇整理，此处不取。

需要与本文区分的是《服务器、训练与实验 · 长对话整理》一篇：那篇记录的是训练过程中的诊断结论与假设修正，属于「跑起来之后发生了什么」；本篇只覆盖「如何跑起来」，即数据转换、环境配置、任务排队与训练启动的操作流程。

**关于脱敏**：原料属于实验室共享服务器场景，涉及他人主机、账号与目录。本文一律写作「实验室共享服务器」「远程实例」「项目目录」；`/data/dicom`、`/data/nifti`、`/output` 等路径保留为**教学示例**，不代表任何真实挂载点；原料中出现的内网地址、邮箱、个人用户名与任何凭据形态均不进入本文。所有命令与参数均照原料记录，原料未给出的参数本文不补，并注明「以实验室实际安装为准」。

## 二、环境与账号准备

共享服务器上的第一个障碍通常不是算法，而是「有没有一个能登录的账号、能不能改系统配置、装了包会不会弄坏别人的环境」。原料对此给出的是一条标准流程：先由管理员建普通账号并赋予必要的 sudo 组，再由使用者在自己的目录里工作。

```bash
useradd -m labuser && passwd labuser
usermod -aG sudo labuser
```

`-m` 会同时创建该用户的家目录。原料反复强调的一点是：普通用户对 `/etc` 下的文件默认只有读权限，改配置必须显式加 `sudo`，而日常的数据与脚本应当留在自己的目录中，不要在家目录里滥用 `sudo`。

远程接入与长任务保活是第二件事。文件传输用 `scp`，长时间运行的任务用 `tmux` 或 `screen` 托管，以免 SSH 会话中断把训练一起带走。

```bash
scp user@remote_ip:/path/to/source_file /local_path/
```

其中的 `remote_ip` 在原料里是具体的内网地址，此处按示例写法保留。

数据落地之后要解决「软件从哪装、装坏怎么办」。原料给出的包管理分两条：系统级用 `apt`（Ubuntu）或 `yum`（CentOS），Python 级用虚拟环境。系统级安装的第一个真实卡点是包名与软件源：

```bash
sudo apt update
sudo apt install mlocate
```

原料记录了一次 `Unable to locate package` 的排查，原因被归纳为三类：包名拼写错误（实际敲成了 `mloacte`）、当前软件源中确实没有该包、软件包索引未更新。更麻烦的是 Ubuntu 24.04 之后源文件位置发生了变化，配置的编辑对象迁移到了 `/etc/apt/sources.list.d/ubuntu.sources`，采用 DEB822 的多行格式，继续改 `sources.list` 不生效。换源前先备份：

```bash
sudo cp /etc/apt/sources.list.d/ubuntu.sources /etc/apt/sources.list.d/ubuntu.sources.bak
```

Python 侧环境有两条路。原料第一条是 conda，这也是实验室最常用的做法：

```bash
wget https://repo.anaconda.com/archive/Anaconda3-2023.03-Linux-x86_64.sh && bash Anaconda3-2023.03-Linux-x86_64.sh
conda create -n med-env python=3.9
conda activate med-env
```

第二条是系统自带的 venv。原料记录了在 Ubuntu 24.04 上直接 `pip install` 被拒的现象：系统 Python 被标记为「外部管理」，禁止 pip 向系统级环境写包，正确反应是改用虚拟环境，而不是去绕过该限制。

```bash
sudo apt install python3-venv
python3 -m venv myenv
source myenv/bin/activate
pip install SimpleITK
deactivate
```

| 目的 | 原料给出的命令 |
|---|---|
| 创建普通账号并设密码 | `useradd -m labuser` 之后执行 `passwd labuser` |
| 加入管理员组 | `usermod -aG sudo labuser` |
| 放行远程登录与网页服务端口 | `ufw allow 22/tcp`；`ufw allow 8000/tcp` |
| 与远程实例互传文件 | `scp user@remote_ip:/path/to/source_file /local_path/` |
| 长任务保持会话 | `tmux` 或 `screen` |
| 增量备份影像数据目录 | `rsync -avz /data /backup` |
| 定时执行备份 | `crontab -e` 中写入 `0 2 * * *` 的 rsync 任务 |
| 用 conda 隔离实验环境 | `conda create -n med-env python=3.9` |
| 用 venv 隔离实验环境 | `python3 -m venv myenv` 后 `source myenv/bin/activate` |
| 查看磁盘与目录占用 | `df -h`；`du -sh ~/project` |

## 三、数据转换：DICOM 到 NIfTI

影像数据进入分析流程的第一步是格式转换。DICOM 是设备与 PACS 系统的存档格式，逐序列分文件、头部携带扫描参数；NIfTI（`.nii` 与压缩形式 `.nii.gz`）则是神经影像与深度学习管线常用的单文件体积格式，便于配准、分割与批量读取。原料选择的转换工具是 `dcm2niix`，安装方式直接取发布包：

```bash
wget https://github.com/rordenlab/dcm2niix/releases/download/v1.0.20230415/dcm2niix_lnx.zip && unzip dcm2niix_lnx.zip
```

单个输入目录的转换写法为：

```bash
./dcm2niix -o /output -f %s_%p -z y /input/dicom
```

其中 `-o` 指定输出目录，末位是输入的 DICOM 目录；`-f` 与 `-z` 在原料中只出现了命令形式而未逐项注释，本文按原始记录保留，具体语义以该版本工具的帮助输出为准。

真正需要拆开讲清楚的是批量写法。原料给出的核心命令是：

```bash
find /data/dicom -name "*.dcm" -exec dcm2niix -o /data/nifti {} \;
```

这条命令的每个片段含义如下（`-exec`、`{}`、`\;` 三者的解释直接来自原料对 `find` 的说明）。

| 片段 | 作用 |
|---|---|
| `/data/dicom` | 搜索的起始路径，省略时默认为当前目录 |
| `-name "*.dcm"` | 按文件名匹配，支持通配符 |
| `-exec` | 对每一个命中的文件执行其后的命令 |
| `dcm2niix -o /data/nifti` | 被执行的命令本体，`/data/nifti` 为输出目录 |
| `{}` | 代表当前找到的那个文件，由 `find` 逐个替换 |
| `\;` | 标记被执行命令的结束，反斜杠用于转义 |

原料为这三个片段另给了一个更直观的例子，可与转换命令对照理解：

```bash
find /tmp -name "*.tmp" -exec rm {} \;
```

除 `-exec` 之外，原料还给出了 `find` 的常用条件：`-type` 按类型（`f` 普通文件、`d` 目录、`l` 符号链接）、`-size` 按大小（`+100M`、`-1k`）、`-mtime` 与 `-mmin` 按修改时间、`-perm` 按权限、`-user` 与 `-group` 按属主属组、`-print` 打印结果。这套条件在影像数据整理时最直接可用，例如清点某个目录下近 7 天内改动过的文件。

`find` 也可以与 `xargs` 组合，这是原料中出现的第二种批量风格：

```bash
find /data -name "*.dcm" | xargs -I {} dcm2nii {} -o /output
find /path/to/dicom -name "*.dcm" | xargs -n 1 dcm2nii
```

需要特别指出的一处**不严谨**：这两条用的是 `dcm2nii`，而前面安装与单目录转换用的是 `dcm2niix`。原料中两种写法混用，`dcm2nii` 是较早的独立程序名。上机时应先用 `which` 确认本机实际存在的是哪一个，不要照抄字符串。这也解释了当时为什么会在这类命令上卡住——命令格式正确，可执行文件名却是另一个。

转换之后要做的是核对，而不是直接训练。原料给出的元数据查看方式是 dcmtk 工具包：

```bash
dcmdump input.dcm
```

Python 侧读取则依赖三个库，原料的安装命令如下：

```bash
pip install pydicom
pip install SimpleITK
pip install nibabel
```

## 四、预处理与配准：FSL 三件套与其他工具

预处理部分原料给出的命令非常克制：只给了工具名、一句话用途，以及一条完整的 ANTs 配准命令行。对 FSL 三件套，它没有列出任何参数。

```bash
sudo apt-get install fsl
```

| 环节 | 工具 | 原料给出的信息 | 参数情况 |
|---|---|---|---|
| 头骨去除 | `bet` | 用途为「去脑壳」，即剥除颅骨等非脑组织 | 原料未记录具体参数 |
| 线性配准 | `flirt` | 用途为线性（刚体/仿射）配准 | 原料未记录具体参数 |
| 组织分割 | `fast` | 用途为脑组织分割 | 原料未记录具体参数 |
| 元数据查看 | `dcmdump` | 仅一条示例命令 | 同上 |
| 高精度配准 | `antsRegistration` | 给出完整命令行 | 见下 |
| 纹理特征提取 | PyRadiomics | 给出 Python 调用片段 | 属库接口而非命令行 |

本文不打算为 `bet`、`flirt`、`fast` 补一张参数表——原料确实没有，凭记忆填写正是笔误与版本错配的来源。合理的做法是按工具的官方文档与本机安装版本核对：FSL 的文档地址为 https://fsl.fmrib.ox.ac.uk/fsl/fslwiki 。

原料中唯一完整给出的配准命令属于 ANTs，它明确写出了维度、固定图像、移动图像与输出前缀四项，可视为「一条配准命令至少要说明哪些信息」的参照：

```bash
antsRegistration --dimensionality 3 \
                 --fixed-image fixed.nii \
                 --moving-image moving.nii \
                 --output transform_prefix
```

对三维体积数据，这条命令的形式本身就说明了配准任务的四个输入：空间维度、作为参照的固定图像、需要被形变对齐的移动图像、以及变换结果的输出前缀。原料另外提到 ITK 与 SimpleITK 作为分割与配准算法的底层库，3D Slicer 用于可视化与分割标注，MRIcroGL 用于体数据浏览与 ROI 查看，但这些工具在具体流程中的调用细节未展开。

从操作顺序看，这一阶段的产出是「干净、对齐、可切块」的体数据，它必须等第三节的格式转换完成之后才能开始，也必须等下一节的 GPU 环境就绪之后才可能与训练衔接。

## 五、CUDA 与 PyTorch：GPU 侧环境

共享服务器上的第二个真实卡点是「驱动、CUDA、cuDNN、框架版本必须成套」。原料给的路径是从驱动向上搭：

```bash
ubuntu-drivers autoinstall
nvidia-smi
nvcc --version
```

`nvidia-smi` 看驱动与卡的实时状态，`nvcc --version` 看工具包版本，这两个检查命令是原料明确写出的验证手段。CUDA 本身用 runfile 安装：

```bash
wget https://developer.download.nvidia.com/compute/cuda/11.7.1/local_installers/cuda_11.7.1_516.94.01_linux.run && sudo sh cuda_11.7.1_516.94.01_linux.run
```

cuDNN 以归档包形式解压后，把头文件与库文件复制到 CUDA 目录并放开读权限：

```bash
sudo cp cudnn-*-archive/include/cudnn*.h /usr/local/cuda/include/ && sudo cp -P cudnn-*-archive/lib/libcudnn* /usr/local/cuda/lib64/ && sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*
```

框架安装侧，原料给出的通道是 pip 加索引地址：

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install tensorflow-gpu==2.12
```

安装后的验证片段原料写得很清楚：

```python
import torch
print(torch.__version__)
print(torch.cuda.is_available())  # 输出 True 表示 GPU 可用
```

关于版本对应，需要坦率说明一点：**原料没有给出一张 CUDA 与 PyTorch 的兼容矩阵**，它只是在若干命令字符串里露出了版本信息。本文只把这些零散信息整理成对照，它不构成通用兼容表；换一块卡或换一台机器时，正确做法是先查实验室服务器上实际装了什么，再选对应的安装通道。

| 原料中出现的片段 | 可直接读出的版本信息 |
|---|---|
| `cuda_11.7.1_516.94.01_linux.run` | CUDA 11.7.1 的安装包与驱动 516.94.01 绑定在同一 runfile 中 |
| `--index-url .../whl/cu117` | 走 CUDA 11.7 通道的 PyTorch 轮子 |
| `--index-url .../whl/cu118` | 原料注明用于 CUDA 11.8 |
| `cudnn-linux-x86_64-8.9.0.131_cuda11-archive.tar.xz` | cuDNN 8.9.0.131 面向 CUDA 11 系列 |
| `FROM nvidia/cuda:11.7.1-cudnn8-runtime-ubuntu20.04` | CUDA 11.7.1 与 cuDNN 8 共存于 Ubuntu 20.04 运行时镜像 |
| `pip install tensorflow-gpu==2.12` | 原料给出的 TensorFlow GPU 版本示例 |

因此上机时的检查动作比背表更重要：驱动状态看 `nvidia-smi`，工具包看 `nvcc --version`，框架侧看 `torch.cuda.is_available()`，Python 与 pip 自身版本看 `python3 --version` 与 `pip3 --version`。原料在这一点上的表述是「需确保 CUDA 与 cuDNN 的版本与软件包版本兼容，参考官方文档」，本文照此保留结论，不代为编造对应关系。

显存与多卡部分，原料给出的两条优化写法属于 TensorFlow：

```python
tf.config.experimental.set_memory_growth(tf.config.list_physical_devices('GPU')[0], True)

strategy = tf.distribute.MirroredStrategy()
with strategy.scope():
    model = tf.keras.Sequential(...)
```

以及一条显存泄漏排查工具名 `nvidia-memcheck`。这些只作为原料记录保留，本文不推断它们在当前版本下是否仍然适用。

## 六、排队与训练：Slurm 与 nnUNet

实验室共享 GPU 的第三个真实卡点是排队：卡是别人的任务正在占着，直接在前台跑训练既拿不到资源，也会因为会话超时被杀掉。原料给出的调度系统是 Slurm，安装与提交命令如下。

```bash
sudo apt-get install slurm-wlm
sbatch --gres=gpu:1 --time=0-1:0:0 --output=log.txt run.sh
```

作业脚本内部以 `#SBATCH` 声明资源，原料给的示例只有两行，最后一行是实际执行的训练命令：

```bash
#!/bin/bash
#SBATCH --nodes=1
#SBATCH --gres=gpu:1
python train_model.py
```

| 参数或片段 | 含义 |
|---|---|
| `sbatch` | 以批处理模式提交作业，而非在当前终端前台运行 |
| `--gres=gpu:1` | 申请 1 块 GPU |
| `--time=0-1:0:0` | 时限参数，原料未注释其格式约定，以集群文档为准 |
| `--output=log.txt` | 作业输出写入该文件，可事后用 `tail -f log.txt` 实时跟踪 |
| `run.sh` | 被提交执行的脚本 |
| `#SBATCH --nodes=1` | 脚本内声明使用 1 个节点 |
| `#SBATCH --gres=gpu:1` | 脚本内声明 GPU 资源 |

必须诚实记录一处缺口：**原料只整理了提交侧命令，没有记录队列查看与作业管理的命令**。也就是说，「看谁在跑、看自己排到第几、撤销一个排错的作业」这三件在共享集群上每天都要做的事，当时是空白的，只能向集群管理员索取本集群的命令表。这一缺失在实操中的代价很直接——提交之后无法判断作业是在排队还是在运行，只能靠 `tail -f` 反复查看输出文件是否开始增长，以及 `nvidia-smi` 与 `htop` 观察卡与 CPU 是否真的被占用。原料另外提到 PBS 作为同类调度系统，未给出命令。

nnUNet 部分原料给出的是一条完整的最短流程，也正好体现了「先规划预处理、再训练」的顺序：

```bash
git clone https://github.com/MIC-DKFZ/nnUNet.git
cd nnUNet
pip install -e .
nnUNet_plan_and_preprocess -t 200 --verify_dataset_integrity
nnUNet_train 2D nnUNetTrainerV2 200 0
```

从命令形式可以读出三点约定。其一，任务以数字编号标识（原料用的是 `200`），规划预处理用 `-t 200` 指定，训练时该编号必须再次出现并保持一致，否则训练找不到对应的预处理产物。其二，`--verify_dataset_integrity` 出现在规划阶段，说明数据一致性检查是在重活之前做的。其三，训练命令的参数顺序依次是维度配置、训练器类名、任务编号，末位还有一个 `0`；原料没有解释这四个位置的语义，本文不补写，按原始记录保留，实际使用前应查该版本自带的帮助。

推理与部署在训练之后。原料给出的部署侧优化片段是 TensorFlow 的 TensorRT 转换：

```python
import tensorflow as tf
from tensorflow.python.compiler.tensorrt import trt_convert as trt
converter = trt.TrtGraphConverterV2(input_saved_model_dir="saved_model")
converter.convert()
converter.save("trt_saved_model")
```

原料同时在流程里明确写了「使用 `dcm2niix` 转换 DICOM 到 NIfTI」作为预处理第一步，也就是说，本文第三、四、五、六节串起来正是它给的一条完整链路：格式转换、体积预处理、GPU 环境、排队训练、最后推理部署。

## 七、容器化：Docker、Neurodocker 与 Singularity

环境搭一次已经够麻烦，共享服务器上更麻烦的问题是「别人的机器上装不出同一套环境」。原料给出的答案是容器化，并把 Singularity 放在集群管理一节，与 Docker 并列——这在共享集群上是常见安排，普通用户往往没有 Docker 守护进程的使用权限。

Docker 的两个基本动作与 GPU 参数：

```bash
docker build -t med-env .
docker run -it --gpus all -v /data:/data med-env
```

`-v /data:/data` 把宿主机的数据目录挂进容器，`--gpus all` 透出全部 GPU，这里的 `/data` 同样是示例路径。原料给出的第一个 Dockerfile 片段是完整的，从 CUDA 运行时镜像一路装到 3D Slicer：

```dockerfile
FROM nvidia/cuda:11.7.1-cudnn8-runtime-ubuntu20.04
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository universe && add-apt-repository multiverse
RUN apt-get install -y 3dslicer
CMD ["3dslicer"]
```

第二个片段是推理部署方向的，原料只给了这三行，本文照此保留而不补全其余部分（例如依赖安装步骤原料并未写出）：

```dockerfile
FROM tensorflow/tensorflow:latest-gpu
COPY . /app
CMD ["python", "/app/predict.py"]
```

当需要的是整套影像工具而非单个软件时，原料给了 Neurodocker 的生成方式，一条命令把 FSL、FreeSurfer 与 ANTs 写进 Dockerfile：

```bash
neurodocker generate docker \
  --base-image ubuntu:20.04 \
  --pkg-manager apt \
  --install fsl freesurfer ants \
  --user=neuro \
  --minimize > Dockerfile
```

集群侧的运行命令用 `--nv` 透出 NVIDIA 设备：

```bash
singularity run --nv /path/to/container.sif
```

| 目标 | 原料给出的做法 |
|---|---|
| 构建本地镜像 | `docker build -t med-env .` |
| 带 GPU 与数据挂载运行 | `docker run -it --gpus all -v /data:/data med-env` |
| 以 CUDA 运行时为基础 | `FROM nvidia/cuda:11.7.1-cudnn8-runtime-ubuntu20.04` |
| 以框架镜像做推理容器 | `FROM tensorflow/tensorflow:latest-gpu` |
| 生成含多种影像工具的环境定义 | `neurodocker generate docker` 及 `--install fsl freesurfer ants` |
| 集群中运行容器 | `singularity run --nv /path/to/container.sif` |

## 八、常见误区与真实卡点

这一节把原料里确实踩到、且与本文主题相关的坑集中列出，其中第一条是原料自身给错的解释，本文予以更正。

**其一，`chown -R -p` 并不成立。** 原料在讲解「`-p` 在不同命令中的作用」时，把 `-p` 说成是 `chown` 的一个「忽略错误继续处理」的选项，并写出 `chown -R -p user:group project`。这个解释是**错误的**：`-p` 不是 `chown` 的选项，照抄这条命令不会得到所谓的容错行为。正确用法是——需要递归修改属主与属组时写作：

```bash
chown -R user:group project
```

其中 `-R` 表示递归，`user:group` 一次同时指定所有者与所属组（原料在权限章节给出的正是这个格式）。而「逐级创建目录」属于另一件事，用 `mkdir -p`；「复制时保留属性」也是另一件事，用 `cp -p`；解包时保留权限则用 `tar` 的 `-p`。这几处混淆的根源是把一个字母当成了通用开关。

| 命令 | `-p` 的真实含义 | 原料示例 |
|---|---|---|
| `mkdir` | 递归创建缺失的父目录 | `mkdir -p parent/child/grandchild` |
| `rmdir` | 逐级删除空的父目录 | `rmdir -p parent/child/grandchild` |
| `tar` | 打包与解包时保留权限与属性 | `tar -czvfp config.tar.gz /etc` |
| `cp` | 保留文件属性 | 与 `-r` 组合可用于目录复制 |
| `chown` | **无此选项**，原料的错误解释 | 递归改属主属组应写作 `chown -R user:group project` |

**其二，系统 Python 不许直接 pip。** Ubuntu 24.04 把系统环境标记为外部管理，`pip install` 会被拒。当时的正确反应是回到虚拟环境，而不是改写系统配置。

**其三，改错源文件。** 24.04 起软件源在 `/etc/apt/sources.list.d/ubuntu.sources`，格式为多行键值形式，继续编辑 `sources.list` 不生效；`Unable to locate package` 要先分辨包名拼写、源内容与索引未更新三种原因，其中原料实际遇到的正是拼写错误。

**其四，路径写错被误认为命令写错。** 原料记录了一次 `cd /test/year` 报 `No such file or directory`：目录实际建在家目录下（`~/test`），加了一个开头的斜杠就变成从根目录找起。绝对路径从 `/` 开始，相对路径相对于当前目录，这一条在敲转换命令时同样成立。

**其五，重定向与追加。** `>` 会清空原内容再写，`>>` 才是追加；`echo` 的文本必须紧跟命令本身并用引号包裹，重定向符号写在末尾。原料中因把文本写在 `>>` 之后而被判成路径，进而报权限错误。

**其六，编辑器与目录。** `vim` 不能直接打开目录；`:wq` 打不出来往往是因为仍处在插入模式，需先按 `Esc`。这类问题与影像流程无关，但确实会卡住改配置的那十几分钟。

**其七，工具名混用。** `dcm2niix` 与 `dcm2nii` 在原料中同时出现，上机前用 `which` 确认本机存在的是哪一个。

**其八，排队可见性缺失。** 如第六节所述，原料只有提交命令而没有队列查询与撤销命令，共享集群上这一项必须向管理员索取，否则无法判断任务是卡在队列还是已在运行。

## 九、总结要点：命令速查

下表按「要做的事」组织，全部命令来自原料原文，示例路径不含真实信息。

| 我要做 X | 用哪条命令 |
|---|---|
| 建账号并授权 | `useradd -m labuser && passwd labuser`；`usermod -aG sudo labuser` |
| 换源前先备份 | `sudo cp /etc/apt/sources.list.d/ubuntu.sources /etc/apt/sources.list.d/ubuntu.sources.bak` |
| 更新包索引并安装 | `sudo apt update`；`sudo apt install mlocate` |
| 建 conda 实验环境 | `conda create -n med-env python=3.9`；`conda activate med-env` |
| 建 venv 环境并进入 | `python3 -m venv myenv`；`source myenv/bin/activate` |
| 批量把 DICOM 转成 NIfTI | `find /data/dicom -name "*.dcm" -exec dcm2niix -o /data/nifti {} \;` |
| 转换单个 DICOM 目录 | `./dcm2niix -o /output -f %s_%p -z y /input/dicom` |
| 查看 DICOM 元数据 | `dcmdump input.dcm` |
| 安装 FSL 做预处理 | `sudo apt-get install fsl`（`bet`、`flirt`、`fast` 参数查官方文档） |
| 三维配准 | `antsRegistration --dimensionality 3 --fixed-image fixed.nii --moving-image moving.nii --output transform_prefix` |
| 装驱动并验证 | `ubuntu-drivers autoinstall`；`nvidia-smi` |
| 验证 CUDA 工具包 | `nvcc --version` |
| 装对应 CUDA 通道的 PyTorch | `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117` |
| 提交一块 GPU 的作业 | `sbatch --gres=gpu:1 --time=0-1:0:0 --output=log.txt run.sh` |
| 跟踪作业输出 | `tail -f log.txt` |
| 规划并预处理任务 200 | `nnUNet_plan_and_preprocess -t 200 --verify_dataset_integrity` |
| 启动 2D 训练 | `nnUNet_train 2D nnUNetTrainerV2 200 0` |
| 构建镜像 | `docker build -t med-env .` |
| 带 GPU 运行容器 | `docker run -it --gpus all -v /data:/data med-env` |
| 集群中运行容器 | `singularity run --nv /path/to/container.sif` |
| 递归改属主属组 | `chown -R user:group project`（没有 `-p`） |
| 逐级创建目录 | `mkdir -p parent/child/grandchild` |
| 增量备份数据 | `rsync -avz /data /backup` |

最后强调两点。其一，这条路线的**顺序是硬约束**：格式转换与完整性检查没做完就装框架，或者框架版本没对上就提交训练作业，返工成本远高于按序推进。其二，原料中的命令多是「最小可用形式」，凡本文标注为原料未记录之处——FSL 的参数、`--time` 的格式约定、nnUNet 训练命令末位参数、队列管理命令——都应以实验室实际安装的版本与集群文档为准，而不是照抄任何一份笔记，包括这一份。
