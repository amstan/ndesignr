#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ipaddress
import ipaddress_additions

import wolfram

import math
import re

import StringIO
import sys
from contextlib import contextmanager
@contextmanager
def stdout_redirected(new_stdout):
	save_stdout = sys.stdout
	sys.stdout = new_stdout
	try:
		yield None
	finally:
		sys.stdout = save_stdout

class City:
	"""A city in the context of a computer network."""
	
	def __init__(self, name):
		self.links = {}
		self.name = name
	
	@property
	def location(self):
		result = wolfram.query("%s coordinates" % self.name)
		parsed = re.match(u"([0-9]*\xb0)? ?([0-9]*').*([NS])(,) ([0-9]*\xb0)? ?([0-9]*').*([WE])",result).groups()
		middle=parsed.index(",")
		
		def parsenumber(parsed):
			n=0
			if parsed[0]!=None:
				n+=float(parsed[0][:-1])
			if parsed[1]!=None:
				n+=float(parsed[1][:-1])/60
			if parsed[-1] in "SW":
				n*=-1
			n+=180
			return n
		
		y=parsenumber(parsed[:middle])
		x=parsenumber(parsed[middle+1:])
		
		return (x/10,y/10)

	@property
	def population(self):
		result = wolfram.query("population of " + self.name).split(" ")
		number = float(result[0])
		
		if("million" in result):
			number *= 1000000
		
		self.population = int(number)
		return self.population
	
	def __hash__(self):
		return hash(self.name)

	def __cmp__(self,other):
		return cmp(self.name,other.name)
	
	@property
	def employees(self):
		return int(eval(config.employees, {
			"population" : self.population
		}))
	
	@property
	def host_counts(self):
		return eval(config.host_counts, {
			"employees":self.employees
		})
	
	@property
	def internet_uplinks(self):
		return eval(config.internet_uplinks, {
			"employees":self.employees
		})
	
	network=ipaddress.IPv4Network(u"10.0.0.0/8")
	
	@property
	def networks(self):
		networks={}
		
		for network_name, host_count in sorted(self.host_counts.items(),key=lambda (name,host_count):host_count,reverse=True):
			bits_required=int(math.ceil(math.log(host_count+3)/math.log(2)))
			cidr=32-bits_required
			try:
				network=network.next_network(cidr)
			except NameError:
				#probably the first network
				network=ipaddress.IPv4Network(u"%s/%d" % (self.network.network_address,cidr))
			
			network.hosts=host_count #store this for later reference
			networks[network_name]=network
		
		networks["Internet"]=[]
		for i in range(self.internet_uplinks):
			network=network.next_network(30)
			networks["Internet"].append(network)
		
		return networks
	
	@property
	def network_size(self):
		"""Required network size(cidr) to encompass the whole branch."""
		networks=self.networks
		internet=networks.pop("Internet")
		networks=networks.values()+internet
		return sum(networks[1:],networks[0]).prefixlen
	
	def __repr__(self):
		return "City(%r)" % (self.name)
	
	def __str__(self):
		output=StringIO.StringIO()
		with stdout_redirected(output):
			print "%s (population %d)" % (self.name,self.population)
			print "%d Employees" % self.employees
			print
			print "%s block allocated to this branch." % self.network
			print
			
			networks=self.networks
			internet=networks.pop("Internet")
			
			print "Networks:"
			for name,network in sorted(networks.items(), key=lambda (name,network): ipaddress.get_mixed_type_key(network)):
				print " %s: %d hosts %s (%d available)" % (name, network.hosts, network, (2**(32-network.prefixlen))-3)
			print ""
			
			print "Internet Uplinks:"
			for network in internet:
				print " local:%s, ISP:%s" % tuple(network.hosts())
			
		return output.getvalue()

class CityLink:
	""" A link to an adjacent city and distance to it."""
	
	def __init__(self, cities):
		if(len(cities) != 2):
			raise ValueError("Only 2 cities allowed.")
		self.cities = frozenset(cities)
		self.link_cities()
	
	def link_cities(self):
		cities=list(self.cities)
		cities[0].links[cities[1]]=self
		cities[1].links[cities[0]]=self
	
	@property
	def distance(self):
		query = "distance from %s to %s" % tuple(sorted(city.name for city in self.cities))
		result = wolfram.query(query).split(" ")
		self.distance = float(result[0])
		return self.distance
	
	@property
	def metric(self):
		"""Metric cost of the link"""
		return eval(config.metric, {
			"distance" : self.distance,
			"employees" : min(city.employees for city in self.cities)
		})

	@property
	def price(seclf):
		"""Real cost of the link"""
	
	def __hash__(self):
		return hash(self.cities)
	
	def __eq__(self,other):
		return self.cities==other.cities
	
	def __repr__(self):
		return "CityLink(%r)" % (list(self.cities),)
	
	def __str__(self):
		return "%s<->%s" % tuple(sorted(city.name for city in self.cities))

if __name__=="__main__":
	import config
	cities={cityname:City(cityname) for cityname in config.cities}
	city_network_sizes={}
	for city in cities.values():
		city_network_sizes[city]=city.network_size
		print "%25r %8d %5d /%d %r" % (city, city.population, city.employees, city_network_sizes[city], city.location)
	links=set(CityLink((c1,c2)) for c1 in cities.values() for c2 in cities.values() if c1!=c2)
	
	for city,network_size in sorted(city_network_sizes.items(),key=lambda (city,network_size):network_size):
		try:
			network=network.next_network(network_size)
		except NameError:
			#probably the first network
			network=ipaddress.IPv4Network(u"%s/%d" % (config.company_network_v4.network_address,network_size))
		city.network=network
	
	def list_links():
		for i,link in enumerate(sorted(links,key=lambda link:sorted(city.name for city in link.cities))):
			print "%s/%s" % (i+1,len(links)),  link, link.distance, link.metric
	
	def list_networks():
		for city in sorted(cities.values(),key=lambda city: ipaddress.get_mixed_type_key(city.network)):
			print "%25r %s" % (city, city.network)
	
	for city in cities.values():
		for max_employees in sorted(config.wan_links):
			num_links = config.wan_links[max_employees]
			if max_employees>city.employees:
				break
		print city.name, city.employees, num_links
		worthy_links=sorted(city.links.values(),key=lambda link: link.metric,reverse=True)[:num_links]
		for othercity,link in city.links.items():
			if link not in worthy_links:
				del city.links[othercity]
	for city in cities.values():
		for link in city.links.values():
			link.link_cities()
	
	from pygraphviz import *
	
	graph = AGraph()
	#graph.graph_attr["mode"]="ipsep"
	graph.graph_attr["K"]=10
	graph.graph_attr["maxiter"]=10000
	graph.node_attr["image"]="resources/router.png"
	graph.node_attr["shape"]="none"
	graph.node_attr["fixedsize"]="true"
	graph.edge_attr["labeldistance"]=5
	
	for city in cities.values():
		graph.add_node(city.name, label="%s\l%s" % (city.name,city.network))#, pin="false", pos="%s,%s!" % city.location)
	
	links=set(link for city in cities.values() for link in city.links.values())
	
	branchnetworks=[city.network for city in cities.values()]
	branchnetworks=sum(branchnetworks[1:],branchnetworks[0])
	for i,link in enumerate(links):
		try:
			link.network=previous_wan.next_network(cidr=30)
		except NameError:
			link.network=branchnetworks.next_network(cidr=30)
		previous_wan=link.network
		
		cities=sorted([city.name for city in link.cities])
		link.dlcis=(100+i*10,100+i*10+1)
		ips=list(link.network.hosts())
		
		graph.add_edge(cities[0],cities[1],headlabel="%s\lDLCI: %d" % (ips[0],link.dlcis[0]),taillabel="%s\lDLCI: %d" % (ips[1],link.dlcis[1]))
	
	graph.draw("output.svg",prog="fdp")