#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ipaddress
import ipaddress_additions

import wolfram

class City:
	"""A city in the context of a computer network."""
	
	def __init__(self, name):
		self.links = {}
		self.name = name
	
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
		return int(self.population*config.employees_factor)+config.employees_offset
	
	def __repr__(self):
		return "City(%r)" % (self.name)

class CityLink:
	""" A link to an adjacent city and distance to it."""
	
	def __init__(self, cities):
		if(len(cities) != 2):
			raise ValueError("Only 2 cities allowed.")
		self.cities = frozenset(cities)
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
		min_employees = min(city.employees for city in self.cities)
		return self.distance * config.metric_distance + min_employees * config.metric_employees

	@property
	def price(seclf):
		"""Real cost of the link"""
	
	def __hash__(self):
		return hash(self.cities)
	
	def __eq__(self,other):
		return self.cities==other.cities
	
	def __repr__(self):
		return "CityLink(%r)" % (self.cities,)
	
	def __str__(self):
		return "%s<->%s" % tuple(sorted(city.name for city in self.cities))

if __name__=="__main__":
	import config
	cities=map(City,config.cities)
	for city in cities:
		print "%20s %8d %5d" % (city, city.population, city.employees)
	links=set(CityLink((c1,c2)) for c1 in cities for c2 in cities if c1!=c2)
	
	def list_links():	
		for i,link in enumerate(links):
			print "%s/%s" % (i,len(links)),  link, link.distance, link.metric
