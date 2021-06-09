import RPi.GPIO as GPIO
import time
import telepot
from picamera import PiCamera
from telepot.loop import MessageLoop


#사진 저장시 중복 하지 않도록 하기위한 변수
 
i=0

#시스템, 메서지, 모터를 컨트롤 하기 위한 변수
controller =0
motocontroller =0
messagecontroller =0



def pro(i,msg):
     GPIO.output(LED, True) #방불을 켜주고
     time.sleep(1)

     i=i+1
     camera.start_preview() #카메라 준비
     time.sleep(1)
     camera.capture('/home/pi/sourceCode/Newer/image%s.jpg' %i) #카메라 찍기
     time.sleep(1)
     GPIO.output(LED, False)# 불을 끄고
     camera.stop_preview() #카메라도 끔
     messageCheck(messagecontroller,telegram_id,msg)
     return i
     
     
def messageCheck(messagecontroller,telegram_id,msg):
    if messagecontroller == 0: #메세지를 받기를 원하면
         bot.sendMessage(chat_id = telegram_id, text = msg) #메세지 보내주기
         return 1


def handle(msg):
    global controller    # 전역변수로 선언
    global messagecontroller
    content_type, chat_type, chat_id = telepot.glance(msg)    #telepot의 glance 메소드 사용해서 값을 받아옴
   
    if content_type == 'text':
        if msg['text'].upper() == 'ON':           #텔레그램에서 on이라는 값받으면
            controller = 1                        #controller를 1로 바꾸고
            bot.sendMessage(chat_id, 'System On') #사용자에서 system on이라고 메세지를 보냄
        elif msg['text'].upper() == 'OFF':
            controller = 0
            bot.sendMessage(chat_id, 'System Off')
        elif msg['text'].upper() == 'MESSAGE OFF':
            messagecontroller = 1
            bot.sendMessage(chat_id, 'MESSAGE OFF')
        elif msg['text'].upper() == 'MESSAGE ON':
            messagecontroller = 0
            bot.sendMessage(chat_id, 'MESSAGE ON') 
        elif msg['text'] == '/start':
            pass
        else:
            bot.sendMessage(chat_id, '지원하지 않는 기능입니다')


TOKEN = ''    # 텔레그램으로부터 받은 Bot API 토큰
telegram_id = ''   #텔레그램 bot_get의 id 값
bot = telepot.Bot(TOKEN)     #텔레그램 bot 토근값을 매개변수로 해서 생성
MessageLoop(bot, handle).run_as_thread()  #봇을 쓰레드로 run



#파이 카메라 생성
camera = PiCamera()

#GPIO 번호 지정
LED = 26
PIR = 6
RR = 20
JODO =24
MOTO = 18
FIRE = 22


#GPIO SETUP
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(PIR, GPIO.IN)
GPIO.setup(FIRE, GPIO.IN)
GPIO.setup(RR, GPIO.OUT)
GPIO.setup(JODO, GPIO.OUT)
GPIO.setup(MOTO, GPIO.OUT)
p = GPIO.PWM(MOTO, 50)




try:

    while True:
        if GPIO.input(FIRE)==0:    #만약 불꽃센서가 감지되고
            if motocontroller ==0: #모터컨트롤러가 0 이면 실행
                time.sleep(1)
                p.start(0)
                p.ChangeDutyCycle(11.5) #모터 각도 조절
                time.sleep(5)
                p.ChangeDutyCycle(7)
                motocontroller=1 #모터 컨트롤러를 1로 바꾸어서 모터가 1번만 돌아가게함(물이 없는데 돌아가면 안되기 때문에.)
                messageCheck(messagecontroller,telegram_id,"집에 불남")
                
                    
        #조도 센서와 레이저 센서
        if controller == 1:    #컨트롤러가 1이면 보안모드 상태
            GPIO.output(RR, True) #레이저 센서 ON   
            GPIO.output(JODO,GPIO.LOW) #어둠의 정도가 낮으면 즉 밝으면 이라는 뜻 - 조도 센서의 값을 LOW로 초기화
            time.sleep(0.1)
            GPIO.setup(JODO, GPIO.IN) #조도 센서를 GPIO.IN으로 해서 현재 받고 있는 빛을 받음
            if GPIO.input(JODO)!=GPIO.LOW:   #어둠의 정도가 낮지않으면 즉 어두우면
                i=pro(i,'레이저 센서 감지')
            GPIO.setup(JODO, GPIO.OUT) #조도센서를 다시 OUT으로 하여 값을 초기화 가능하게 함

            
        
# 적외선 센서 
        if controller == 1:
            if GPIO.input(PIR)!=0:
                i=pro(i,'적외선 센서 감지')
                
                
                   
                
      
        
except KeyboardInterrupt:
    p.stop()
    GPIO.output(RR, False)
    GPIO.output(LED, False)
    GPIO.cleanup()
