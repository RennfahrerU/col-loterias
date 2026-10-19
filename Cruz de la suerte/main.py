import kivy
kivy.require('1.0.6')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout

Builder.load_file ('main.kv')

class Test1 (FloatLayout):

    def __init__(self, **kwargs):
        super(Test1, self).__init__(**kwargs)
        self.adicion_r = 0
        self.valor1 = 0
        self.valor2 = 0
        self.valor_r = 0

    def limpiar(self, text):
    	self.ids['input_a'].text = ""
    	self.ids['input_b'].text = ""
    	self.ids['input_c'].text = ""
    	self.ids['input_d'].text = ""
    	self.ids['input_e'].text = ""
    	self.ids['input_f'].text = ""
    	
    pass


    def cerrar(self):
    	exit (MyApp)

    def calculo_1(self):
    	
        try:
            self.valor1 = int(self.ids.input_a.text)
            print(self.valor1)
            self.valor2 = int(self.ids.input_c.text)
            print(self.valor2)
            self.valor_r = int(self.valor1 + self.valor2)
            num = int(self.valor_r)
            self.sumar1(num)

            self.ids['label_9'].text = str(self.adicion_r)
            self.ids['label_17'].text = str(self.adicion_r)

        except ValueError:
            self.ids.label_9.text = 'Fallo fecha'

    def calculo_2(self):
        try:
            self.valor1 = int(self.ids.input_a.text)
            print(self.valor1)
            self.valor2 = int(self.ids.input_d.text)
            print(self.valor2)
            self.valor_r = int(self.valor1 + self.valor2)
            num = int(self.valor_r)
            self.sumar1(num)

            self.ids['label_10'].text = str(self.adicion_r)
            self.ids['label_18'].text = str(self.adicion_r)

        except ValueError:
            self.ids.label_10.text = 'Fallo fecha'

    def calculo_3(self):
        try:
            self.valor1 = int(self.ids.input_a.text)
            print(self.valor1)
            self.valor2 = int(self.ids.input_e.text)
            print(self.valor2)
            self.valor_r = int(self.valor1 + self.valor2)
            num = int(self.valor_r)
            self.sumar1(num)

            self.ids['label_11'].text = str(self.adicion_r)
            self.ids['label_19'].text = str(self.adicion_r)

        except ValueError:
            self.ids.label_11.text = 'Fallo fecha'

    def calculo_4(self):
        try:
            self.valor1 = int(self.ids.input_a.text)
            print(self.valor1)
            self.valor2 = int(self.ids.input_f.text)
            print(self.valor2)
            self.valor_r = int(self.valor1 + self.valor2)
            num = int(self.valor_r)
            self.sumar1(num)

            self.ids['label_12'].text = str(self.adicion_r)
            self.ids['label_20'].text = str(self.adicion_r)

        except ValueError:
            self.ids.label_12.text = 'Fallo fecha'

    def calculo_5(self):
        try:
            self.valor1 = int(self.ids.input_b.text)
            print(self.valor1)
            self.valor2 = int(self.ids.input_c.text)
            print(self.valor2)
            self.valor_r = int(self.valor1 + self.valor2)
            num = int(self.valor_r)
            self.sumar1(num)

            self.ids['label_13'].text = str(self.adicion_r)
            self.ids['label_21'].text = str(self.adicion_r)

        except ValueError:
            self.ids.label_13.text = 'Fallo fecha'

    def calculo_6(self):
        try:
            self.valor1 = int(self.ids.input_b.text)
            print(self.valor1)
            self.valor2 = int(self.ids.input_d.text)
            print(self.valor2)
            self.valor_r = int(self.valor1 + self.valor2)
            num = int(self.valor_r)
            self.sumar1(num)

            self.ids['label_14'].text = str(self.adicion_r)
            self.ids['label_22'].text = str(self.adicion_r)

        except ValueError:
            self.ids.label_14.text = 'Fallo fecha'

    def calculo_7(self):
        try:
            self.valor1 = int(self.ids.input_b.text)
            print(self.valor1)
            self.valor2 = int(self.ids.input_e.text)
            print(self.valor2)
            self.valor_r = int(self.valor1 + self.valor2)
            num = int(self.valor_r)
            self.sumar1(num)

            self.ids['label_15'].text = str(self.adicion_r)
            self.ids['label_23'].text = str(self.adicion_r)

        except ValueError:
            self.ids.label_15.text = 'Fallo fecha'

    def calculo_8(self):
        try:
            self.valor1 = int(self.ids.input_b.text)
            print(self.valor1)
            self.valor2 = int(self.ids.input_f.text)
            print(self.valor2)
            self.valor_r = int(self.valor1 + self.valor2)
            num = int(self.valor_r)
            self.sumar1(num)

            self.ids['label_16'].text = str(self.adicion_r)
            self.ids['label_24'].text = str(self.adicion_r)

        except ValueError:
            self.ids.label_16.text = 'Fallo fecha'

    def sumar1(self, num):
        try:
            while num > 9:
                suma = 0
                while num:
                    suma, num = suma + num % 10, num // 10
                num = suma
                self.adicion_r = num
            else:
                self.adicion_r = num
                return

        except ValueError:
            self.ids.label_41.text = 'fallo, reinicie la APP'

class Drawer(FloatLayout):
    pass

class MyApp (App):
    def build (self):
        return Test1 ()


if __name__ == '__main__':
    MyApp () .run ()
