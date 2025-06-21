from kivy.clock import Clock
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.properties import ObjectProperty,NumericProperty,StringProperty
from kivy.graphics import RenderContext
from requests import get
from threading import Thread
import asyncio

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return






class ReactButton(Button):
	image_base = ObjectProperty()
	type = ''
	def __init__(self, **kwargs):
		super(ReactButton, self).__init__(**kwargs)
		
	def on_press(self):
		print(self.acceptResponse())
		twrv = ThreadWithReturnValue(target=self.SetImage)
		twrv.start()
		response = twrv.join()
		self.image_base.source = f"http://localhost:2348/img?doc_id={response}"
		self.image_base.doc_id = self.image_base.source.split('?doc_id=')[-1]



	def acceptResponse(self):
		headers = {
		'Connection': 'keep-alive',
		'Cache-Control': 'max-age=0',
		'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
		'sec-ch-ua-mobile': '?0',
		'sec-ch-ua-platform': '"Windows"',
		'Upgrade-Insecure-Requests': '1',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'Sec-Fetch-Site': 'none',
		'Sec-Fetch-Mode': 'navigate',
		'Sec-Fetch-User': '?1',
		'Sec-Fetch-Dest': 'document',
		'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh;q=0.5',
		}

		params = (
		('doc_id', self.image_base.doc_id),
		('response', self.type),
		)

		response = get('http://localhost:2348/response', headers=headers, params=params)
		return response.url
	def SetImage(self):
		headers = {
		'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
		'sec-ch-ua-mobile': '?0',
		'sec-ch-ua-platform': '"Windows"',
		'Upgrade-Insecure-Requests': '1',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
		}
		return get('http://localhost:2348/next', headers=headers).json()['doc_id']
		


class MainImage(AsyncImage):
	doc_id = StringProperty()
	def __init__(self, **kwargs):
		super(MainImage, self).__init__(**kwargs)
		twrv = ThreadWithReturnValue(target=self.SetImage)
		twrv.start()
		response = twrv.join()
		self.source = f"http://localhost:2348/img?doc_id={response}"
		self.doc_id = self.source.split('?doc_id=')[-1]
		print(self.doc_id)


	def acceptResponse(self):
		headers = {
		'Connection': 'keep-alive',
		'Cache-Control': 'max-age=0',
		'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
		'sec-ch-ua-mobile': '?0',
		'sec-ch-ua-platform': '"Windows"',
		'Upgrade-Insecure-Requests': '1',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'Sec-Fetch-Site': 'none',
		'Sec-Fetch-Mode': 'navigate',
		'Sec-Fetch-User': '?1',
		'Sec-Fetch-Dest': 'document',
		'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh;q=0.5',
		}

		params = (
		('doc_id', self.image_base.doc_id),
		('response', self.type),
		)

		response = get('http://localhost:2348/response', headers=headers, params=params)
		return response.url
	def SetImage(self):
		headers = {
		'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
		'sec-ch-ua-mobile': '?0',
		'sec-ch-ua-platform': '"Windows"',
		'Upgrade-Insecure-Requests': '1',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
		}
		return get('http://localhost:2348/next', headers=headers).json()['doc_id']


kv = """
BoxLayout:
	orientation:'horizontal'
	MainImage:
		id:main_image
		source:''
	BoxLayout:
		orientation:'vertical'
		ReactButton:
			image_base:main_image
			type: "RES_NEGATIVE"
			text:'(N)egative'
		ReactButton:
			image_base:main_image
			type: "RES_FINE"
			text:'(O)k'
		ReactButton:
			image_base:main_image
			type: "RES_BETTER"
			text:'(H)as Value'
		ReactButton:
			image_base:main_image
			type: "RES_MORE"
			text:'(M)ore'
		ReactButton:
			image_base:main_image
			type: "RES_WOW"
			text:'(G)ood'
		ReactButton:
			image_base:main_image
			type: "RES_SAVE"
			text:'(S)tar'
		
"""


class BluredBackgroundApp(App):
	def build(self):
		return Builder.load_string(kv)

async def main():
	BluredBackgroundApp().run()

if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
