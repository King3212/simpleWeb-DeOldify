#NOTE:  This must be the first call in order to work properly!
from deoldify import device
from deoldify.device_id import DeviceId
#choices:  CPU, GPU0...GPU7
device.set(device=DeviceId.GPU0)

from deoldify.visualize import *
plt.style.use('dark_background')
torch.backends.cudnn.benchmark=True
import warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*?Your .*? set is empty.*?")

def color(path):
    colorizer = get_image_colorizer(artistic=True)
    #NOTE:  Max is 45 with 11GB video cards. 35 is a good default
    render_factor=35
    print("colorPath:"+path)
    source_path = path
    result_path = colorizer.plot_transformed_image(path=source_path, render_factor=render_factor, compare=True)
    return result_path
    
def color_video(path):
    colorizer = get_video_colorizer()
    #NOTE:  Max is 44 with 11GB video cards.  21 is a good default
    render_factor=21
    source_path = path
    print("coloring")
    result_path = colorizer.colorize_from_file_name(source_path, render_factor=render_factor)
    print("finish")
    return result_path

