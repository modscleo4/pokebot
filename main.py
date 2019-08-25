from abc import ABC

import requests
import json
from html.parser import HTMLParser

pokemon = {

}


def defaultPokemon():
    return {
        "name": "",
        "description": "",
        "height": None,
        "category": None,
        "weight": None,
        "abilities": [],
        "genders": [],
        "types": [],
        "stats": {
            "hp": None,
            "attack": None,
            "defense": None,
            "special_attack": None,
            "special_defense": None,
            "speed": None,
        },
        "weaknesses": [],
        "predecessor": None,
        "successor": None,
    }


ignoreList = [
    "name1", "description1", "fromData", "height", "category", "weight", "ability", "ability-name", "ability-desc",
    "gender", "typeUl", "type", "evolution-profileUl", "evolution", "ability-info", "ability-info-d", "category-info",
]

ability = {}

evolution = []


class PokedexHTMLParser(HTMLParser, ABC):
    attribute = ""

    def handle_starttag(self, tag, attrs):
        if tag == "div" and self.attribute == "name1":
            self.attribute = "name"
            return
        elif tag == "p" and self.attribute == "description1":
            for names, values in attrs:
                if names == "class" and "active" in values:
                    self.attribute = "description"
                    return
        elif tag == "i" and self.attribute == "gender":
            for names, values in attrs:
                if names == "class" and "_male" in values:
                    if pokemon.get('genders') is None:
                        pokemon['genders'] = []
                    pokemon.get('genders').append("Male")
                elif names == "class" and "_female" in values:
                    if pokemon.get('genders') is None:
                        pokemon['genders'] = []
                    pokemon.get('genders').append("Female")
            return
        elif tag == "a" and self.attribute == "typeUl":
            for names, values in attrs:
                if names == "href" and "/br/pokedex/?type=" in values:
                    self.attribute = "type"
                    return
        elif tag == "span" and self.attribute == "evolution-profileUl":
            for names, values in attrs:
                if names == "class" and values == "pokemon-number":
                    self.attribute = "evolution"
                    return
        elif self.attribute == "ability-info":
            for names, values in attrs:
                if names == "class" and "pokemon-ability-info-detail match" in values:
                    self.attribute = "ability-info-d"
                    return

        elif self.attribute == "ability":
            if tag == "h3":
                self.attribute = "ability-name"
            elif tag == "p":
                self.attribute = "ability-desc"

        for names, values in attrs:
            if names == "class" and values == "pokedex-pokemon-pagination-title":
                self.attribute = "name1"
                return
            elif names == "class" and values == "pokedex-pokemon-details-right":
                self.attribute = "description1"
                return
            elif names == "class" and "pokemon-ability-info " in values and "active" in values:
                self.attribute = "ability-info"
                return
            elif names == "class" and "pokemon-ability-info " in values and "active" not in values:
                self.attribute = ""
                return
            elif names == "class" and "pokedex-pokemon-attributes" in values and "active" in values:
                self.attribute = "category-info"
                return
            elif names == "class" and "pokedex-pokemon-attributes" in values and "active" not in values:
                self.attribute = ""
                return
            elif self.attribute == "ability-info" and names == "class" and values == "attribute-title":
                self.attribute = "fromData"
                return
            elif self.attribute == "category-info" and names == "class" and values == "dtm-type":
                self.attribute = "typeUl"
                return
            elif names == "class" and "evolution-profile" in values:
                self.attribute = "evolution-profileUl"
                return

    def handle_endtag(self, tag):
        if self.attribute == "gender" and tag == "li":
            self.attribute = "ability-info"
        elif self.attribute == "type" and tag == "ul":
            self.attribute = ""
        elif self.attribute == "evolution" and tag == "span":
            self.attribute = "evolution-profileUl"
        elif self.attribute == "evolution-profileUl" and tag == "ul":
            if self.lasttag == "span":
                self.attribute = ""

    def handle_data(self, data):
        global ability

        if self.attribute != "":
            data = data.strip()

            if self.attribute == "fromData":
                data = data.lower()

                if data == "gender":
                    self.attribute = "gender"
                elif data == "abilities":
                    self.attribute = "ability-info"
                elif pokemon.get(data) is None:
                    self.attribute = data
            elif self.attribute == "name":
                pokemon['name'] = data
            elif self.attribute == "description":
                pokemon['description'] = data
            elif self.attribute == "height":
                if data != "":
                    data = float(data.replace(' m', ''))
                    pokemon['height'] = data
                    self.attribute = "ability-info"

            elif self.attribute == "category":
                if data != "":
                    pokemon['category'] = data
                    self.attribute = "ability-info"

            elif self.attribute == "weight":
                if data != "":
                    data = float(data.replace(' kg', ''))
                    pokemon['weight'] = data
                    self.attribute = "ability-info"

            elif self.attribute == "gender":
                if data != "":
                    if pokemon.get('genders') is None:
                        pokemon['genders'] = []
                    pokemon.get('genders').append(data)
                    self.attribute = "ability-info"

            elif self.attribute == "ability-info-d":
                if data == "Ability Info":
                    self.attribute = "ability"

            elif self.attribute == "ability-name":
                if data != "":
                    ability = {"name": data}
                    self.attribute = "ability"

            elif self.attribute == "ability-desc":
                if pokemon.get('abilities') is None:
                    pokemon['abilities'] = []

                ability['description'] = data
                pokemon.get('abilities').append(ability)
                self.attribute = "ability-info"

            elif self.attribute == "type":
                if data != "":
                    if pokemon.get('types') is None:
                        pokemon['types'] = []
                    pokemon.get('types').append(data)

            elif self.attribute == "evolution":
                if data != "":
                    evolution.append(int(data.replace('Nº ', '')))

            if self.attribute not in ignoreList:
                self.attribute = ""


ignoreList2 = [
    "hp", "attack", "defense", "sp. atk", "sp. def", "speed", "fromData", "stats", "isWeaknesses1", "isWeaknesses2",
    "weaknesses", "weaknessEffectiveness", "stop",
]

weakness = {}


class PokemonDBHTMLParser(HTMLParser, ABC):
    attribute = ""

    def handle_starttag(self, tag, attrs):
        global weakness

        if self.attribute != "stop":
            if tag == "th" and self.attribute == "stats":
                self.attribute = "fromData"
            elif tag == "div" and self.attribute == "isWeaknesses2":
                for names, values in attrs:
                    if names == "class" and "active" in values:
                        self.attribute = "weaknesses"
            elif tag == "table" and self.attribute == "isWeaknesses2":
                for names, values in attrs:
                    if names == "class" and "type-table type-table-pokedex" in values:
                        self.attribute = "weaknesses"
            elif tag == "h2" and self.attribute == "":
                self.attribute = "isWeaknesses1"
            elif tag == "td" and self.attribute == "weaknesses":
                if pokemon.get('weaknesses') is None:
                    pokemon['weaknesses'] = []

                for names, values in attrs:
                    if names == "title" and "normal effectiveness" in values:
                        t = values.split(" ")[0]
                        weakness = {"type": t, "effectiveness": 4}
                        # pokemon.get('weaknesses').append(weakness)
                        weakness = {}
                    elif names == "title" and "not very effective" in values or "super-effective" in values or "no effect" in values:
                        t = values.split(" ")[0]
                        weakness = {"type": t}
                        self.attribute = "weaknessEffectiveness"
                return

            for names, values in attrs:
                if names == "id" and values == "dex-stats":
                    self.attribute = "stats"
                    return

    def handle_endtag(self, tag):
        if self.attribute == "weaknesses" and tag == "div":
            self.attribute = "stop"

    def handle_data(self, data):
        global weakness

        if self.attribute != "" and self.attribute != "stop":
            data = data.strip()

            if self.attribute == "fromData":
                data = data.lower()
                self.attribute = data
            elif self.attribute == "isWeaknesses1":
                if data == "Type defenses":
                    self.attribute = "isWeaknesses2"
            else:
                if self.attribute == "hp":
                    if data != "":
                        if pokemon.get('stats') is None:
                            pokemon['stats'] = {}
                        pokemon['stats']['hp'] = int(data)
                        self.attribute = "stats"
                elif self.attribute == "attack":
                    if data != "":
                        if pokemon.get('stats') is None:
                            pokemon['stats'] = {}
                        pokemon['stats']['attack'] = int(data)
                        self.attribute = "stats"
                elif self.attribute == "defense":
                    if data != "":
                        if pokemon.get('stats') is None:
                            pokemon['stats'] = {}
                        pokemon['stats']['defense'] = int(data)
                        self.attribute = "stats"
                elif self.attribute == "sp. atk":
                    if data != "":
                        if pokemon.get('stats') is None:
                            pokemon['stats'] = {}
                        pokemon['stats']['special_attack'] = int(data)
                        self.attribute = "stats"
                elif self.attribute == "sp. def":
                    if data != "":
                        if pokemon.get('stats') is None:
                            pokemon['stats'] = {}
                        pokemon['stats']['special_defense'] = int(data)
                        self.attribute = "stats"
                elif self.attribute == "speed":
                    if data != "":
                        if pokemon.get('stats') is None:
                            pokemon['stats'] = {}
                        pokemon['stats']['speed'] = int(data)
                        self.attribute = "stats"
                elif self.attribute == "weaknessEffectiveness":
                    if data != "":
                        effectiveness = data
                        if effectiveness == "⅛":
                            effectiveness = 1
                        elif effectiveness == "¼":
                            effectiveness = 2
                        elif effectiveness == "½":
                            effectiveness = 3
                        elif effectiveness == "0":
                            effectiveness = 0
                        elif effectiveness == "2" or effectiveness == "2.5":
                            effectiveness = 5
                        elif effectiveness == "4" or effectiveness == "5":
                            effectiveness = 6

                        weakness['effectiveness'] = effectiveness
                        pokemon.get('weaknesses').append(weakness)
                        weakness = {}
                        self.attribute = "weaknesses"

            if self.attribute not in ignoreList2:
                self.attribute = ""


pokemons = []


def getPokemon(i):
    global pokemon

    conn = requests.get("https://www.pokemon.com/br/pokedex/{}".format(i))
    if conn.status_code == 200:
        data = conn.text
        parser = PokedexHTMLParser()
        parser.feed(data)
        if i - 1 in evolution:
            pokemon['predecessor'] = i - 1
        if i + 1 in evolution:
            pokemon['successor'] = i + 1

        conn = requests.get("https://pokemondb.net/pokedex/{}".format(i))
        if conn.status_code == 200:
            data = conn.text
            parser = PokemonDBHTMLParser()
            parser.feed(data)
        else:
            print("HTTP {} {}".format(conn.status_code, conn.reason))
    else:
        print("HTTP {} {}".format(conn.status_code, conn.reason))

    conn.close()


def main():
    global pokemon, evolution, weakness

    for i in range(1, 152):
        pokemon = {}
        evolution = []
        weakness = {}
        getPokemon(i)
        pokemons.append(pokemon)
        print(pokemon)

    print("JSON: {}".format(json.dumps(pokemons)))


if __name__ == "__main__":
    main()
