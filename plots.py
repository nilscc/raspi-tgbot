import io

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

def to_bytes(fig):
    # the bytes IO object
    bio = io.BytesIO()

    # render figure
    fig.savefig(bio, format='png', bbox_inches='tight')

    # back to start of file
    bio.seek(0)

    return bio.getvalue()

def temp_history(data):
    fig,axis = plt.subplots(figsize=(8,2))

    # dates
    x_data = [ d.date for d in data ]
    
    # temperature
    y_data = [ d.temperature for d in data ]

    axis.plot(x_data, y_data)
    axis.grid()

    # rotate x labels by 45°
    plt.xticks(rotation=45)

    return fig
