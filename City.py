import wolfram

class City:
	"""A city in the context of a computer network."""
	
	def __init__(self, name):
		self.links = {}
		self.name = name
	
	@property
	def population(self):
		result = wolfram.client.query("population of " + self.name).result().split(" ")
		number = float(result[0])
		
		if("million" in result):
			number *= 1000000
		
		self.population = number
		return self.population
	
	def __repr__(self):
		return "City(%r)" % (self.name)

class CityLink:
	""" A link to an adjacent city and distance to it."""
	
	def __init__(self, cities):
		if(len(cities) != 2):
			raise ValueError("Only 2 cities allowed.")
		self.cities = cities
		cities[0].links[cities[1]]=self
		cities[1].links[cities[0]]=self
	
	@property
	def distance(self):
		query = "distance from {0} to {1}".format(*[city.name for city in self.cities])
		result = wolfram.client.query(query).result().split(" ")
		self.distance = float(result[0])
		return self.distance
	
	def __repr__(self):
		return "CityLink(%r)" % self.cities
