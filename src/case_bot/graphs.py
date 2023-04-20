import io
import matplotlib.pyplot as plt

import db.currencies

import mplfinance as mpf
import pandas as pd


def get_daily(data, title, ylabel):
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
    
    font = 'sans-serif'

    plt.title(title, color=blue, fontsize=25, fontfamily=font)
    plt.xlabel('Date', color=blue, fontsize=15, fontfamily=font)
    plt.ylabel(ylabel, color=blue, fontsize=15, fontfamily=font)

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

def get_weekly(data, title, ylabel):
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

    font = 'sans-serif'

    plt.title(title, color=blue, fontsize=25, fontfamily=font)
    plt.xlabel('Date', color=blue, fontsize=15, fontfamily=font)
    plt.ylabel(ylabel, color=blue, fontsize=15, fontfamily=font)

    ax = plt.gca()
    ax.set_facecolor((24/255, 37/255, 51/255))
    ax.spines["bottom"].set_color(blue)
    ax.spines["top"].set_color(blue)
    ax.spines["left"].set_color(blue)
    ax.spines["right"].set_color(blue)
    ax.tick_params(axis="x", colors=blue, rotation=23)
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

def handler(data, cur_id, graph_value, graph_time, item_name=None):
    cur_symbol = db.currencies.get_symbol(cur_id)
    
    if cur_id != 1:
        data = data_to_cur(data, cur_id)
    
    if graph_value == 'item':
        title = f'The price of {item_name} ({graph_time})'
        ylabel = f'Price ({cur_symbol})'
    elif graph_value == 'asset':
        title = f'The price of your assets ({graph_time})'
        ylabel = f'Assets ({cur_symbol})'
    
    if graph_time == '24h':
        new_graph = get_daily(data, title, ylabel)
    elif graph_time in ['7d', '30d']:
        new_graph = get_weekly(data, title, ylabel)
    
    return new_graph

def data_to_cur(data, cur_id):
    rate = db.currencies.get_rate(cur_id)
    data = [(item[0], item[1]*rate) for item in data]
    return data