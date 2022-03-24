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
from flask import Flask, request, Response, jsonify

# the version number of this bot
bot_version = "0.0.5"

# reading the config file
with open("config.json") as json_config:
    data_config = json.load(json_config)

# reading the alias list
with open("alias.json") as json_alias:
    data_alias = json.load(json_alias)

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

        print("\n" + request.json["eventData"]["timestamp"][0:10] + " " + request.json["eventData"]["timestamp"][11:19] + " - " + request.json["eventData"]["user"]["displayName"] + " - " + request.json["eventData"]["body"]);

        isComm = request.json["eventData"]["body"].partition(' ')[0]

        # check for aliases
        if (data_alias.get(isComm.lower()) != None):
            isComm = data_alias[isComm.lower()]

        if (data_commands.get(isComm.lower()) != None):

            answer = data_commands[isComm.lower()]

            # extract the parameter (everything that was provided after the actual command)
            parameter = ""
            if (isComm != request.json["eventData"]["body"]):
                para = request.json["eventData"]["body"].split(" ", 1)
                if (len(para) > 1):
                    parameter = para[1]
                    # remove the @ at the beginning of a parameter (may have been used for autocomplete names)
                    if (parameter[0] == "@"):
                        parameter = parameter[1:]

            # replace variables in the command responses:
            #     {sender} -    the sender's user name
            #     {tohost} -    a given parameter or the host's user name (as set in config.json)
            #     {touser} -    a given parameter or the sender's user name
            #     {parameter} - a given parameter (required)
            #     {random} -    a random number between 1 and 100
            #     {cmdlist} -   the list of all available commands
            #     {aliaslist} - the list of all available commands
            #     {botver} -    the version number of this bot

            answer = answer.replace("{sender}", request.json["eventData"]["user"]["displayName"])

            if ("{tohost}" in answer):
                if (parameter != ""):
                    answer = answer.replace("{tohost}", parameter)
                else:
                    answer = answer.replace("{tohost}", data_config["host_name"])

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

            if ("{aliaslist}" in answer):
                cmds = ""
                for cmd in data_alias.keys():
                    cmds = cmds + cmd +" "
                answer = answer.replace("{aliaslist}", cmds)

            answer = answer.replace("{botver}", bot_version)

            # building the response's body and sending it
            data = '{"body": "' + answer + '"}'
            resp = requests.post(owncast_url, headers=headers, data=data.encode('utf-8'))
            if resp.status_code != 200:
                print("Can't respond, error code: " + str(resp.status_code))
            else:
                print("RESPONSE: " + answer)

    return Response(status=200)
