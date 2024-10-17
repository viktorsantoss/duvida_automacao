import undetected_chromedriver as uc
import urllib3
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
#from selenium_stealth import stealth
#InvalidElementStateException
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException, InvalidElementStateException, UnexpectedAlertPresentException,ElementClickInterceptedException
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from pathlib import Path
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from twocaptcha import TwoCaptcha
import re
import pandas as pd
from time import sleep


class Automacao:

    def __init__(self, cpf, chave_api):
        self._url = 'https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PF/EmitirPGFN'
        self._navegador  = None
        self.caminho_pasta = Path.cwd()
        self.cpf = cpf
        self.api_key = chave_api


    def ir_para_pagina(self):
        options = uc.ChromeOptions()

        options.add_argument('start-maximized')  # Inicializa com a tela cheia
        # options.add_argument('--headless')  # Inicializa sem mostrar o navegador. Fica invisível
        # options.add_argument('--headless')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36')
        prefs = {
            "download.default_directory": str(self.caminho_pasta),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
            'profile.default_content_setting_values.automatic_downloads': 1
        }
        options.add_experimental_option('prefs', prefs)

        self._navegador = uc.Chrome(options=options)
        self._navegador.maximize_window()

        for i in range(4):
            try:
                self._navegador.get(self._url)
            except Exception as e:
                if isinstance(e, (
                        urllib3.exceptions.MaxRetryError, ConnectionError, ConnectionRefusedError, TimeoutException)):
                    sleep(10)
                    self._navegador.get(self._url)
            else:
                break

    def esperar_pagina_carregar(self):
        for _ in range(4):
            try:
                WebDriverWait(self._navegador, 10).until(EC.visibility_of_element_located((By.ID, 'NI')))
            except TimeoutException:
                continue
            else:
                sleep(1)
                break

    def preencher_cpf(self):
        campo_cpf_cnpj = self._navegador.find_element(By.ID, 'NI')
        campo_cpf_cnpj.send_keys(self.cpf)


    def resolver_captch(self):
        solver = TwoCaptcha(self.api_key)

        site_key = self._navegador.find_element(By.CLASS_NAME, 'h-captcha').get_attribute('data-sitekey')
        id_captcha = self._navegador.find_element(By.TAG_NAME, 'textarea').get_attribute('id')
        print(id_captcha)
        for _ in range(10):
            response = solver.hcaptcha(sitekey=site_key, url=self._url)
            code = response['code']
            if code:
                print(code)
                self._navegador.execute_script(f'document.getElementById("{id_captcha}").value="{code}";')
                break

    def clicar_botao_consulta(self):
        botao = self._navegador.find_element(By.ID, 'validar')
        botao.click()


    def realizar_consulta(self):
        try:
            self.ir_para_pagina()
            self.esperar_pagina_carregar()
            self.preencher_cpf()
            self.resolver_captch()
            self.clicar_botao_consulta()
        except Exception as e:
            print(e)
        finally:
            self._navegador.quit()


if __name__ == '__main__':
    valor_cpf = ''
    api_key = ''

    c = Automacao(valor_cpf, api_key)
    c.realizar_consulta()
  