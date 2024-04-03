from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import config as cf
import os,pickle,telebot, sys, easyocr, datetime

tb = telebot.TeleBot(cf.telegram_key)
reader = easyocr.Reader(['es', 'en'])

# cargamos la lista de urls procesadas
procesados=[]
if (os.path.isfile('procesados.pkl')):
    try:
        with open('procesados.pkl', 'rb') as fp:
            procesados=pickle.load(fp)
            print('Cargados los enlaces ya procesados de procesados.pkl')
    except:
        print("Error al cargar procesados.pkl")


def login(driver):
    # entramos en la web
    driver.get('https://www.instagram.com/forocoches/?hl=es')
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "button")))
    # sleep(2)
    #aceptamos los terminos y condiciones
    accept_terms_button = driver.find_elements(By.TAG_NAME,"button")
    for button in accept_terms_button:
        if (button.text=='Permitir todas las cookies'):
            button.send_keys(Keys.RETURN)
            return

def procesa_entrada(driver,entrada):
    url=entrada.get_property('href')
    try:
        procesados.index(url)
        return
    except:
        pass
    print(url)
    imagen_url=entrada.find_element(By.TAG_NAME,'img').get_property('src')
    print(imagen_url)
    driver.switch_to.new_window('tab')
    driver.get(imagen_url)
    driver.save_screenshot('img.png')
    driver.close()
    result = reader.readtext('img.png')
    print(result)
    cadena=""
    for r in result:
        cadena+=f'<code>{r[-2]}</code>\n'
    cadena+='<a href="https://forocoches.com/codigo/">Enlace registro</a>'
    procesados.append(url)
    with open('procesados.pkl', 'wb') as fp:
        pickle.dump(procesados, fp)
    tb.send_photo(cf.telegram_userid, imagen_url, caption=cadena, parse_mode='HTML')

def main():
    options = webdriver.ChromeOptions()
    # si hay parametro -nh se NO abre en modo headless
    try:
        sys.argv.index('-nh')
    except:
        options.add_argument('--headless=new')
    loop=True
    driver = webdriver.Chrome(options=options)
    login(driver)
    while(loop):
        try:
            for enlace in driver.find_elements(By.TAG_NAME, "a"):
                try:
                    if (enlace.get_property('href').startswith('https://www.instagram.com/forocoches/p/')):
                        procesa_entrada(driver, enlace)
                        break
                except Exception as e:
                    print(e)
                    pass
        except:
            pass
        #si hay parametro 1 en linea de comandos se sale
        try:
            sys.argv.index('-1')
            driver.quit()
            return
        except:
            pass
        # esperar hasta siguiente ciclo
        print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} Esperando {cf.espera_entre_ciclos} segundos hasta siguiente ciclo')
        sleep(cf.espera_entre_ciclos)
        driver.refresh()
        print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} Recargando la pagina')
        sleep(5)


if __name__ == '__main__':
    main()
