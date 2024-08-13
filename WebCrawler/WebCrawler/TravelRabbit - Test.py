# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 12:23:27 2021

@author: dermo
"""
import shlex
import shutil
import os
import sys
import traceback
import time
import datetime
import uuid
import math
import requests
from io import StringIO
import pandas as pd
import numpy as np
import pyodbc
from selenium import webdriver
import Service.PublicFun as PublicFun
import Service.SettingReader as SettingReader
import Service.SpiderHandler as SpiderHandler
from selenium.webdriver.common.action_chains import ActionChains
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import Service.SQLConnect as SQLConnect

from shapely.geometry import Polygon
import numpy as np

# 定义多边形对象
coordinates = [[121.559147, 25.209356], [121.582303, 25.193635], [121.576989, 25.169828], 
                [121.606978, 25.128952], [121.59521, 25.11368], [121.628236, 25.085381], 
                [121.615709, 25.06382], [121.646078, 25.028783], [121.59521, 25.005875], 
                [121.600525, 24.960058], [121.561045, 24.96455], [121.52688, 24.989704], 
                [121.519667, 25.018452], [121.493095, 25.009019], [121.486261, 25.032377], 
                [121.506761, 25.06921], [121.4874, 25.09706], [121.457791, 25.106493], 
                [121.465003, 25.130749], [121.501446, 25.16893], [121.559147, 25.209356]]
polygon = Polygon(coordinates)

# 定义掃描间距
step = 0.1

# 将多边形分解为线段
lines = []
for i in range(len(coordinates)):
    p1, p2 = coordinates[i], coordinates[(i+1)%len(coordinates)]
    if p1[1] == p2[1]:
        # 水平线段
        ymin, ymax = sorted([p1[1], p2[1]])
        for x in np.arange(p1[0], p2[0], step):
            lines.append(((x, ymin), (x, ymax)))
    elif p1[0] == p2[0]:
        # 垂直线段
        xmin, xmax = sorted([p1[0], p2[0]])
        for y in np.arange(p1[1], p2[1], step):
            lines.append(((xmin, y), (xmax, y)))

# 在水平线段上计算交点
intersections = []
for y in np.arange(polygon.bounds[1], polygon.bounds[3], step):
    line_segments = []
    for line in lines:
        p1, p2 = line
        if p1[1] <= y < p2[1] or p2[1] <= y < p1[1]:
            x = (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1]) + p1[0]
            line_segments.append(x)
    line_segments.sort()
    intersections.extend(list(zip(line_segments[::2], [y]*len(line_segments[::2]))))


    # 在垂直线段上计算交点
for x in np.arange(polygon.bounds[0], polygon.bounds[2], step):
    line_segments = []
    for line in lines:
        p1, p2 = line
        if p1[0] <= x < p2[0] or p2[0] <= x < p1[0]:
            y = (x - p1[0]) * (p2[1] - p1[1]) / (p2[0] - p1[0]) + p1[1]
            line_segments.append(y)
    line_segments.sort()
    intersections.extend(list(zip([x]*len(line_segments[::2]), line_segments[::2])))

# 输出交点
for intersection in intersections:
    print(intersection)
