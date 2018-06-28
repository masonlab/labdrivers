import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure()
ax1 = fig.add_subplot(111)

# set up the independent variable
x = np.array([])

for i in np.linspace(0, 5*np.pi, 100):
  # update data
  x = np.append(x, i)
  y = np.sin(x)
  
  # clear the plot of lines already plotted
  ax1.clear()

  # update the plot
  plt.plot(x,y)
  plt.draw()
  
  # no need to pause, but helps so you can see real-time plots
  plt.pause(0.1)
