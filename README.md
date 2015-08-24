#Microgear-python
-----------
microgear- python คือ client library ภาษา Python  ที่ทำหน้าที่เป็นตัวกลางในการเชื่อมโยง application code หรือ hardware เข้ากับบริการของ netpie platform เพื่อการพัฒนา IOT application รายละเอียดเกี่ยวกับ netpie platform สามารถศึกษาได้จาก http://netpie.io



##การติดตั้ง
-----------
pip install microgear



##ตัวอย่างการเรียกใช้งาน
-----------
```python
import microgear.client as client
import time

gearkey = <gearkey>
gearsecret =  <gearsecret>
appid = <appid>

microgear.create(gearkey,gearsecret,appid,{'debugmode': True})

def connection():
	print "Now I am connected with netpie"

def subscription(topic,message):
	client.chat("nobita","Hello world. "+str(int(time.time())))
	print topic+" "+message

client.setname("doraemon")
client.on_connect = connection
client.on_message = subscription
client.subscribe("/mails")

client.connect()
```



##การใช้งาน library
------------
**microgear.create(*gearkey*,*gearsecret*,*appid*):**

arguments

 * *gearkey* `string` - เป็น key สำหรับ gear ที่จะรัน ใช้ในการอ้างอิงตัวตนของ gear
 * *gearsecret* `string` - เป็น secret ของ key ซึ่งจะใช้ประกอบในกระบวนการยืนยันตัวตน
 * *appid* `string` - กลุ่มของ application ที่ microgear จะทำการเชื่อมต่อ

```python
gearkey = <gearkey>
gearsecret =  <gearsecret>
appid = <appid>

microgear.create(gearkey,gearsecret,appid)
```




##Microgear
---------------

**microgear.connect():** การเชื่อมต่อ microgear

```python
microgear.connect();
```







**microgear.setname(*gearname*):** microgear สามารถตั้งชื่อตัวเองได้
ซึ่งสามารถใช้เป็นชื่อเรียกในการใช้ฟังก์ชั่น chat()

argument

* *gearname* `string` - ชื่อของ microgear นี้



```python
microgear.setname("python");
```

**microgear.chat(*gearname*, *message*):** การส่งข้อความโดยระบุ gearname และข้อความที่ต้องการส่ง

arguments

* *gearname* `string` - ชื่อของ microgear นี้
* *message* `string` – ข้อความ

```python
microgear.chat("html","hello from python");
```







**microgear.publish(*topic*, *message*):** ในกรณีที่ต้องการส่งข้อความแบบไม่เจาะจงผู้รับ สามารถใช้ฟังชั่น publish ไปยัง topic ที่กำหนดได้ ซึ่งจะมีแต่ microgear ที่ subscribe topoic นี้เท่านั้น ที่จะได้รับข้อความ

arguments

* *topic* `string` - ชื่อของ topic ที่ต้องการจะส่งข้อความไปถึง
* *message* `string` – ข้อความ

```python
microgear.publish("/outdoor/temp","28.5");
```




**microgear.subscribe(*topic*)** microgear อาจจะมีความสนใจใน topic
ใดเป็นการเฉพาะ เราสามารถใช้ฟังก์ชั่น subscribe() ในการบอกรับ message ของ topic นั้นได้

argument

* *topic* `string` - ชื่อของ topic ที่ความสนใจ



```python
microgear.subscribe("/outdoor/temp");
```



##Event
---------------
application ที่รันบน microgear จะมีการทำงานในแบบ event driven คือเป็นการทำงานตอบสนองต่อ event ต่างๆ ด้วยการเขียน callback function ขึ้นมารองรับในลักษณะๆดังต่อไปนี้

**client.on_connect**  เกิดขึ้นเมื่อ microgear library เชื่อมต่อกับ platform สำเร็จ

ค่าที่ set

* *callback* `function` - ฟังก์ชั่นที่จะทำงาน เมื่อมีการ connect


```python
def callback_connect() :
	print "Now I am connected with netpie"
client.on_ connect = callback_connect
```




**client.on_disconnect** เกิดขึ้นเมื่อ microgear library ตัดการเชื่อมต่อกับ platform

ค่าที่ set


* *callback* `function` - callback function


```python
def callback_disconnect() :
	print "Disconnected”
client.on_disconnect = callback_disconnect

```




**client.on_message** เกิดขึ้นเมื่อ ได้รับข้อความจากการ chat หรือ หัวข้อที่ subscribe

ค่าที่ set
* *callback* `function` - ฟังก์ชั่น ที่จะทำงานเมื่อได้รับข้อความ โดยฟังก์ชั่นนี้จะรับ parameter 2 ตัวคือ
    * *topic* - ชื่อ topic ที่ได้รับข้อความนี้
    * *message* - ข้อความที่ได้รับ


```python
def callback_message(topic, message) :
  print "I got message from ", topic, ": ", message
client.on_message= callback_message

```


**client.on_present** event นี้จะเกิดขึ้นเมื่อมี microgear ใน appid เดียวกัน online เข้ามาเชื่อมต่อ netpie

ค่าที่ set


* *callback* `function` - จะทำงานเมื่อเกิดเหตุการณ์นี้ โดยจะรับค่า parameter คือ
     * *gearkey* - ระบุค่าของ gearkey ที่เกี่ยวข้องกับเหตุการณ์นี้


```python
def callback_present(gearkey) :
	print gearkey+" become online."
client.on_present = callback_present

```




**client.on_present** event นี้จะเกิดขึ้นเมื่อมี microgear ใน appid เดียวกัน offline หายไป

ค่าที่ set


* *callback* `function` - จะทำงานเมื่อเกิดเหตุการณ์นี้ โดยจะรับค่า parameter คือ
    * *gearkey* - ระบุค่าของ gearkey ที่เกี่ยวข้องกับเหตุการณ์นี้


```python
def callback_absent(gearkey) :
	print gearkey+" become offline."
client.on_absent = callback_absent

```