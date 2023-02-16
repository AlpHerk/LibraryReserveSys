from library.consts import LOCAL_PATH, JIAN_PATH, PATH_PAIR1, PATH_PAIR2
from config.config import webdav_usr, webdav_pwd 
from webdav4.client import Client

url = "https://dav.jianguoyun.com/dav/"

class WebDavCookies():

    def up_cookies(path_pair=PATH_PAIR1):
        try:
            client = Client(base_url=url, auth=(webdav_usr, webdav_pwd))
            client.upload_file(from_path=path_pair[0], to_path=path_pair[1], overwrite=True)
            return True
        except:
            return False

    def down_cookies(path_pair=PATH_PAIR1):
        try:
            client = Client(base_url=url, auth=(webdav_usr, webdav_pwd))
            client.download_file(from_path=path_pair[1], to_path=path_pair[0])
            return True
        except:
            return False