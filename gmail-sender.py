#Log de actualizaciones.....
#20120911 - Agrego posibilidad de parametros para cuentas, mail y listas. Agrego mensajes de error.
#20130118 - Agrego posibilidad de parametro de servidor para distintas cuentas.
#End Log

import sys
import smtplib 
import mimetypes
import email.mime.text
from time import sleep
#from email.MIMEText import MIMEText
#import email.encoders.encode_base64
#from email.Encoders import encode_base64

############# CONFIGURACION ################
de="Flash Pack S.R.L."
maxporcuenta=490
indicecuenta=0
tiempo_entre_mails=8
############################################


########################################### NO TOCAR DEBAJO DE ESTA LINEA ########################
if len(sys.argv)<5:
	print("El formato de uso debe ser el siguiente")
	print("%s <archivo_de_cuentas> <archivo_de_mails> <html_mail_enviar> 'Asunto'" % (sys.argv[0]))
	print("Ejemplo: %s c:\cuentas.txt c:\listamails.txt c:\mail.html" % (sys.argv[0]))
	exit()

asunto=sys.argv[4]
archivocuentas=sys.argv[1]
mails=sys.argv[2]
cuentas=[]
mailserver=""
contador=0
errores=0
indicecuenta=0
cantidadcuentas=0
mailServer=smtplib.SMTP


def conectar(user,passwd,servidor):
	try:
		# Conexion al server
		print("Conectando a %s" % servidor)
		mailServer = smtplib.SMTP(servidor[0:-1],587)
		# Se recorta un caracter al final del servidor por que llega con "\n"

		mailServer.ehlo()
		mailServer.starttls()
		mailServer.ehlo()
		print("Logueando como %s : %s" % (user,passwd))
		mailServer.login(user,passwd)
		return mailServer
	except BaseException as e:
		print("\n")
		print("ERROR "*10)
		print("No se pudo conectar a %s@%s:%s al servidor: %s" % (user,servidor,passwd,e))
		print("ERROR "*10)
		print("\n")
		exit()
		siguienteCuenta()


# Cargado de cuentas
def cargarCuentas():
	global cuentas
	global cantidadcuentas
	print ("Cargando cuentas")
	f = open(archivocuentas, "r")
	for linea in f.readlines():
		cuentas.append(linea.split("\t"))
	cantidadcuentas=len(cuentas)
	print("Cantidad de cuentas cargadas: %s " % cantidadcuentas)
	conectarCuenta()

# Avanzador de cuentas
def siguienteCuenta():
	global indicecuenta
	print("Cambiando a siguiente cuenta")
	print("Cuenta actual: %s" % indicecuenta)
	if indicecuenta>=cantidadcuentas-1:
		print("Cuentas finalizadas. Reiniciando contador")		
		indicecuenta=0
	else:
		print("Pasando a siguiente cuenta")
		indicecuenta=indicecuenta+1		
	print("Nueva cuenta: %s" % indicecuenta)
	print("Direccion %s" % cuentas[indicecuenta][0])
	conectarCuenta()
	

def conectarCuenta():
	global contador
	global mailServer
	global cuentas
	print("Conectando a %s" % cuentas[indicecuenta][0])
	try:
		# Conexion al server
		mailServer=conectar(cuentas[indicecuenta][1],cuentas[indicecuenta][2],cuentas[indicecuenta][3])
		contador=0
	except BaseException as e:
		print("\n")
		print("ERROR "*10)
		print("No se ha podido conectar a la cuenta %s. Error : %s" % (cuentas[indicecuenta][0],e))
		print("ERROR "*10)
		print("\n")
		print("Intentando seguir...")
		siguienteCuenta()


cargarCuentas()

# Lectura de mensaje
mail=""
f=open(sys.argv[3])

for l in f.readlines():
	mail+=l

# Contador de mails enviados
f = open(mails, "r")
for linea in f.readlines():
	contador=contador+1
	if contador>maxporcuenta:
		print("Maximo de envios alcanzado %s" % cuentas[indicecuenta][0])
		siguienteCuenta()

	# Armado del mail
	mensaje = email.mime.text.MIMEText(mail,'html')
	mensaje['Subject']=asunto
	mensaje['From']="%s <%s>" % (de,cuentas[indicecuenta][0])
	mensaje['To']= linea

	print("Enviando a %s desde %s" % (linea,cuentas[indicecuenta][0]))
	print("Contador %s" % contador)
	try:
		mailServer.sendmail(de, linea, mensaje.as_string())
		errores=0
	except BaseException as e:
		print("\n")
		print("ERROR "*10)
		print("No se ha podido enviar a %s : %s" % (linea,e))
		print("ERROR "*10)
		print("\n")
		errores=errores+1
		if errores>3:
			print("Intentando seguir...")
			siguienteCuenta()

	sleep(tiempo_entre_mails)

mailServer.close()
