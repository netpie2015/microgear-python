#Microgear-python
-----------
microgear- python คือ client library ภาษา Python  ที่ทำหน้าที่เป็นตัวกลางในการเชื่อมโยง application code หรือ hardware เข้ากับบริการของ netpie platform เพื่อการพัฒนา IOT application รายละเอียดเกี่ยวกับ netpie platform สามารถศึกษาได้จาก http://netpie.io



##การติดตั้ง
-----------
```sh
$ pip install microgear
```


##ตัวอย่างการเรียกใช้งาน
-----------
```python
import microgear.client as microgear
import time

appid = <appid>
gearkey = <gearkey>
gearsecret =  <gearsecret>

microgear.create(gearkey,gearsecret,appid,{'debugmode': True})

def connection():
  print "Now I am connected with netpie"

def subscription(topic,message):
  print topic+" "+message

def disconnect():
  print "disconnect is work"

microgear.setalias("doraemon")
microgear.on_connect = connection
microgear.on_message = subscription
microgear.on_disconnect = disconnect
microgear.subscribe("/mails")
microgear.connect(True)

```
[ตัวอย่างเพิ่มเติม](https://github.com/netpieio/microgear-python/wiki#%E0%B8%95%E0%B8%B1%E0%B8%A7%E0%B8%AD%E0%B8%A2%E0%B9%88%E0%B8%B2%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B9%83%E0%B8%8A%E0%B9%89%E0%B8%87%E0%B8%B2%E0%B8%99)


##การใช้งาน library
------------
###Microgear
---------------
**client.create(*gearkey*,*gearsecret*,*appid*,*args*):**

arguments

 * *gearkey* `string` - เป็น key สำหรับ gear ที่จะรัน ใช้ในการอ้างอิงตัวตนของ gear
 * *gearsecret* `string` - เป็น secret ของ key ซึ่งจะใช้ประกอบในกระบวนการยืนยันตัวตน
 * *appid* `string` - กลุ่มของ application ที่ microgear จะทำการเชื่อมต่อ
 * *args* `dictionary` - เป็นการตั้งค่าเพิ่มเติม สำหรับ microgear ได้แก่
   * *debugmode* `boolean` - แสดงข้อความในโหมด debug
   * *scope* `string` - กำหนด scope ให้กับ microgear เพื่อให้/จำกัดสิทธิ์บางอย่าง โดยมีรูปแบบดังนี้
       * [r][w]:&lt;/topic/path&gt; - r และ w คือสิทธิ์ในการ publish ละ subscribe topic ดังที่ระบุ เช่น rw:/outdoor/temp
       *  name:&lt;gearname&gt; - คือสิทธิ์ในการตั้งชื่อตัวเองว่า &lt;gearname&gt;
       *  chat:&lt;gearname&gt; - คือสิทธ์ในการ chat กับ &lt;gearname&gt;
   * *alias* string - กำหนดชื่อเรียกสำหรับ microgear นี้ โดยจะปรากฎที่หน้า key management และสามารถเป็นชื่อที่ microgear ตัวอื่นใช้สำหรับ `chat()` ได้

ในขั้นตอนของการสร้าง key บนเว็บ netpie.io นักพัฒนาสามารถกำหนดสิทธิ์ขั้นพื้นฐานให้แต่ละ key ได้อยู่แล้ว หากการ create microgear อยู่ภายใต้ขอบเขตของสิทธิ์ที่มี token จะถูกจ่ายอัตโนมัติ และ microgear จะสามารถเชื่อมต่อ netpie platform ได้ทันที แต่หาก scope ที่ร้องขอนั้นมากเกินกว่าสิทธิ์ที่กำหนดไว้ นักพัฒนาจะได้รับ notification ให้พิจารณาอนุมัติ microgear ที่เข้ามาขอเชื่อมต่อ ข้อควรระวัง หาก microgear มีการกระทำการเกินกว่าสิทธิ์ที่ได้รับไป เช่น พยายามจะ publish ไปยัง topic ที่ตัวเองไม่มีสิทธิ์ netpie จะตัดการเชื่อมต่อของ microgear โดยอัตโนมัติ ในกรณีที่ใช้ APPKEY เป็น gearkey เราสามารถละเว้น attribute นี้ได้ เพราะ APPKEY จะได้สิทธิ์ทุกอย่างในฐานะของเจ้าของ app โดย default อยู่แล้ว 


```python
gearkey = <gearkey>
gearsecret =  <gearsecret>
appid = <appid>

client.create(gearkey,gearsecret,appid, {'debugmode': True, 'scope': "r:/outdoor/temp,w:/outdoor/valve,name:logger,chat:plant", 'alias': "logger"})
```




**client.connect(*will_block*):** การเชื่อมต่อ microgear

argument

* *will_block* `boolean` - `(optional)` ระบุรูปแบบการเชื่อมต่อ ว่าให้มีการ Block หลังจากเรียกฟังก์ชั่น หรือไม่ ซึ่งจะมีค่า default เป็น `False`  โดยโปรแกรมจะทำงานในบรรทัดถัดไปหลังจากที่ทำการ connect แล้ว ซึ่งจะทำให้ ผู้พัฒนาสามารถ เขียนโปรแกรม ในการติดต่อกับ platfrom ต่อไปได้ โดยการเชื่อมต่อกับ platform จะคงอยู่ เท่าที่มีการทำงานของโปรแกรม เช่น

```python
client.connect()
while True:
    client.chat("doraemon","Hello world. "+str(int(time.time())))
    time.sleep(2)
```
หากต้องการให้ library ทำการ Block หลังจากทำการ connect แล้ว ซึ่งหลังจาก connect แล้วโปรแกรมหยุดอยู่ที่การทำงานร่วมกับ platform โดยจะทำงานตามที่มี เหตุการณ์ callback (on_*) ที่ถูกกำหนดไว้ก่อนหน้า โดยสามารถระบุ พารามิเตอร์เป็น `True` ได้ เช่น
```python
client.connect(True)
```




**client.setalias(*alias*):** กำหนดชื่อเรียกสำหรับ microgear นี้ โดยจะปรากฎที่หน้า key management และสามารถเป็นชื่อที่ microgear ตัวอื่นใช้สำหรับ `chat()` ได้

argument

* *alias* `string` - ชื่อของ microgear นี้



```python
client.setalias("python");
```

**client.setname(*gearname*):** microgear สามารถตั้งชื่อตัวเองได้
ซึ่งสามารถใช้เป็นชื่อเรียกในการใช้ฟังก์ชั่น chat() **แนะนำให้ใช้ `setalias()` แทน**

argument

* *gearname* `string` - ชื่อของ microgear นี้



```python
client.setname("python");
```

**client.chat(*gearname*, *message*):** การส่งข้อความโดยระบุ gearname และข้อความที่ต้องการส่ง

arguments

* *gearname* `string` - ชื่อของ microgear นี้
* *message* `string` – ข้อความ

```python
client.chat("html","hello from python");
```







**client.publish(*topic*, *message*, *retain*):** ในกรณีที่ต้องการส่งข้อความแบบไม่เจาะจงผู้รับ สามารถใช้ฟังชั่น publish ไปยัง topic ที่กำหนดได้ ซึ่งจะมีแต่ microgear ที่ subscribe topoic นี้เท่านั้น ที่จะได้รับข้อความ

arguments

* *topic* `string` - ชื่อของ topic ที่ต้องการจะส่งข้อความไปถึง
* *message* `string` – ข้อความ
* *args* `dictionary` - เป็นการตั้งค่าเพิ่มเติม สำหรับการ publish ได้แก่
  * *retain* `boolean` - ระบุค่า `True` ถ้าต้องการเก็บข้อความไว้ หากมีการ subscribe topic นี้ก็จะได้รับข้อความนี้อีก ค่าปริยายเป็น `False` หากไม่ระบุ และถ้าต้องการลบข้อความที่บันทึกไว้ให้ส่งข้อความ "" ซึ่งมีความยาวเป็น 0 เพื่อล้างค่าข้อความที่ไว้ทึกไว้

```python
client.publish("/outdoor/temp","28.5");
client.publish("/outdoor/temp","28.5",{'retain':True});
```




**client.subscribe(*topic*)** microgear อาจจะมีความสนใจใน topic
ใดเป็นการเฉพาะ เราสามารถใช้ฟังก์ชั่น subscribe() ในการบอกรับ message ของ topic นั้นได้

argument

* *topic* `string` - ชื่อของ topic ที่ความสนใจ โดยขึ้นต้นด้วยเครื่องหมาย "/" 



```python
client.subscribe("/temp");
```

**client.resettoken()** สำหรับต้องการลบ Token ที่มีอยู่ ซึ่งจะทำการลบ Token ที่อยู่ภายใน cache และบน platform เมื่อลบแล้ว จำเป็นจะต้องขอ Token ใหม่ทุกครั้ง

```python
client.resettoken();
```



###Event
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

**client.on_warning** เป็น event ที่เกิดมีเหตุการณ์บางอย่างเกิดขึ้นขึ้น และมีการเตือนให้ทราบ

ค่าที่ set


* *callback* `function` - จะทำงานเมื่อเกิดเหตุการณ์นี้ โดยจะรับค่า parameter คือ
    * *msg* - ระบุข้อความ ที่เกี่ยวข้องกับเหตุการณ์นี้


```python
def callback_warning(msg) :
	print msg
client.on_warning = callback_warning

```

**client.on_info** เป็น event ที่เกิดมีเหตุการณ์บางอย่างเกิดขึ้นขึ้นภายใน microgear

ค่าที่ set


* *callback* `function` - จะทำงานเมื่อเกิดเหตุการณ์นี้ โดยจะรับค่า parameter คือ
    * *msg* - ระบุข้อความ ที่เกี่ยวข้องกับเหตุการณ์นี้


```python
def callback_info(msg) :
	print msg
client.on_info = callback_info

```

**client.on_error** event นี้จะเกิดขึ้นเมื่อมี error

ค่าที่ set


* *callback* `function` - จะทำงานเมื่อเกิดเหตุการณ์นี้ โดยจะรับค่า parameter คือ
    * *msg* - ระบุ error ที่เกี่ยวข้องกับเหตุการณ์นี้


```python
def callback_error(msg) :
	print msg
client.on_error = callback_error

```
