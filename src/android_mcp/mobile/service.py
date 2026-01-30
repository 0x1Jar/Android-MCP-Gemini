from android_mcp.mobile.views import MobileState
from android_mcp.tree.service import Tree
import uiautomator2 as u2
from io import BytesIO
from PIL import Image
import base64

class Mobile:
    def __init__(self,device:str=None):
        self.device_serial = device
        self.device = None
        try:
            self.connect()
        except Exception:
            pass

    def connect(self):
        try:
            self.device = u2.connect(self.device_serial)
            self.device.info
        except u2.ConnectError as e:
            raise ConnectionError(f"Failed to connect to device {self.device_serial}: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error connecting to device {self.device_serial}: {e}")

    def get_device(self):
        if self.device is None:
            self.connect()
        return self.device

    def shell(self, command: str) -> str:
        """Executes a shell command on the device."""
        try:
            output, exit_code = self.get_device().shell(command, stream=False)
            if exit_code != 0:
                 raise RuntimeError(f"Shell command failed with exit code {exit_code}: {output}")
            return output
        except Exception as e:
            raise RuntimeError(f"Failed to execute shell command: {e}")

    def push_file(self, src: str, dst: str):
        """Pushes a file from the local machine to the device."""
        try:
            self.get_device().push(src, dst)
        except Exception as e:
            raise RuntimeError(f"Failed to push file: {e}")

    def get_state(self,use_vision=False,as_bytes:bool=False,as_base64:bool=False):
        try:
            tree = Tree(self)
            tree_state = tree.get_state()
            if use_vision:
                nodes=tree_state.interactive_elements
                annotated_screenshot=tree.annotated_screenshot(nodes=nodes,scale=1.0)
                if as_base64:
                    screenshot=self.as_base64(annotated_screenshot)
                elif as_bytes:
                    screenshot=self.screenshot_in_bytes(annotated_screenshot)
                else:
                    screenshot=annotated_screenshot
            else:
                screenshot=None
            return MobileState(tree_state=tree_state,screenshot=screenshot)
        except Exception as e:
            raise RuntimeError(f"Failed to get device state: {e}")
    
    def get_screenshot(self,scale:float=0.7)->Image.Image:
        try:
            screenshot=self.get_device().screenshot()
            if screenshot is None:
                raise ValueError("Screenshot capture returned None.")
            size=(screenshot.width*scale, screenshot.height*scale)
            screenshot.thumbnail(size=size, resample=Image.Resampling.LANCZOS)
            return screenshot
        except Exception as e:
            raise RuntimeError(f"Failed to get screenshot: {e}")
    
    def screenshot_in_bytes(self,screenshot:Image.Image)->bytes:
        try:
            if screenshot is None:
                raise ValueError("Screenshot is None")
            io=BytesIO()
            screenshot.save(io,format='PNG')
            bytes=io.getvalue()
            if len(bytes) == 0:
                raise ValueError("Screenshot conversion resulted in empty bytes.")
            return bytes
        except Exception as e:
            raise RuntimeError(f"Failed to convert screenshot to bytes: {e}")

    def as_base64(self,screenshot:Image.Image)->str:
        try:
            if screenshot is None:
                raise ValueError("Screenshot is None")
            io=BytesIO()
            screenshot.save(io,format='PNG')
            bytes=io.getvalue()
            if len(bytes) == 0:
                raise ValueError("Screenshot conversion resulted in empty bytes.")
            return base64.b64encode(bytes).decode('utf-8')
        except Exception as e:
            raise RuntimeError(f"Failed to convert screenshot to base64: {e}")

    