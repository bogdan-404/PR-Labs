import json
from player import Player
import xml.etree.ElementTree as ET
from player_pb2 import PlayersList, Class


class PlayerFactory:
    def to_json(self, players):
        # this function should transform a list of Player objects into a list with dictionaries.
        returned_json = []
        for player in players:
            new_player = {
                "nickname": player.nickname,
                "email": player.email,
                "date_of_birth": player.date_of_birth.strftime("%Y-%m-%d"),
                "xp": player.xp,
                "class": player.cls
            }
            returned_json.append(new_player)
        return returned_json

    def from_json(self, list_of_dict):
       # This function should transform a list of dictionaries into a list with Player objects.
        players = []
        for dict in list_of_dict:
            new_player = Player(dict['nickname'], dict['email'], dict['date_of_birth'], int(
                dict['xp']), dict['class'])
            players.append(new_player)
        return players

    def to_xml(self, list_of_players):
        # This function should transform a list with Player objects into a XML string.
        usrconfig = ET.Element("usrconfig")
        usrconfig = ET.SubElement(usrconfig, "data")
        for player in list_of_players:
            usr = ET.SubElement(usrconfig, "player")

            nick = ET.SubElement(usr, "nickname")
            nick.text = player.nickname

            email = ET.SubElement(usr, "email")
            email.text = player.email

            date_of_birth = ET.SubElement(usr, "date_of_birth")
            date_of_birth.text = player.date_of_birth.strftime("%Y-%m-%d")

            xp = ET.SubElement(usr, "xp")
            xp.text = str(player.xp)

            clss = ET.SubElement(usr, "class")
            clss.text = player.cls

        return ET.tostring(usrconfig, encoding='utf8')

    def from_xml(self, xml_string):
        # This function should transform a XML string into a list with Player objects.
        root = ET.fromstring(xml_string)
        players = []
        for child in root:
            list = []
            for secondary in child:
                list.append(secondary.text)
            players.append(
                Player(list[0], list[1], list[2], int(list[3]), list[4]))
        return players

    def from_protobuf(self, binary):
        # This function should transform a binary protobuf string into a list with Player objects.
        players_list = PlayersList()
        players_list.ParseFromString(binary)

        players = []

        for player in players_list.player:
            new_player = Player(player.nickname, player.email, player.date_of_birth, int(
                player.xp), Class.Name(player.cls))
            players.append(new_player)
        return players

    def to_protobuf(self, list_of_players):
        # This function should transform a list with Player objects into a binary protobuf string.
        players_list = PlayersList()
        for object in list_of_players:
            player = players_list.player.add()
            player.nickname = object.nickname
            player.email = object.email
            player.date_of_birth = object.date_of_birth.strftime("%Y-%m-%d")
            player.xp = object.xp
            player.cls = Class.Value(object.cls)
        return players_list.SerializeToString()

