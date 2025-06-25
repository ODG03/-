from matplotlib import pyplot as plt
import cv2
import numpy as np

filename = "animal.jpg"

orig = cv2.imread(filename)

roi = (2000,500,2500,750)

orig[roi[1]:roi[3],roi[0]:roi[2]] = [0,0,0]

src = cv2.cvtColor(orig,cv2.COLOR_BGR2RGB)
plt.imshow(src)
plt.show()
