import io

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates

import itertools

from modules.heat_index import heat_index

def to_bytes(fig):
    # the bytes IO object
    bio = io.BytesIO()

    # render figure
    fig.savefig(bio, format='png', bbox_inches='tight')

    # back to start of file
    bio.seek(0)

    return bio.getvalue()

def close(fig):
    plt.close(fig)

def temp_history(data):

    fig = plt.figure(figsize=(8,6))

    # dates
    x_data = [ d.date for d in data ]

    #
    # plot temperature diagram
    #

    axis = plt.subplot2grid((3,1), (0,0), fig=fig)
    
    # hide x-axis labels (shared with pressure plot)
    # https://matplotlib.org/stable/gallery/subplots_axes_and_figures/shared_axis_demo.html
    plt.setp(axis.get_xticklabels(), visible=False)

    # format y-axis
    axis.set_ylabel('Temperatur [°C]')

    # plot temperature
    y_data = [ d.temperature for d in data ]
    axis.plot(x_data, y_data, color='red', label='Temperatur')
    
    # plot heat index
    c = 0
    for k,g in itertools.groupby(data, key=lambda d: d.temperature >= 27):
        if not k:
            continue

        g = list(g)
        d_data = [ d.date for d in g ]
        h_data = [ heat_index(d.temperature, d.humidity) for d in g ]

        # plot heat index
        axis.plot(list(d_data), h_data,
            color='tomato',
            alpha=0.6,
            label='Hitzeindex' if c == 0 else None)

        # count number of heat index plots
        c += 1

    # show grid
    axis.grid()

    # show legend if we have heat index plots
    if c > 0:
        axis.legend(loc='upper left', fontsize='small')

    #
    # plot humidity diagram
    #

    axis = plt.subplot2grid((3,1), (1,0), fig=fig)

    # hide x-axis labels
    plt.setp(axis.get_xticklabels(), visible=False)

    # format y-axis
    axis.set_ylabel('Luftfeuchtigkeit [%]')

    # humidity
    y_data = [ d.humidity for d in data ]
    axis.plot(x_data, y_data, color='blue')
    

    # show grid
    axis.grid()

    #
    # plot second diagram
    #

    axis = plt.subplot2grid((3,1), (2,0), fig=fig)

    # format x-axis (time)
    axis.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
    axis.set_xlabel('Uhrzeit')
    
    # format y-axis
    axis.set_ylabel('Luftdruck [hPa]')

    # plot pressure
    y_data = [ d.pressure / 100.0 for d in data ]
    axis.plot(x_data, y_data, color='darkgreen')

    # show grid
    axis.grid()

    return fig
