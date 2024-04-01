from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import config as cf
import os,pickle,telebot, sys, easyocr

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
    try:
        procesados.index(entrada.get_property('href'))
        return
    except:
        pass
    print(entrada.get_property('href'))
    imagen_url=entrada.find_element(By.TAG_NAME,'img').get_property('src')
    print(imagen_url)
    driver.get(imagen_url)
    driver.save_screenshot('img.png')
    result = reader.readtext('img.png')
    print(result)
    cadena=""
    for r in result:
        cadena+=f'<code>{r[-2]}</code>\n'
    cadena+='<a href="https://forocoches.com/codigo/">Enlace registro</a>'
    procesados.append(entrada.get_property('href'))
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
    while(loop):
        try:
            driver = webdriver.Chrome(options=options)
            # preproceso de la web
            login(driver)

            for enlace in driver.find_elements(By.TAG_NAME, "a"):
                try:
                    if (enlace.get_property('href').startswith('https://www.instagram.com/forocoches/p/')):
                        procesa_entrada(driver, enlace)
                        break
                except Exception as e:
                    print(e)
                    pass
            driver.quit()
        except:
            pass
        #si hay parametro 1 en linea de comandos se sale
        try:
            sys.argv.index('-1')
            return
        except:
            pass
        # esperar 30 segundos hasta siguiente ciclo
        sleep(cf.espera_entre_ciclos)


if __name__ == '__main__':
    main()