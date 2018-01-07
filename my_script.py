

import time
import random
from datetime import datetime
import smtplib
import RPi.GPIO as GPIO

def send_email(text):
	to = 'jenda.specian@seznam.cz'
	user = 'kocici.zachod@seznam.cz'
	passwd = '<Kocicka>'
	try:
		smtpserver = smtplib.SMTP("smtp.seznam.cz",25)
		smtpserver.ehlo()
		smtpserver.starttls()
		smtpserver.ehlo() # extra characters to permit edit
		smtpserver.login(user, passwd)
		header = 'To:' + to + '\n' + 'From: ' + user + '\n' + 'Subject:Upozorneni \n'
		print(header)
		msg = header + '\n ' + text +' \n\n'
		try:
			smtpserver.sendmail(user, to, msg)
			print('Email poslan')
		finally:
			smtpserver.quit()
	except Exception:
		print("Nepovedlo se odeslat email: ")
		print(text)


if __name__ == "__main__":
	print("Ahoj RPI")
	LED = 18		# alias pro port 
	VSTUP = 23		# alias pro vstupni port  - PIR cidlo
	# privedenim logicke hodnity 1 na GPIO24 se ukonci program 
	#- nekonecna smycka do dalsiho restartu
	UKONCENI = 24	# alias pro ukoncovaci pin

	# konstanta, po kolika pruchodech posilat upozorneni
	PO_KOLIKA_PRUCHODECH = 7

	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	GPIO.setup(VSTUP,GPIO.IN)	# vstupni port pro PIR
	GPIO.setup(LED,GPIO.OUT)	# vystupni port pro indikacni LED
	GPIO.setup(UKONCENI,GPIO.IN)	# vstupni port pro ukonceni programu


	GPIO.output(LED,GPIO.LOW) # zhasnuti ledky na zacatku

	pocet_pruchodu = 0	# citani poctu aktivace PIR cidla

	pracovat = True	# navigacni promnna pro cyklus

	# while musi byt ukoncitelny
	while pracovat:

		# ctu stav PIR cidla
		state = GPIO.input(VSTUP)
		if (state == True):

			print("Pruchod")
			print(pocet_pruchodu)

			# rozdvitim indikacni ledku
			GPIO.output(LED, GPIO.HIGH)

			#citam prichody
			pocet_pruchodu = pocet_pruchodu + 1
			if(pocet_pruchodu % PO_KOLIKA_PRUCHODECH == 0):
				print("Vybrat zachod")
				text = "Je potreba vybrat kocici zachod!\n "
				with open("log.txt","r") as file:
					text = text + file.read()
				# vyprazdnim log soubor s casy pruchodu
				open('log.txt', 'w').close()
				#poslani emailu trva
				#2minuty a Led dioda SVITI
				send_email(text)

			#zapis do souboru
			i = datetime.now()
			# 2018/01/06 20:12:18
			# radek se zapiso do log souboru
			radek_pro_zapis = i.strftime('%Y/%m/%d %H:%M:%S')
			print(radek_pro_zapis)
			with open("log.txt","a") as file:
				file.write(radek_pro_zapis + "\n")

			#pro testovani 3s
			time.sleep(3.0) # cekani na dokonceni pouziti zachodu 5min,
		else:
			GPIO.output(LED, GPIO.LOW)

		time.sleep(0.2) # perioda cteni z PIR cidla

		# ctu stav ukoncivaciho vstupu - tlacitka
		state2 = GPIO.input(UKONCENI)
		if (state2 == True):
			pracovat = False
			print("Program skoncil")

	if not pracovat:
		GPIO.output(LED,GPIO.LOW) # zhasnuti indikacni ledky na konci