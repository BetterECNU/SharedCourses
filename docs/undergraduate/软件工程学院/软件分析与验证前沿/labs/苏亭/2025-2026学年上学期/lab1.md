---
title: lab1
---

:::info
本次实验作为第一次实验, 只需要跟着实验手册一步步做就行.  
由于实验结果可能有个体差异性, 所以在此不提供个人作业
:::

1. 运行 `make all`
2. 打开 `answers.txt` 和 `c_programs` 里面的十份源码
3. 挨个阅读源码, 脑测一下是否会出现 `division by zero` 错误, 如果会的话, 就在 `ground truth` 列填 `right`; 反之填写 `wrong`
4. 这个时候你的 `make all` 应该运行完了, 没有的话等它运行完
5. 打开 `results`, 里面有 `afl_logs` 和 `csa_logs`
   1. 对于 `afl_logs`, 我们查看 `afl_logs/test{n}/afl_output/crashes` 中是否有文件, 如果有, 说明对于 `test{n}`, afl 检测到了 `division by zero` 错误, 那么我们在对应的 `AFL` 列填写 `reject`; 反之, 填写 `accept`
   2. 对于 `csa_logs`, 我们挨个查看 `test{n}_out.txt`, 并在每个之中查找字符串 `Division by zero`, 如果查找到了, 说明对于 `test{n}`, csa 检测到了 `division by zero` 错误, 那么我们在对应的 `CSA` 列填写 `reject`; 反之, 填写 `accept`
6. 根据刚刚填写的内容计算 `AFL` 和 `CSA` 列的 `Precision`, `Recall` 和 `F1 score`
   1. Precision: 准确率, 即不误报, 即对于所有检测结果为 `Reject` 的行里 `Ground Truth` 为 `wrong` 的比例
   2. Recall: 召回率, 即不漏报, 即对于所有 `Ground Truth` 为 `wrong` 的行, 检测结果为 `Reject` 的比例
   3. F1 score: 计算公式:
   $$
   F1 =  \frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}
   $$
7. 回答下方的问题
   1. 第 1, 2 题中的 sound 对应 Precision, complete 对应 Recall, 根据自己的运行结果回答即可
   2. 讨论 `CSA` 的 `accuracy` 和 `cost` 的时候要关注它的性质——静态分析工具
