import io
import matplotlib.pyplot as plt

import mplfinance as mpf
import pandas as pd


def daily(data, title, ylabel):
    if data == None:
        return None

    times = []
    values = []

    for item in data:
        time, value = item
        times.append(time.strftime("%H:%M"))
        values.append(value)

    blue = (86/255, 186/255, 250/255)

    plt.figure(facecolor=(24/255, 37/255, 51/255))
    plt.grid(color=(24/255, 37/255, 51/255), linestyle='-')

    plt.title(title, color=blue, fontsize=25, style='italic', fontfamily='fantasy')
    plt.xlabel('Date', color=blue, fontsize=15, fontfamily='fantasy')
    plt.ylabel(ylabel, color=blue, fontsize=15, fontfamily='fantasy')

    ax = plt.gca()
    ax.set_facecolor((24/255, 37/255, 51/255))
    ax.spines["bottom"].set_color(blue)
    ax.spines["top"].set_color(blue)
    ax.spines["left"].set_color(blue)
    ax.spines["right"].set_color(blue)
    ax.tick_params(axis="x", colors=blue, rotation=45)
    ax.tick_params(axis="y", colors=blue)


    plt.margins(x=0, y=0.15, tight=True)

    for i in range(len(data)-1):
        mini = float(min(values))
        if values[i] > values[i+1]:
            plt.fill_between([times[i], times[i+1]], [values[i], values[i+1]], y2=mini-mini*0.25, color="r", alpha=0.2)
        else:
            plt.fill_between([times[i], times[i+1]], [values[i], values[i+1]], y2=mini-mini*0.25, color="g", alpha=0.2)

    plt.plot(times, values, color=(86/255, 186/255, 250/255))

    img_buf = io.BytesIO()
    img_buf.name = 'image.png'
    
    plt.savefig(img_buf, format='png')
    plt.close()
    
    img_buf.seek(0)
    return img_buf

def weekly(data, title, ylabel):
    if data == None:
        return None
    
    times = []
    values = []

    for item in data:
        time, value = item[:2]
        times.append(time.strftime("%d.%m %H:00"))
        values.append(value)

    blue = (86/255, 186/255, 250/255)

    plt.figure(facecolor=(24/255, 37/255, 51/255))
    plt.grid(color=(24/255, 37/255, 51/255), linestyle='-')

    plt.title(title, color=blue, fontsize=25, style='italic', fontfamily='fantasy')
    plt.xlabel('Date', color=blue, fontsize=15, fontfamily='fantasy')
    plt.ylabel(ylabel, color=blue, fontsize=15, fontfamily='fantasy')

    ax = plt.gca()
    ax.set_facecolor((24/255, 37/255, 51/255))
    ax.spines["bottom"].set_color(blue)
    ax.spines["top"].set_color(blue)
    ax.spines["left"].set_color(blue)
    ax.spines["right"].set_color(blue)
    ax.tick_params(axis="x", colors=blue, rotation=20)
    ax.tick_params(axis="y", colors=blue)


    plt.margins(x=0, y=0.15, tight=True)

    for i in range(len(data)-1):
        mini = float(min(values))
        if values[i] > values[i+1]:
            plt.fill_between([times[i], times[i+1]], [values[i], values[i+1]], y2=mini-mini*0.25, color="r", alpha=0.2)
        else:
            plt.fill_between([times[i], times[i+1]], [values[i], values[i+1]], y2=mini-mini*0.25, color="g", alpha=0.2)

    plt.plot(times, values, color=(86/255, 186/255, 250/255))

    img_buf = io.BytesIO()
    img_buf.name = 'image.png'
    
    plt.savefig(img_buf, format='png')
    plt.close()
    
    img_buf.seek(0)
    return img_buf