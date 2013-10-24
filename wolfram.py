#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import wolframalpha
import config
_client=wolframalpha.Client(config.app_id)

try:
	cache=eval(open("cache.txt").read())
except IOError:
	cache={}

def query(query):
	try:
		return cache[query]
	except KeyError:
		result=list(_client.query(query).results)[0].text.split("(")[0].strip()
		cache[query]=result
		with open("cache.txt","w") as f:
			f.write(repr(cache))
		return result