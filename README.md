#Microgear-python
=======
microgear- python คือ client library ภาษา Python  ที่ทำหน้าที่เป็นตัวกลางในการเชื่อมโยง application code หรือ hardware เข้ากับบริการของ netpie platform เพื่อการพัฒนา IOT application รายละเอียดเกี่ยวกับ netpie platform สามารถศึกษาได้จาก http://netpie.io



##การติดตั้ง
-----------
pip install microgear



##ตัวอย่างการเรียกใช้งาน
-----------
```python
import microgear.client as microgear
import time

gearkey = <gearkey>
gearsecret =  <gearsecret>
appid = <appid>

microgear.create(gearkey,gearsecret,appid)

def connection():
	print "Now I am connected with netpie"

def subscription(topic,message):
	microgear.chat("htmlgear","Hello world. "+str(int(time.time())))
	print topic+" "+message

microgear.setname("python")
microgear.on_connect(connection)
microgear.on_subscribe("python",subscription)

microgear.connect()
```



##การใช้งาน library
------------
**microgear.create(*gearkey*,*gearsecret*,*appid*):**

arguments

 * *gearkey* `string` - เป็น key สำหรับ gear ที่จะรัน ใช้ในการอ้างอิงตัวตนของ gear
 * *gearsecret* `string` - เป็น secret ของ key ซึ่งจะใช้ประกอบในกระบวนการยืนยันตัวตน
 * *appid* `string` - กลุ่มของ application ที่ microgear จะทำการเชื่อมต่อ

```python:
microgear.create("qDDwMaHEXfBiXmL","vNoswuhfqjxWSm0GR7cycGPniekw03","piedemo")
```




##Microgear
---------------

**microgear.connect():** การเชื่อมต่อ microgear

```python:
microgear.connect();
```







**microgear.setname(*gearname*):** microgear สามารถตั้งชื่อตัวเองได้ ซึ่งสามารถใช้เป็นชื่อเรียกในการใช้ฟังก์ชั่น chat()

argument

* *gearname* `string` - ชื่อของ microgear นี้








```python:
microgear.setname("python");
```

**microgear.chat(*gearname*, *message*):** การส่งข้อความโดยระบุ gearname และข้อความที่ต้องการส่ง

arguments

* *gearname* `string` - ชื่อของ microgear นี้
* *message* `string` – ข้อความ

```python:
microgear.chat("html","hello from python");
```


<br data-effect="nomal"/>




**microgear.publish(*topic*, *message*):** ในการณีที่ต้องการส่งข้อความแบบไม่เจาะจงผู้รับ สามารถใช้ฟังชั่น publish ไปยัง topic ที่กำหนดได้ ซึ่งจะมีแต่ microgear ที่ subscribe topoic นี้เท่านั้น ที่จะได้รับข้อความ

arguments

* *topic* `string` - ชื่อของ topic ที่ต้องการจะส่งข้อความไปถึง
* *message* `string` – ข้อความ

```python:
microgear.publish("/outdoor/temp","28.5");
```

<br data-effect="nomal"/>


**microgear.subscribe(*topic*)** microgear อาจจะมีความสนใจใน topic ใดเป็นการเฉพาะ เราสามารถใช้ฟังก์ชั่น subscribe() ในการบอกรับ message ของ topic นั้นได้

argument

* *topic* `string` - ชื่อของ topic ที่ความสนใจ



```python:
microgear.subscribe("/outdoor/temp");
```

<br data-effect="nomal"/>

##Event
---------------
application ที่รันบน microgear จะมีการทำงานในแบบ event driven คือเป็นการทำงานตอบสนองต่อ event ต่างๆ ด้วยการเขียน callback function ขึ้นมารองรับในลักษณะๆดังต่อไปนี้

**microgear.on_connect(*callback*)**

argument

* *callback* `function` - callback function


```python:
def callback_connect() :
	print “Now I am connected with netpie”
microgear.on_ connect (callback_connect)
```

<br data-effect="nomal"/>


**microgear.on_subscribe(*topic*, *callback*)**

arguments

* *topic* `string` - ชื่อของ topic ที่ความสนใจ
* *callback* `function` - callback function


```python:
def callback_subscribe(topic,message) :
	print topic+ “ “ +message
microgear.on_subscribe(topic, callback_subscribe)
```

<br data-effect="nomal"/>


**microgear.on_disconnect(*callback*)**

argument


* *callback* `function` - callback function


```python:
def callback_disconnect() :
	pritnt "Disconnected”
microgear.on_ disconnect (callback_disconnect)

```

<br data-effect="nomal"/>