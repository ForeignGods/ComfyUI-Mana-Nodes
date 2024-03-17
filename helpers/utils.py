import sys
import torch
import numpy as np
import subprocess
from PIL import Image
from torch.nn.functional import pad

# Tensor to PIL
def tensor2pil(image):
    return Image.fromarray(np.clip(255.0 * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))


# Convert PIL to Tensor
def pil2tensor(image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

def ensure_opencv():
    if "python_embeded" in sys.executable or "python_embedded" in sys.executable:
        pip_install = [sys.executable, "-s", "-m", "pip", "install"]
    else:
        pip_install = [sys.executable, "-m", "pip", "install"]

    try:
        import cv2
    except Exception as e:
        try:
            subprocess.check_call(pip_install + ['opencv-python'])
        except:
            print('failed import cv2')

def stack_audio_tensors(tensors, mode="pad"):
    # assert all(len(x.shape) == 2 for x in tensors)
    sizes = [x.shape[-1] for x in tensors]

    if mode in {"pad_l", "pad_r", "pad"}:
        # pad input tensors to be equal length
        dst_size = max(sizes)
        stack_tensors = (
            [pad(x, pad=(0, dst_size - x.shape[-1])) for x in tensors]
            if mode == "pad_r"
            else [pad(x, pad=(dst_size - x.shape[-1], 0)) for x in tensors]
        )
    elif mode in {"trunc_l", "trunc_r", "trunc"}:
        # truncate input tensors to be equal length
        dst_size = min(sizes)
        stack_tensors = (
            [x[:, x.shape[-1] - dst_size:] for x in tensors]
            if mode == "trunc_r"
            else [x[:, :dst_size] for x in tensors]
        )
    else:
        assert False, 'unknown mode "{pad}"'

    return torch.stack(stack_tensors)