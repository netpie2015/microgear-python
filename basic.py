import microgear.client as mg



mg.create("qDDwMaHEXfBiXmL","vNoswuhfqjxWSm0GR7cycGPniekw03","piedemo")
#mg.subscribe("/piedemo/gearname/python")

def test(p):
	mg.chat("htmlgear","hello2222 test"+p)
	print "test"+p

#mg.setname("python")
mg.subscribe("python",test)
mg.chat("htmlgear","tewwwwwwwwwwwwst")
mg.connect()
