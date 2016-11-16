#Microgear-python
-----------
microgear- python is a client library for  Python  The library is used to connect application code or hardware with the NETPIE Platform's service for developing IoT applications. For more details on the NETPIE Platform, please visit https://netpie.io . 



##Installation
-----------
```sh
$ pip install microgear
```


##Usage Example
-----------
```python
import microgear.client as microgear
import logging
import time

appid = <appid>
gearkey = <gearkey>
gearsecret =  <gearsecret>

microgear.create(gearkey,gearsecret,appid,{'debugmode': True})

def connection():
    logging.debug("Now I am connected with netpie")

def subscription(topic,message):
    logging.debug(topic+" "+message)

def disconnect():
    logging.debug("disconnected")

microgear.setalias("doraemon")
microgear.on_connect = connection
microgear.on_message = subscription
microgear.on_disconnect = disconnect
microgear.subscribe("/mails")
microgear.connect(True)

```
[More examples](https://github.com/netpieio/microgear-python/wiki#%E0%B8%95%E0%B8%B1%E0%B8%A7%E0%B8%AD%E0%B8%A2%E0%B9%88%E0%B8%B2%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B9%83%E0%B8%8A%E0%B9%89%E0%B8%87%E0%B8%B2%E0%B8%99)


##Library Usage
------------
###Microgear
---------------
**client.create(*gearkey*,*gearsecret*,*appid*,*args*):**

arguments

 * *gearkey* `string` -  is used as a microgear identity
 * *gearsecret* `string` - comes in a pair with gearkey. The secret is used for authentication and integrity. 
 * *appid* `string` - defines a group of application that microgear is part of
 * *args* `dictionary` - sets additional options for  microgear 
   * *debugmode* `boolean` - show debug messages
   * *scope* `string` -  This can be specified when the microgear needs additional rights beyond default scope. If the scope is specified, it may need an approval from the Application ID's owner for each request. The scope format is the concatenation of strings in the following forms, separated with commas:
      * [r][w]:&lt;/topic/path&gt; - r and w is the right to publish and subscribe topic as specified such as rw:/outdoor/temp
      *  name:&lt;gearname&gt; - is the right to name the &lt;gearname&gt;
      *  chat:&lt;gearname&gt; - is the right to chat with &lt;gearname&gt;
   * *alias* string - defines a name for this microgear. The name will appear on the key management page at the website http://netpie.io.  This name can be use in the `chat()` function.

In the key generation process on the web netpie.io, the developer can specify basic rights to each key. If the creation of microgear is within right scope, a token will be automatically issued, and the microgear can be connected to NETPIE immediately. However, if the requested scope is beyond the specified right, the developer will recieve a notification to approve a microgear's connection. Note that if the microgear has operations beyond its right (e.g., pulishing to the topic that it does not has the right to do so), NETPIE will automatically disconnect the microgear. In case that APPKEY is used as a gearkey, the developer can ignore this attribute since by default the APPKEY will gain all rights as the ownwer of the app.
 

```python
gearkey = <gearkey>
gearsecret =  <gearsecret>
appid = <appid>

client.create(gearkey,gearsecret,appid, {'debugmode': True, 'scope': "r:/outdoor/temp,w:/outdoor/valve,name:logger,chat:plant", 'alias': "logger"})
```




**client.connect(*will_block*):**  microgear connection

argument

* *will_block* `boolean` - `(optional)`specifies connection type whether to block after this function. The default value is `False` so the program will execute the next line after microgear is connected to the platform. For example,

```python
client.connect()
while True:
    client.chat("doraemon","Hello world. "+str(int(time.time())))
    time.sleep(2)
```
If you want the library to Block after being connected to the platform, you could wait for specified events using callback (on_*). In this case, use the argument  `True` for this function. For example,
```python
client.connect(True)
```




**client.setalias(*alias*):** microgear can set its own alias, which to be used for others make a function call chat(). The alias will appear on the key management portal of netpie.io .

argument

* *alias* `string` - name of this microgear 



```python
client.setalias("python");
```

**client.setname(*gearname*):** microgear can set its own name to use with chat() **This function is deprecated. Please use `setalias()` instead**

argument

* *gearname* `string` - name of this microgear



```python
client.setname("python");
```

**client.chat(*gearname*, *message*):** sending a message to a specified gearname 

arguments

* *gearname* `string` - name of microgear to which to send a message. 
* *message* `string` - message to be sent.

```python
client.chat("html","hello from python");
```







**client.publish(*topic*, *message*, *retain*):** In the case that the microgear want to send a message to an unspecified receiver, the developer can use the function publish to the desired topic, which all the microgears that subscribe such topic will receive a message.

arguments

* *topic* `string` - name of topic to be send a message to. 
* *message* `string` - message to be sent.
* *args* `dictionary` - sets additional options for  microgear
  * *retain* `boolean` - retain a message or not (the default is `False`) If `True`, the message is kept.  To remove the retained message, publish an empty message or  "" which is a message with length 0. 

```python
client.publish("/outdoor/temp","28.5");
client.publish("/outdoor/temp","28.5",{'retain':True});
```




**client.subscribe(*topic*)** microgear may be interested in some topic.  The developer can use the function subscribe() to subscribe a message belong to such topic. If the topic used to retain a message, the microgear will receive a message everytime it subscribes that topic.

argument

* *topic* `string` -  name of the topic to send a message to. Should start with "/". 



```python
client.subscribe("/temp");
```

**client.resettoken()** For deleting Token in cache and on the platform. If deleted, need to get a new Token for the next connection.

```python
client.resettoken();
```



###Event
---------------
An application that runs on a microgear is an event-driven type, which responses to various events with the callback function in a form of event function call:


**client.on_connect**  This event is created when the microgear library successfully connects to the NETPIE platform.

Parameter set

* *callback* `function` - A function to execute after getting connected


```python
def callback_connect() :
	print "Now I am connected with netpie"
client.on_ connect = callback_connect
```




**client.on_disconnect** This event is created when the microgear library disconnects the NETPIE platform.

Parameter set


* *callback* `function` - A function to execute after getting disconnected


```python
def callback_disconnect() :
	print "Disconnected”
client.on_disconnect = callback_disconnect

```




**client.on_message** When there is an incomming message from chat or from subscribed topic. This event is created with the related information to be sent via the callback function.

Parameter set
* *callback* `function` - A function to execute after getting a message. It takes 2 arguments.
    * *topic* - The subscribed topic that he message belongs to. 
    * *message* - The received message.


```python
def callback_message(topic, message) :
  print "I got message from ", topic, ": ", message
client.on_message= callback_message

```


**client.on_present** This event is created when there is a microgear under the same appid appears online to connect to NETPIE.

Parameter set


* *callback* `function` - A function to executed after this event. It takes 1 argument.
     * *gearkey* - The gearkey related to this event.


```python
def callback_present(gearkey) :
	print gearkey+" become online."
client.on_present = callback_present

```




**client.on_absent** This event is created when the microgear under the same appid appears offline.

Parameter set


* *callback* `function` - A function to executed after this event. It takes 1 argument.
    * *gearkey* - The gearkey related to this event.


```python
def callback_absent(gearkey) :
	print gearkey+" become offline."
client.on_absent = callback_absent

```

**client.on_warning** This event is created when some event occurs, and a warning message will be notified.

Parameter set


* *callback* `function` - A function to executed after this event. It takes 1 argument.
    * *msg* - A message related to this event.


```python
def callback_warning(msg) :
	print msg
client.on_warning = callback_warning

```

**client.on_info** This event is created when there is some event occurs within a microgear

Parameter set


* *callback* `function` - A function to executed after this event. It takes 1 argument.
    * *msg* - A message related to this event.


```python
def callback_info(msg) :
	print msg
client.on_info = callback_info

```

**client.on_error** This event is created when an error occurs within a microgear.

Parameter set


* *callback* `function` - A function to executed after this event. It takes 1 argument.
    * *msg* - An error message related to this event.


```python
def callback_error(msg) :
	print msg
client.on_error = callback_error

```
