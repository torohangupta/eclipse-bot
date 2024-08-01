import json
import config
from helpers.PlayerHelper import PlayerHelper
from PIL import Image, ImageDraw, ImageFont
import os
import random

class GamestateHelper:
    def __init__(self, game_id):
        self.game_id = game_id
        self.gamestate = self.get_gamestate()

    def get_gamestate(self):
        with open(f"{config.gamestate_path}/{self.game_id}.json", "r") as f:
            gamestate = json.load(f)
        return gamestate
    
    def showTile(self, tileName):
        filepath = "images/resources/hexes/"+tileName+".png"
        tileImage = Image.open(filepath).convert("RGBA")
        tileImage = tileImage.resize((345, 299))
        return tileImage

    def tile_draw(self, ring):
        if int(ring) <= 3:
            random.shuffle(self.gamestate[f"tile_deck_{ring}00"])
            tile = self.gamestate[f"tile_deck_{ring}00"].pop(0)
            self.update()
            return tile
        else:
            random.shuffle(self.gamestate[f"tile_deck_300"])
            tile = self.gamestate[f"tile_deck_300"].pop(0)
            self.update()
            return tile

    def tile_discard(self, sector):
        self.gamestate["tile_discard"].append(sector)
        self.update()

    def getShipFullName(self, shipAbbreviation):
        if shipAbbreviation == "int":  
            return "interceptor"
        elif shipAbbreviation == "cru": 
            return "cruiser"
        elif shipAbbreviation == "drd":
            return "dreadnought"
        elif shipAbbreviation == "sta": 
            return "starbase"
    
    def drawTile(self, context, position, tileName, rotation):
        filepath = "images/resources/hexes/defended/"+tileName+".png"
        if not os.path.exists(filepath):  
            filepath = "images/resources/hexes/homesystems/"+tileName+".png"
        if not os.path.exists(filepath):  
            filepath = "images/resources/hexes/backs/"+tileName+".png"
        if not os.path.exists(filepath):
            filepath = "images/resources/hexes/sector1/"+tileName+".png"
        if not os.path.exists(filepath):  
            filepath = "images/resources/hexes/sector2/"+tileName+".png"
        if not os.path.exists(filepath):  
            filepath = "images/resources/hexes/sector3/"+tileName+".png"
        if os.path.exists(filepath):  
            tileImage = Image.open(filepath).convert("RGBA")
            
            tileImage = tileImage.resize((345, 299))
            tile = self.gamestate["board"][position]
            if "player_ships" in tile:
                ships = tile["player_ships"]
                count = 0
                for ship in ships:  
                    result = ship.split('-')
                    color = result[0]
                    type = self.getShipFullName(result[1])
                    shippath = "images/resources/components/basic_ships/"+type+"_basic_"+color+".png"
                    shipImage = Image.open(shippath).convert("RGBA")
                    shipImage = shipImage.resize((70,70))
                    tileImage.paste(shipImage, (125+count,32+count),mask=shipImage)
                    count = count + 20
                    
            if "owner" in tile and tile["owner"] != 0:
                color = tile["owner"]
                influencepath = "images/resources/components/all_boards/influence_disc_"+color+".png"
                influenceImage = Image.open(influencepath).convert("RGBA")
                influenceImage = influenceImage.resize((50,50))
                tileImage.paste(influenceImage, (148,125),mask=influenceImage)

            tileImage = tileImage.rotate(rotation)
            font = ImageFont.truetype("arial.ttf", size=45) 
            text = str(position)
            text_position = (255, 132) 
            text_color = (255, 255, 255) 
            textDrawableImage = ImageDraw.Draw(tileImage)
            textDrawableImage.text(text_position,text,text_color,font=font)
            return tileImage

        return context
    
    def getShortFactionNameFromFull(self, fullName):
        if fullName == "Descendants of Draco":  
            return "draco"
        elif fullName == "Mechanema": 
            return "mechanema"
        elif fullName == "Planta": 
            return "planta"
        elif fullName == "Orian Hegemony" or fullName == "Orion Hegemony": 
            return "orion"
        elif fullName == "Hydran Progress": 
            return "hydran"
        elif fullName == "Eridian Empire": 
            return "eridani"
        elif "terran" in fullName: 
            return fullName.lower().replace(" ","_")

    def drawPlayerArea(self, player):
        faction = player["name"]
        faction = self.getShortFactionNameFromFull(faction)
        filepath = "images/resources/components/factions/"+faction+"_board.png"
        context = Image.new("RGBA",(1200,500),(255,255,255,0))
        boardImage = Image.open(filepath).convert("RGBA")
        boardImage = boardImage.resize((895, 500))
        context.paste(boardImage, (0,0))
        x = 925
        y = 50
        font = ImageFont.truetype("arial.ttf", size=90) 
        stroke_color=(0, 0, 0)
        stroke_width=2

        moneyImage = Image.open("images/resources/components/resourcesymbols/money.png").convert("RGBA")
        moneyImage = moneyImage.resize((100, 100))
        context.paste(moneyImage, (x,y))
        text_color = (255, 255, 0) 
        textDrawableImage = ImageDraw.Draw(context)
        textDrawableImage.text((x+120, y),str(player["money"]),text_color,font=font,stroke_width=stroke_width,stroke_fill=stroke_color)

        y = y+100
        scienceImage = Image.open("images/resources/components/resourcesymbols/science.png").convert("RGBA")
        scienceImage = scienceImage.resize((100, 100))
        context.paste(scienceImage, (x,y))
        text_color = (255,192,203) 
        textDrawableImage = ImageDraw.Draw(context)
        textDrawableImage.text((x+120, y),str(player["science"]),text_color,font=font,stroke_width=stroke_width,stroke_fill=stroke_color)

        y = y+100
        materialImage = Image.open("images/resources/components/resourcesymbols/material.png").convert("RGBA")
        materialImage = materialImage.resize((100, 100))
        context.paste(materialImage, (x,y))
        text_color = (101, 67, 33) 
        textDrawableImage = ImageDraw.Draw(context)
        textDrawableImage.text((x+120, y),str(player["materials"]),text_color,font=font,stroke_width=stroke_width,stroke_fill=stroke_color)

        return context


    def add_tile(self, position, orientation, sector, owner=None):

        with open("data/sectors.json") as f:
            tile_data = json.load(f)
        try:
            tile = tile_data[sector]
            if owner != None:
                tile["owner"] = owner
            tile.update({"sector": sector})
            tile.update({"orientation": orientation})
        except KeyError:
            tile = {"sector": sector, "orientation": orientation}
        self.gamestate["board"][position] = tile
        self.update()

    def add_control(self, color, position):
        self.gamestate["board"][position]["owner"] = color
        self.gamestate["players"][self.get_player_from_color(color)]["influence_discs"] -= 1
        self.update()

    def remove_control(self, color, position):
        self.gamestate["board"][position]["owner"] = 0
        self.gamestate["players"][self.get_player_from_color(color)]["influence_discs"] += 1
        self.update()

    def add_units(self, unit_list, position):
        for i in unit_list:
            self.gamestate["board"][position]["player_ships"].append(i)
        self.update()
            #TODO remove ships from player stock

    def remove_units(self, unit_list, position):
        for i in unit_list:
            if i in self.gamestate["board"][position]["player_ships"]:
                self.gamestate["board"][position]["player_ships"].remove(i)
        self.update()
                #TODO return ships to player stock


    def player_setup(self, player_id, faction, color):
        if self.gamestate["setup_finished"] == 1:
            return ("The game has already been setup!")

        with open("data/factions.json", "r") as f:
            faction_data = json.load(f)

        self.gamestate["players"][str(player_id)].update({"color": color})
        self.gamestate["players"][str(player_id)].update(faction_data[faction])
        self.update()
        #return(f"{name} is now setup!")

    def setup_finished(self):

        for i in self.gamestate["players"]:
            if len(self.gamestate["players"][i]) < 3:
                return(f"{self.gamestate['players'][i]['player_name']} still needs to be setup!")
            else:
                p1 = PlayerHelper(i, self.get_player(i))
                home = self.get_system_coord(p1.stats["home_planet"])
                if p1.stats["name"] == "Orion Hegemony":
                    self.gamestate["board"][home]["player_ships"].append(p1.stats["color"]+"-cru")
                else:
                    self.gamestate["board"][home]["player_ships"].append(p1.stats["color"] + "-int")

                if p1.stats["name"] == "Eridani Empire":
                    random.shuffle(self.gamestate["reputation_deck"])
                    p1.stats["reputation_track"][0] = self.gamestate["reputation_deck"].pop(0)
                    p1.stats["reputation_track"][1] = self.gamestate["reputation_deck"].pop(0)
                    self.update_player(p1)

        self.gamestate["player_count"] = len(self.gamestate["players"])
        draw_count = {2: [5, 12], 3: [8, 14], 4: [14, 16], 5: [16, 18], 6: [18, 20]}

        third_sector_tiles = ["301", "302", "303", "304", "305", "306", "307", "308", "309", "310", "311", "312", "313", "314",
                              "315", "316", "317", "318", "381", "382"]
        sector_draws = draw_count[self.gamestate["player_count"]][0]
        tech_draws = draw_count[self.gamestate["player_count"]][1]

        with open("data/techs.json", "r") as f:
            tech_data = json.load(f)

        while sector_draws > 0:
            random.shuffle(third_sector_tiles)
            self.gamestate["tile_deck_300"].append(third_sector_tiles.pop(0))
            sector_draws -= 1

        while tech_draws > 0:
            random.shuffle(self.gamestate["tech_deck"])
            picked_tech = self.gamestate["tech_deck"].pop(0)

            self.gamestate["available_techs"].append(tech_data[picked_tech])

            if tech_data[picked_tech]["track"] == "any":
                pass
            else:
                tech_draws -= 1

        self.gamestate["setup_finished"] = 1
        self.update()
        return("Game setup complete")

    def update(self):
        with open(f"{config.gamestate_path}/{self.game_id}.json", "w") as f:
            json.dump(self.gamestate, f)

    def get_player(self, player_id):
        return self.gamestate["players"][str(player_id)]

    def get_player_from_color(self, color):
        for i in self.gamestate["players"]:
            if self.gamestate["players"][i]["color"] == color:
                return i

    def update_player(self, *args):

        for ar in args:
            self.gamestate["players"][ar.player_id] = ar.stats
        self.update()

    def get_system_coord(self, sector):
        for i in (self.gamestate["board"]):
            if self.gamestate["board"][i]["sector"] == sector:
                return(i)
        return(False)