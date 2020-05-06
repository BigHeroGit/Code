# coding = utf-8
import kivy
from kivy.app import App
kivy.Config.set('graphics', 'multisamples', '0')
kivy.require('1.10.1')

from kivy.uix.boxlayout import BoxLayout

class TelaPrincipal(BoxLayout):
    pass

class Init(App):
    def build(self):
        self.title = 'Big Hero - Process Analyzer'
        return TelaPrincipal()

if __name__ == '__main__':
    window = Init()

    window.run()
