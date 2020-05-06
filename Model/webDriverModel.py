from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver


class Chrome(webdriver.Chrome):

    def validar(self,element,todosElementos):
        if todosElementos:
            return element
        if len(element):
            return element[0]
        return False

    def find_element_by_id(self, id_,todosElementos=False):
        element=super().find_elements_by_id(id_=id_)
        return self.validar(element=element,todosElementos=todosElementos)

    def find_element_by_xpath(self, xpath,todosElementos=False):
        element=super().find_elements_by_xpath(xpath=xpath)
        return self.validar(element=element,todosElementos=todosElementos)

    def find_element_by_link_text(self, link_text,todosElementos=False):
        element=super().find_elements_by_link_text(link_text=link_text)
        return self.validar(element=element,todosElementos=todosElementos)

    def find_element_by_partial_link_text(self, link_text,todosElementos=False):
        element=super().find_elements_by_partial_link_text(link_text=link_text)
        return self.validar(element=element,todosElementos=todosElementos)

    def find_element_by_name(self, name,todosElementos=False):
        element=super().find_elements_by_name(name=name)
        return self.validar(element=element,todosElementos=todosElementos)

    def find_element_by_tag_name(self, name,todosElementos=False):
        element=super().find_elements_by_tag_name(name=name)
        return self.validar(element=element,todosElementos=todosElementos)

    def find_element_by_class_name(self, name,todosElementos=False):
        element=super().find_elements_by_class_name(name=name)
        return self.validar(element=element,todosElementos=todosElementos)

    def find_element_by_css_selector(self, css_selector,todosElementos=False):
        element=super().find_elements_by_css_selector(css_selector=css_selector)
        return self.validar(element=element,todosElementos=todosElementos)

