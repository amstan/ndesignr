from pygraphviz import *

A=AGraph()

A.graph_attr["mindist"]=10

# set some default node attributes
A.node_attr['style']='filled'
A.node_attr['shape']='none'
A.node_attr['fixedsize']='true'
A.node_attr['fontcolor']='#FFFFFF'
A.node_attr['image']="resources/router.png"
A.edge_attr["headlabel"]="192.168.0.10/24\n102".replace("\n","\l")
A.edge_attr["taillabel"]="192.168.0.11/24\n103".replace("\n","\l")
#A.edge_attr["head_lp"]="1000"

A.edge_attr["label"]="10MB/s"

for i in range(5):
	A.add_node(i, pin=True, pos="%s,%s!" % (i*60,10))

for i in range(5):
	for j in range(5):
		if i!=j:
			A.add_edge(i,j)

## make a star in shades of red
#for i in range(16):
    #A.add_edge(0,i)
    #n=
    #n.attr['fillcolor']="#ffffff"
    #n.attr['height']="%s"%(i/16.0+0.5)
    #n.attr['width']="%s"%(i/16.0+0.5)

A.draw('output.png',prog="neato") # draw to png using circo
