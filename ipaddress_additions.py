#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ipaddress
import math

class monkeypatch(object):
	"""Decorator for monkey patching."""
	def __init__(self,cls,name=None):
		self.cls=cls
		self.name=name
	def __call__(self,function):
		if self.name==None:
			try:
				self.name=function.__name__
			except:
				self.name=function.__func__.__name__ #classmethods are different
		setattr(self.cls,self.name,function)

@monkeypatch(ipaddress._BaseAddress,"__invert__")
def inv_ip(self):
	cls=self.__class__
	return cls(self._ALL_ONES^int(self))

@monkeypatch(ipaddress._BaseAddress,"__and__")
def and_ip(self,other):
	cls=self.__class__
	return cls(int(self)&int(other))

@monkeypatch(ipaddress._BaseAddress,"__or__")
def or_ip(self,other):
	cls=self.__class__
	return cls(int(self)&int(other))

@monkeypatch(ipaddress._BaseAddress)
@classmethod
def create_netmask(cls,bits):
	"""Creates netmask ip from CIDR number."""
	addr_len=int(math.ceil(math.log(cls._ALL_ONES)/math.log(2)))
	return ~cls(2**(addr_len-bits)-1)

@monkeypatch(ipaddress._BaseAddress)
def network(self,cidr=None):
	"""Returns a network for a corresponding ip address. It will try to autodetect(for ipv4) the address if no cidr is given using classful addresses."""
	cls=self.__class__
	
	if cidr==None and cls==ipaddress.IPv4Address:
		classes = {
			ipaddress.IPv4Network(u"0.0.0.0/1"): 8,
			ipaddress.IPv4Network(u"128.0.0.0/2"): 16,
			ipaddress.IPv4Network(u"192.0.0.0/3"): 24,
		}
	
		for network,cidr in classes.items():
			if self in network:
				break
	
	netmask=cls.create_netmask(cidr)
	network_cls={ipaddress.IPv4Address:ipaddress.IPv4Network,ipaddress.IPv6Address:ipaddress.IPv6Network}[cls]
	
	return network_cls(u"%s/%s" % (self & netmask,netmask))

@monkeypatch(ipaddress._BaseNetwork,"__add__")
def add_networks(self,other):
	cls=self.__class__
	common_bits=self.network_address & other.network_address
	addr_cls=common_bits.__class__
	max_prefix=max(self.prefixlen,other.prefixlen)
	
	for i in reversed(range(max_prefix)):
		netmask=addr_cls.create_netmask(i)
		supernet=cls(u"%s/%s" % (common_bits&netmask,netmask))
		if self.overlaps(supernet) and other.overlaps(supernet):
			break
	
	return supernet

@monkeypatch(ipaddress._BaseNetwork)
def next_network(self,cidr=None):
	"""Returns the next network after the current one. The cidr(recommended smaller than current) of the new network is optional, will be the same as current one if not given."""
	next_address=self.broadcast_address+1
	if cidr==None:
		cidr=self.prefixlen
	next_network=next_address.network(cidr)
	if cidr<self.prefixlen:
		#This might work without a gap
		if self.overlaps(next_network):
			raise ipaddress.AddressValueError("Can't come up with the next network without leaving a gap. Try a smaller cidr.")
	return next_network

@monkeypatch(ipaddress._BaseNetwork)
def gateway_address(self):
	"""By convention, in our Cisco Class, we use the last usable ip as the gateway."""
	return self.broadcast_address-1

if __name__=="__main__":
	"""Stuff useful for testing"""
	nl=ipaddress.IPv4Network(u"127.0.0.0/24")
	n0=ipaddress.IPv4Network(u"192.167.255.0/24")
	n1=ipaddress.IPv4Network(u"192.168.0.0/24")
	n2=n1.next_network()