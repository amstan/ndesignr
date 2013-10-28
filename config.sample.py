cities=['Toronto', 'Hamilton', 'London', 'Ottawa', 'Sarnia', 'Windsor', 'Thunder Bay', 'Montreal', 'Quebec City', 'Sherbrooke', 'St Johns', 'Halifax', 'Vancouver', 'Calgary', 'Edmonton', 'Regina', 'Winnipeg', 'Victoria, BC', 'Prince George', 'Yellowknife', 'Whitehorse, Yukon', 'New York', 'Chicago', 'Buffalo', 'Detroit', 'St. Louis', 'Washington DC', 'Atlanta', 'Cincinnati', 'New Orleans', 'Houston', 'Dallas', 'Miami', 'Seattle', 'Los Angles', 'London, UK', 'Paris', 'Rome', 'Berlin', 'Dublin', 'Madrid', 'Brussels', 'Vienna', 'Helsinki', 'Amsterdam', 'Sao Paulo', 'Buenos Aires', 'Santiago', 'Lima', 'Caracas', 'Sydney', 'Perth', 'Melbourne', 'Adelaide', 'Singapore', 'New Delhi', 'Mumbai', 'Bangalore', 'Beijing', 'Hong Kong', 'Abu Dhabi', 'Dubai', 'Manila']

app_id="" #for wolfram alpha

#employee calculation
employees="population * 0.0002 + 20"

#wan links
metric="(-1/10000.0 * distance) + (1/1000.0 * employees)"

host_counts="""{
	"Servers": 1 + employees/50,
	"Printers": 2 + employees/10,
	"Wifi": 30 + employees,
	"Voip": 10 + 2*employees,
	"PCs": 10 + 3*employees,
	"Admin": 2 + employees/128, #Switch management vlan,
}"""

wan_links={
	100: 1,
	200: 2,
	500: 2,
	1000: 3,
	10000: 3,
}

internet_uplinks = "1 + employees/250"

import ipaddress
company_network_v4 = ipaddress.IPv4Network(u"25.0.0.0/8")
company_network_v6 = ipaddress.IPv6Network(u"dead:beef:2500::/48")
