---
source: DeepSeek
conversation_id: 7509597c-3e3f-4cdf-ab33-a50b2f0993d2
title: scikit-learn交叉验证错误选项判断
inserted_at: 2026-05-22T20:09:40.350000+08:00
updated_at: 2026-05-23T17:59:59.623000+08:00
message_count: 3
---

### THINK

我们被问到："在 scikit-learn 中下列说法错误的是"，选项是A、B、C、D。我们需要找出错误的说法。

回顾scikit-learn中的交叉验证方法：

A. RepeatedKFold 方法可以控制交叉验证的次数； - RepeatedKFold重复K折交叉验证多次，参数n_repeats控制重复次数，所以正确。

B. ShuffleSplit 方法，可以随机的把数据打乱，然后分为训练集和测试集； - ShuffleSplit产生随机排列，然后分割成训练和测试集，确实随机打乱数据。正确。

C. RepeatedStratifiedKFold 在每个重复中以不同的随机化重复 n 次分层的方式划分数据集； - RepeatedStratifiedKFold是重复的分层K折，每个重复中随机化分层划分。正确。

D. LeaveOneOut 方法，当 n 很大的时候，计算量不会很大。 - LeaveOneOut是留一法，对于n个样本，需要训练n次模型，计算量随n线性增长，当n很大时计算量非常大。所以这个说法错误。

因此，错误的是D。

答案：D

### DeepSeek

正确答案是 D。LeaveOneOut 在样本量 n 很大时，需要训练 n 次模型，计算量非常大，因此说法错误。

### 我（提问）

答案

