# hatbot - a very basic Owncast chat bot
# Public Domain, written 2021 by hatniX
# https://github.com/hatniX/hatbot
#
# Requirements:
#     Owncast - https://owncast.online
#     Python3 - https://www.python.org/
#     Flask - https://flask.palletsprojects.com/
#
# Setup Owncast webhook url: http://localhost:5000/webhook
# Setup Flask using python3-pip: python3 -m pip install Flask
# Run this script: FLASK_APP=hatbot.py python3 -m flask run

import os, random, json, requests
from requests.structures import CaseInsensitiveDict
from flask import Flask, request, Response

# the version number of this bot
bot_version = "0.0.2"

# reading the config file
with open("config.json") as json_config:
    data_config = json.load(json_config)

# reading the command list
with open("commands.json") as json_commands:
    data_commands = json.load(json_commands)

# the url of  the Owncast API for bot posts
owncast_url = data_config["owncast_server"] + "/api/integrations/chat/send"

# prepare the header for the bot posts
headers = CaseInsensitiveDict()
headers["Content-Type"] = "application/json"
headers["Authorization"] = "Bearer " + data_config["access_token"]

app = Flask(__name__)
@app.route('/webhook', methods=['POST'])

def respond():

    # in case of a CHAT event... (no other events are handled at the moment)
    if request.json["type"] == "CHAT":

        # TODO creating/saving a chatlog
        # print(request.json["eventData"]["timestamp"] + "\t" + request.json["eventData"]["user"]["displayName"] + "\t" + request.json["eventData"]["body"]);
        # filename = "/foo/bar/baz.txt"
        # os.makedirs(os.path.dirname(filename), exist_ok=True)
        # with open(filename, "w") as f:
        #     f.write("FOOBAR")

        isComm = request.json["eventData"]["body"].partition(' ')[0]
        if (data_commands.get(isComm) != None):

            # make sure everything is latin-1 (still needs some fine-tuning?)
            answer = str(bytes(data_commands[isComm], "utf-8"), "latin-1")

            # extract the parameter (everything that was provided after the actual command)
            parameter = ""
            if (isComm != request.json["eventData"]["body"]):
                para = request.json["eventData"]["body"].split(" ", 1)
                if (len(para) > 1):
                    parameter = para[1]

            # replace variables in the command responses:
            #     {sender} -    the sender's user name
            #     {touser} -    a given parameter or the sender's user name
            #     {parameter} - a given parameter (required)
            #     {random} -    a random number between 1 and 100
            #     {cmdlist} -   the list of all available commands
            #     {botver} -    the version number of this bot

            answer = answer.replace("{sender}", request.json["eventData"]["user"]["displayName"])

            if ("{touser}" in answer):
                if (parameter != ""):
                    answer = answer.replace("{touser}", parameter)
                else:
                    answer = answer.replace("{touser}", request.json["eventData"]["user"]["displayName"])

            if ("{parameter}" in answer):
                if (parameter != ""):
                    answer = answer.replace("{parameter}", parameter)
                else:
                    answer = "This command needs something to work with. Try: **" + isComm + " WhatEverYouLike**"

            answer = answer.replace("{random}", str(random.randrange(1, 100, 1)))

            if ("{cmdlist}" in answer):
                cmds = ""
                for cmd in data_commands.keys():
                    cmds = cmds + cmd +" "
                answer = answer.replace("{cmdlist}", cmds)

            answer = answer.replace("{botver}", bot_version)

            # building the response's body and sending it
            data = '{"body": "' + answer + '"}'
            resp = requests.post(owncast_url, headers=headers, data=data)
            if resp.status_code != 200:
                print("Bot post, error code: " + str(resp.status_code))

    return Response(status=200)
