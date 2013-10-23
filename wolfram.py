import wolframalpha
import config
client=wolframalpha.Client(config.app_id)

def result(resultObject):
	return list(resultObject.results)[0].text.split("(")[0].strip()
wolframalpha.Result.result=result