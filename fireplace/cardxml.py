import os
from xml.etree import ElementTree
from fireplace.enums import AuraType, CardClass, CardType, Faction, GameTag, PlayReq, Race, Rarity, Zone


class CardXML(object):
	def __init__(self, xml):
		self.xml = xml
		e = self.xml.findall("./Tag")
		self.tags = {GameTag(int(tag.attrib["enumID"])): self._getTag(tag) for tag in e}

		e = self.xml.findall("HeroPower")
		self.heroPower = e and e[0].attrib["cardID"]

		e = self.xml.findall("Power[PlayRequirement]/PlayRequirement")
		self.requirements = self._getRequirements(e)

		e = self.xml.findall("PowerUpRequirement")
		self.powerUpRequirements = [Race(int(tag.attrib["param"])) for tag in e]

		e = self.xml.findall("./EnrageDefinition/Tag")
		self.enrageTags = {GameTag(int(tag.attrib["enumID"])): self._getTag(tag) for tag in e}

		e = self.xml.findall("Aura")
		self.auras = [{
			"id": tag.attrib["cardID"],
			"requirements": self._getRequirements(tag.findall("ActiveRequirement")),
			"type": AuraType(int(tag.attrib["type"])),
		} for tag in e]

		self.chooseCards = [tag.attrib["cardID"] for tag in xml.findall("ChooseCard")]
		self.entourage = [tag.attrib["cardID"] for tag in xml.findall("EntourageCard")]

	def __str__(self):
		return self.name

	def __repr__(self):
		return "<%s: %r>" % (self.id, self.name)

	def _findTag(self, id):
		return self.xml.findall('./Tag[@enumID="%i"]' % (id))

	def _getTag(self, element):
		type = element.attrib.get("type", "Int")

		if type == "Card":
			return element.attrib["value"]

		if type == "String":
			return element.text

		value = int(element.attrib["value"])
		if type == "Bool":
			return bool(value)

		return value

	def _getRequirements(self, reqs):
		return {PlayReq(int(tag.attrib["reqID"])): int(tag.attrib["param"] or 0) for tag in reqs}

	@property
	def id(self):
		return self.xml.attrib["CardID"]

	@property
	def name(self):
		return self.tags[GameTag.CARDNAME]

	@property
	def description(self):
		return self.tags.get(GameTag.CARDTEXT_INHAND, "")

	@property
	def cardClass(self):
		return CardClass(self.tags.get(GameTag.CLASS, 0))

	@property
	def collectible(self):
		return bool(self.tags.get(GameTag.Collectible, False))

	@property
	def cost(self):
		return self.tags.get(GameTag.COST, 0)

	@property
	def faction(self):
		return Faction(self.tags.get(GameTag.FACTION, 0))

	@property
	def race(self):
		return Race(self.tags.get(GameTag.CARDRACE, 0))

	@property
	def rarity(self):
		return Rarity(self.tags.get(GameTag.RARITY, 0))

	@property
	def type(self):
		return CardType(self.tags.get(GameTag.CARDTYPE, 0))

	@property
	def secret(self):
		return bool(self.tags.get(GameTag.SECRET, False))

def load(path):
	db = {}
	with open(path, "r", encoding="utf8") as f:
		xml = ElementTree.parse(f)
		for carddata in xml.findall("Entity"):
			card = CardXML(carddata)
			db[card.id] = card
	return db, xml
