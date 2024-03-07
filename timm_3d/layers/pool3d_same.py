""" AvgPool3d w/ Same Padding

Hacked together by / Copyright 2020 Ross Wightman
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple, Optional

from .helpers import to_3tuple
from .padding import pad_same, get_padding_value


def avg_pool3d_same(x, kernel_size: List[int], stride: List[int], padding: List[int] = (0, 0),
                    ceil_mode: bool = False, count_include_pad: bool = True):
    # FIXME how to deal with count_include_pad vs not for external padding?
    x = pad_same(x, kernel_size, stride)
    return F.avg_pool3d(x, kernel_size, stride, (0, 0), ceil_mode, count_include_pad)


class AvgPool3dSame(nn.AvgPool3d):
    """ Tensorflow like 'SAME' wrapper for 2D average pooling
    """
    def __init__(self, kernel_size: int, stride=None, padding=0, ceil_mode=False, count_include_pad=True):
        kernel_size = to_3tuple(kernel_size)
        stride = to_3tuple(stride)
        super(AvgPool3dSame, self).__init__(kernel_size, stride, (0, 0, 0), ceil_mode, count_include_pad)

    def forward(self, x):
        x = pad_same(x, self.kernel_size, self.stride)
        return F.avg_pool3d(
            x, self.kernel_size, self.stride, self.padding, self.ceil_mode, self.count_include_pad)


def max_pool2d_same(
        x, kernel_size: List[int], stride: List[int], padding: List[int] = (0, 0),
        dilation: List[int] = (1, 1), ceil_mode: bool = False):
    x = pad_same(x, kernel_size, stride, value=-float('inf'))
    return F.max_pool2d(x, kernel_size, stride, (0, 0), dilation, ceil_mode)


class MaxPool3dSame(nn.MaxPool3d):
    """ Tensorflow like 'SAME' wrapper for 3D max pooling
    """
    def __init__(self, kernel_size: int, stride=None, padding=0, dilation=1, ceil_mode=False):
        kernel_size = to_3tuple(kernel_size)
        stride = to_3tuple(stride)
        dilation = to_3tuple(dilation)
        super(MaxPool3dSame, self).__init__(kernel_size, stride, (0, 0), dilation, ceil_mode)

    def forward(self, x):
        x = pad_same(x, self.kernel_size, self.stride, value=-float('inf'))
        return F.max_pool3d(x, self.kernel_size, self.stride, (0, 0), self.dilation, self.ceil_mode)


def create_pool3d(pool_type, kernel_size, stride=None, **kwargs):
    stride = stride or kernel_size
    padding = kwargs.pop('padding', '')
    padding, is_dynamic = get_padding_value(padding, kernel_size, stride=stride, **kwargs)
    if is_dynamic:
        if pool_type == 'avg':
            return AvgPool3dSame(kernel_size, stride=stride, **kwargs)
        elif pool_type == 'max':
            return MaxPool3dSame(kernel_size, stride=stride, **kwargs)
        else:
            assert False, f'Unsupported pool type {pool_type}'
    else:
        if pool_type == 'avg':
            return nn.AvgPool3d(kernel_size, stride=stride, padding=padding, **kwargs)
        elif pool_type == 'max':
            return nn.MaxPool3d(kernel_size, stride=stride, padding=padding, **kwargs)
        else:
            assert False, f'Unsupported pool type {pool_type}'
