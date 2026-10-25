"""
teardown_observe.py — CUT / PSPStain 生成器「抽头拆解观察」
零训练：加载现有 netG 权重，把瓶颈 6 个 ResBlock 的输出分别用解码器解出，
看语义 / 结构随深度如何形成。

======== 你需要改的（搜 TODO）========
  CKPT_PATH : 训练好的 generator 权重（state_dict）
  DATA_DIR   : 若干张 2 通道 H/E 输入，.npy，shape [2,H,W] 或 [H,W,2]
  OUT_DIR    : 出图目录
  build_netG : 改成你仓库里真实的生成器构建方式（define_G / 模型类）
======================================
用法：python teardown_observe.py
"""
import os, torch, numpy as np
from PIL import Image
import torch.nn as nn
import torch.nn.functional as F

# ───────────────────────────── TODO ─────────────────────────────
CKPT_PATH = "/path/to/latest_net_G.pth"     # generator 权重
DATA_DIR  = "/path/to/he_inputs"            # 放若干 .npy (2,H,W)
OUT_DIR   = "./teardown_out"
N_BLOCKS  = 6
DEVICE    = "cuda" if torch.cuda.is_available() else "cpu"
# ────────────────────────────────────────────────────────────────


# ---------- 1) 构建并加载 netG（改成你仓库的真实方式）----------
# 下面用 CUT 标准 ResnetGenerator 作占位；如你已是这个类可去掉 import。
# from your_repo.models.networks import ResnetGenerator
# netG = ResnetGenerator(input_nc=2, output_nc=3, ngf=64, n_blocks=N_BLOCKS)
netG = None  # TODO: 用你的方式构建
sd = torch.load(CKPT_PATH, map_location=DEVICE)
if isinstance(sd, dict) and "netG" in sd:
    sd = sd["netG"]
if netG is None:
    raise RuntimeError("请在 TODO 处构建 netG，再 load_state_dict")
netG.load_state_dict(sd, strict=False)
netG = netG.module if isinstance(netG, nn.DataParallel) else netG
netG.eval().to(DEVICE)

# ---------- 2) 找瓶颈 6 个 ResBlock（CUT 的 model 是 nn.Sequential）----------
seq = netG.model if hasattr(netG, "model") else netG
b_idx, b_mod = [], []
for i, m in enumerate(seq):
    if m.__class__.__name__ == "ResnetBlock":
        b_idx.append(i); b_mod.append(m)
assert len(b_mod) == N_BLOCKS, f"找到 {len(b_mod)} 个块，期望 {N_BLOCKS}；改 find 逻辑或 N_BLOCKS"
print(f"[ok] 瓶颈块位置 = {b_idx}")

# ---------- 3) 钩子抓每块输出 ----------
taps = {}
def _hook(k):
    def h(_m, _i, o): taps[k] = o.detach()
    return h
for k, m in enumerate(b_mod):
    m.register_forward_hook(_hook(k))

# ---------- 4) 解码器 = 最后一个块之后的所有层 ----------
decoder = seq[b_idx[-1] + 1:]

def decode(t):
    with torch.no_grad():
        return decoder(t)

# ---------- 5) 简易 RGB→H/E（仅当输入是 RGB 且没预处理；建议换 Macenko/Vahadane）----------
def rgb_to_he(rgb):  # rgb:[3,H,W] 0~1 → [2,H,W]
    eps = 1e-6
    od = -torch.log(torch.clamp(rgb, eps, 1.0))
    M = torch.tensor([[0.65,0.70,0.29],[0.07,0.99,0.11],[0.27,0.57,0.78]],
                     device=od.device, dtype=od.dtype)
    he = torch.linalg.solve(M.T, od.reshape(3, -1)).reshape(3, *od.shape[1:])
    return he[:2]

def sharpness(t):  # 梯度幅值代理：越大越“有结构/锐利”
    t = t.mean(0)  # [C,H,W] → 灰度
    gx = (t[:, 1:] - t[:, :-1]).abs().mean()
    gy = (t[1:] - t[:-1]).abs().mean()
    return float(gx + gy)

# ---------- 6) 跑样本 + 存 montage ----------
os.makedirs(OUT_DIR, exist_ok=True)
files = sorted(f for f in os.listdir(DATA_DIR) if f.endswith(".npy"))
assert files, "DATA_DIR 里没有 .npy"
for f in files[:8]:
    arr = np.load(os.path.join(DATA_DIR, f)).astype(np.float32)
    if arr.shape[0] != 2 and arr.shape[-1] == 2:
        arr = np.transpose(arr, (2, 0, 1))
    if arr.shape[0] == 3:
        print(f"[warn] {f} 是 RGB，用占位 Beer-Lambert 分离（建议改 Macenko）")
        arr = rgb_to_he(torch.from_numpy(arr)).numpy()
    x = torch.from_numpy(arr).unsqueeze(0).to(DEVICE)
    taps.clear()
    with torch.no_grad():
        netG(x)                       # 触发钩子
    row, sharp = [arr], []
    for k in range(len(b_mod)):
        y = decode(taps[k])[0].cpu().numpy()
        row.append(y); sharp.append(sharpness(torch.from_numpy(y)))
    save_montage(row, os.path.join(OUT_DIR, f.replace(".npy", ".png")),
                 titles=["H/E"] + [f"tap{k+1}" for k in range(len(b_mod))])
    print(f"{f}: 各块锐度(代理)= {np.round(sharp, 4)}")

def save_montage(row, path, titles=()):
    imgs = []
    for t in row:
        t = np.clip(t, 0, 1)
        if t.shape[0] == 2:
            t = np.concatenate([t, t[:1] * 0], 0)   # 2→3 仅显示
        if t.shape[0] == 1:
            t = np.repeat(t, 3, 0)
        imgs.append((t * 255).astype("uint8").transpose(1, 2, 0))
    H = max(i.shape[0] for i in imgs); W = sum(i.shape[1] for i in imgs)
    canvas = np.zeros((H, W, 3), "uint8"); x0 = 0
    for i in imgs:
        canvas[:i.shape[0], x0:x0+i.shape[1]] = i; x0 += i.shape[1]
    Image.fromarray(canvas).save(path)

print("done →", OUT_DIR)
