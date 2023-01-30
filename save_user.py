#!/usr/bin/env python

import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import mysql.connector

import board
import digitalio
import adafruit_character_lcd.character_lcd as character_lcd

db = mysql.connector.connect(
  host="localhost",
  user="test",
  passwd="test123",
  database="iotrfid"
)
LED_PIN_GREEN = 16
LED_PIN_YELLOW = 14
cursor = db.cursor()
reader = SimpleMFRC522()
lcd_rs = digitalio.DigitalInOut(board.D4)
lcd_en = digitalio.DigitalInOut(board.D24)
lcd_d7 = digitalio.DigitalInOut(board.D22)
lcd_d6 = digitalio.DigitalInOut(board.D18)
lcd_d5 = digitalio.DigitalInOut(board.D17)
lcd_d4 = digitalio.DigitalInOut(board.D23)
lcd_backlight = digitalio.DigitalInOut(board.D4)
lcd_columns = 16
lcd_rows = 2
lcd = character_lcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_PIN_YELLOW, GPIO.OUT)
GPIO.setup(LED_PIN_GREEN, GPIO.OUT)
try:
  while True:
    lcd.clear()
    lcd.message ='Postavi karticu\nza registraciju'
    id, text = reader.read()
    cursor.execute("SELECT id FROM users WHERE rfid_uid="+str(id))
    cursor.fetchone()

    if cursor.rowcount >= 1:
      lcd.clear()
      GPIO.output(LED_PIN_YELLOW,GPIO.HIGH)
      lcd.message = "Korisnik vec\npostoji!"
      overwrite = input("Korisnik vec postoji, da li zelite da azurirate ime (Y/N)? ")
      if overwrite[0] == 'Y' or overwrite[0] == 'y':
        lcd.clear()
        GPIO.output(LED_PIN_YELLOW,GPIO.LOW)
        
        lcd.message = "Izmena \nsacuvana."
        #GPIO.output(LED_PIN_GREEN,GPIO.HIGH)
        time.sleep(1)
        #GPIO.output(LED_PIN_GREEN,GPIO.OUT)
        sql_insert = "UPDATE users SET name = %s WHERE rfid_uid=%s"
      else:
        continue;
    else:
      sql_insert = "INSERT INTO users (name, rfid_uid) VALUES (%s, %s)"
    lcd.clear()
    GPIO.output(LED_PIN_YELLOW,GPIO.HIGH)
    lcd.message = 'Unesi ime'
    new_name = input("Ime: ")

    cursor.execute(sql_insert, (new_name, id))

    db.commit()

    lcd.clear()
    GPIO.output(LED_PIN_YELLOW,GPIO.LOW)
    lcd.message = "Sacuvan korisnik\n" + new_name
    print("Korisnik : " + new_name + "\nBroj kartice : " + str(id) + "\nUspesno sacuvan")
    GPIO.output(LED_PIN_GREEN,GPIO.HIGH)
    time.sleep(2)
    GPIO.output(LED_PIN_GREEN,GPIO.OUT)
    
finally:
  GPIO.cleanup()
