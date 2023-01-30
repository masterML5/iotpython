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
LED_PIN_RED = 21
LED_PIN_GREEN = 16
BUZZER_PIN = 26
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
GPIO.setup(LED_PIN_RED, GPIO.OUT)
GPIO.setup(LED_PIN_GREEN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

try:
  while True:
    lcd.clear()
    lcd.message = 'Skeniraj karticu'
    id, text = reader.read()

    cursor.execute("Select id, name FROM users WHERE aktivan AND vazeci AND rfid_uid="+str(id))
    result = cursor.fetchone()
    lcd.clear()

    if cursor.rowcount >= 1:
      lcd.message = "Dobrodosli \n" + result[1]
      cursor.execute("INSERT INTO attendance (user_id) VALUES (%s)", (result[0],) )
      
      GPIO.output(LED_PIN_GREEN, GPIO.HIGH)
      GPIO.output(BUZZER_PIN, GPIO.HIGH)
      time.sleep(0.15)
      GPIO.output(BUZZER_PIN, GPIO.LOW)
      time.sleep(1.5)
      GPIO.output(LED_PIN_GREEN, GPIO.LOW)
     
      db.commit()
    else:
      lcd.message = "Ne postoji \nkorisnik."
      GPIO.output(LED_PIN_RED, GPIO.HIGH)
      GPIO.output(BUZZER_PIN, GPIO.HIGH)
      time.sleep(0.9)
      GPIO.output(BUZZER_PIN, GPIO.LOW)
      time.sleep(1.5)
      GPIO.output(LED_PIN_RED, GPIO.LOW)
      
    time.sleep(1)
finally:
  GPIO.cleanup()
 
