import numpy as np
from scipy.stats import rankdata
import subprocess
import logging
import os

def checkPath(path):
    if not os.path.exists(path):
        os.mkdir(path)
    return

def cal_ranks(scores, labels, filters):
    target_ids = np.nonzero(labels)
    target_preds = scores[target_ids]
    target_batchs = target_ids[0]
    ranks = []
    for i in range(len(target_preds)):
        pred = scores[target_batchs[i]]
        mask = 1-filters[target_batchs[i]]
        pos_pred = target_preds[i]
        rank = np.sum((pred >= pos_pred) * mask) + 1
        ranks.append(rank)
    return ranks

def cal_performance(ranks):
    mrr = (1. / ranks).sum() / len(ranks)
    h_1 = sum(ranks<=1) * 1.0 / len(ranks)
    h_3 = sum(ranks <= 3) * 1.0 / len(ranks)
    h_10 = sum(ranks<=10) * 1.0 / len(ranks)
    return mrr, h_1, h_3, h_10

def select_gpu():
    nvidia_info = subprocess.run('nvidia-smi', stdout=subprocess.PIPE)
    gpu_info = False
    gpu_info_line = 0
    proc_info = False
    gpu_mem = []
    gpu_occupied = set()
    i = 0
    for line in nvidia_info.stdout.split(b'\n'):
        line = line.decode().strip()
        if gpu_info:
            gpu_info_line += 1
            if line == '':
                gpu_info = False
                continue
            if gpu_info_line % 3 == 2:
                mem_info = line.split('|')[2]
                used_mem_mb = int(mem_info.strip().split()[0][:-3])
                gpu_mem.append(used_mem_mb)
        if proc_info:
            if line == '|  No running processes found                                                 |':
                continue
            if line == '+-----------------------------------------------------------------------------+':
                proc_info = False
                continue
            proc_gpu = int(line.split()[1])
            #proc_type = line.split()[3]
            gpu_occupied.add(proc_gpu)
        if line == '|===============================+======================+======================|':
            gpu_info = True
        if line == '|=============================================================================|':
            proc_info = True
        i += 1
    for i in range(0,len(gpu_mem)):
        if i not in gpu_occupied:
            logging.info('Automatically selected GPU %d because it is vacant.', i)
            return i
    for i in range(0,len(gpu_mem)):
        if gpu_mem[i] == min(gpu_mem):
            logging.info('All GPUs are occupied. Automatically selected GPU %d because it has the most free memory.', i)
            return i

def uniqueWithoutSort(a):
    indexes = np.unique(a, return_index=True)[1]
    res = [a[index] for index in sorted(indexes)]
    return res