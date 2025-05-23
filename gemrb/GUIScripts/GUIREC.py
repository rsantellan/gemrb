# GemRB - Infinity Engine Emulator
# Copyright (C) 2003-2009 The GemRB Project
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#


# GUIREC.py - scripts to control stats/records windows from the GUIREC winpack
###################################################
import GemRB
import GameCheck
import GUICommon
import Spellbook
import CommonTables
import LUCommon
import LevelUp
import DualClass
import GUIRECCommon
import PartyReform
from GUIDefines import *
from GUICommonWindows import CreateTopWinLoader, ToggleWindow, OpenWindowOnce
from ie_stats import *
from ie_restype import *
###################################################
InformationWindow = None
KitInfoWindow = None
ColorTable = None
ColorIndex = None
ScriptTextArea = None
SelectedTextArea = None

###################################################

def InitRecordsWindow (Window):
	"""Open Records Window"""

	# dual class
	Button = Window.GetControl (0)
	Button.SetText (7174)
	Button.OnPress (DualClass.DualClassWindow)

	# levelup
	Button = Window.GetControl (37)
	Button.SetText (7175)
	Button.OnPress (LevelUp.OpenLevelUpWindow)

	# information
	Button = Window.GetControl (1)
	Button.SetText (11946)
	Button.OnPress (OpenInformationWindow)

	# reform party
	Button = Window.GetControl (51)
	Button.SetText (16559)
	Button.OnPress (OpenRecReformPartyWindow)

	# customize
	Button = Window.GetControl (50)
	Button.SetText (10645)
	Button.OnPress (GUIRECCommon.OpenCustomizeWindow)

	# export
	Button = Window.GetControl (36)
	Button.SetText (13956)
	Button.OnPress (GUIRECCommon.OpenExportWindow)

	# kit info
	if GameCheck.IsBG2OrEE ():
		Button = Window.GetControl (52)
		Button.SetText (61265)
		Button.OnPress (OpenKitInfoWindow)

	return

def UpdateRecordsWindow (Window):
	global alignment_help

	pc = GemRB.GameGetSelectedPCSingle ()
	GUICommon.UpdateMageSchool (pc)

	# exportable
	Button = Window.GetControl (36)
	if Exportable (pc):
		Button.SetState (IE_GUI_BUTTON_ENABLED)
	else:
		Button.SetState (IE_GUI_BUTTON_DISABLED)

	# dual-classable
	Button = Window.GetControl (0)
	if GUICommon.CanDualClass (pc):
		Button.SetState (IE_GUI_BUTTON_ENABLED)
	else:
		Button.SetState (IE_GUI_BUTTON_DISABLED)

	# levelup
	Button = Window.GetControl (37)
	if LUCommon.CanLevelUp (pc):
		Button.SetState (IE_GUI_BUTTON_ENABLED)
	else:
		Button.SetState (IE_GUI_BUTTON_DISABLED)

	# name
	Label = Window.GetControl (0x1000000e)
	Label.SetText (GemRB.GetPlayerName (pc, 0))

	# portrait
	Button = Window.GetControl (2)
	Button.SetFlags (IE_GUI_BUTTON_NO_IMAGE | IE_GUI_BUTTON_PICTURE, OP_SET)
	Button.SetState (IE_GUI_BUTTON_LOCKED)
	portrait = GemRB.GetPlayerPortrait (pc, 0)
	pic = portrait["Sprite"] if portrait else ""

	if GameCheck.IsBG2OrEE () and not GameCheck.IsBG2Demo():
		Button.SetPicture (pic, "NOPORTMD")
	else:
		Button.SetPicture (pic, "NOPORTLG")

	# armorclass
	GUICommon.DisplayAC (pc, Window, 0x10000028)

	# hp now
	Label = Window.GetControl (0x10000029)
	Label.SetText (str (GemRB.GetPlayerStat (pc, IE_HITPOINTS)))
	Label.SetTooltip (17184)

	# hp max
	Label = Window.GetControl (0x1000002a)
	Label.SetText (str (GemRB.GetPlayerStat (pc, IE_MAXHITPOINTS)))
	Label.SetTooltip (17378)

	# stats
	sstr = GemRB.GetPlayerStat (pc, IE_STR)
	sstrx = GemRB.GetPlayerStat (pc, IE_STREXTRA)
	cstr = GetStatColor (pc, IE_STR)
	if sstrx > 0 and sstr==18:
		sstr = "%d/%02d" %(sstr, sstrx % 100)
	else:
		sstr = str (sstr)

	sint = str (GemRB.GetPlayerStat (pc, IE_INT))
	cint = GetStatColor (pc, IE_INT)
	swis = str (GemRB.GetPlayerStat (pc, IE_WIS))
	cwis = GetStatColor (pc, IE_WIS)
	sdex = str (GemRB.GetPlayerStat (pc, IE_DEX))
	cdex = GetStatColor (pc, IE_DEX)
	scon = str (GemRB.GetPlayerStat (pc, IE_CON))
	ccon = GetStatColor (pc, IE_CON)
	schr = str (GemRB.GetPlayerStat (pc, IE_CHR))
	cchr = GetStatColor (pc, IE_CHR)

	Label = Window.GetControl (0x1000002f)
	Label.SetText (sstr)
	Label.SetColor (cstr)

	Label = Window.GetControl (0x10000009)
	Label.SetText (sdex)
	Label.SetColor (cdex)

	Label = Window.GetControl (0x1000000a)
	Label.SetText (scon)
	Label.SetColor (ccon)

	Label = Window.GetControl (0x1000000b)
	Label.SetText (sint)
	Label.SetColor (cint)

	Label = Window.GetControl (0x1000000c)
	Label.SetText (swis)
	Label.SetColor (cwis)

	Label = Window.GetControl (0x1000000d)
	Label.SetText (schr)
	Label.SetColor (cchr)

	# class
	ClassTitle = GUICommon.GetActorClassTitle (pc)
	Label = Window.GetControl (0x10000030)
	Label.SetText (ClassTitle)

	# race
	text = CommonTables.Races.GetValue (CommonTables.Races.FindValue (3, GemRB.GetPlayerStat (pc, IE_RACE)) , 0)

	Label = Window.GetControl (0x1000000f)
	Label.SetText (text)

	# alignment
	text = CommonTables.Aligns.FindValue (3, GemRB.GetPlayerStat (pc, IE_ALIGNMENT))
	text = CommonTables.Aligns.GetValue (text, 0)
	Label = Window.GetControl (0x10000010)
	Label.SetText (text)

	# gender
	Label = Window.GetControl (0x10000011)
	if GemRB.GetPlayerStat (pc, IE_SEX) == 1:
		Label.SetText (7198)
	else:
		Label.SetText (7199)

	# help, info textarea
	Text = Window.GetControl (45)
	Text.SetColor (ColorWhitish, TA_COLOR_INITIALS)
	Text.SetText (GetStatOverview (pc))
	#TODO: making window visible/shaded depending on the pc's state

	return

ToggleRecordsWindow = CreateTopWinLoader(2, "GUIREC", ToggleWindow, InitRecordsWindow, UpdateRecordsWindow, True)
OpenRecordsWindow = CreateTopWinLoader(2, "GUIREC", OpenWindowOnce, InitRecordsWindow, UpdateRecordsWindow, True)

#original returns to game before continuing...
def OpenRecReformPartyWindow ():
	ToggleRecordsWindow()
	PartyReform.OpenReformPartyWindow()
	return

#don't allow exporting polymorphed or dead characters
def Exportable(pc):
	if not (GemRB.GetPlayerStat (pc, IE_MC_FLAGS)&MC_EXPORTABLE): return False
	if GemRB.GetPlayerStat (pc, IE_POLYMORPHED): return False
	if GemRB.GetPlayerStat (pc, IE_STATE_ID)&STATE_DEAD: return False
	return True

def GetStatColor (pc, stat):
	a = GemRB.GetPlayerStat (pc, stat)
	b = GemRB.GetPlayerStat (pc, stat, 1)
	if a==b:
		return {'r' : 255, 'g' : 255, 'b' : 255}
	if a<b:
		return {'r' : 255, 'g' : 255, 'b' : 0}
	return {'r' : 0, 'g' : 255, 'b' : 0}

# shorthand wrappers for Modified/Base stat and ability bonus
def GS (pc, stat):
	return GemRB.GetPlayerStat (pc, stat)

def GB (pc, stat):
	return GemRB.GetPlayerStat (pc, stat, 1)

def GA (pc, stat, col):
	return GemRB.GetAbilityBonus (stat, col, GS (pc, stat))

# Basic full stat printout function for record sheet
# LevelDiff is used only from the level up code and holds the level
# difference for each class
def GetStatOverview (pc, LevelDiff=[0,0,0]):
	cdet = GemRB.GetCombatDetails (pc, 0)

	outputtext = GetClassTitles (pc,LevelDiff)
	outputtext+= GetEffectIcons (pc,LevelDiff)
	outputtext+= GetProficiencies (pc, cdet)
	outputtext+= GetLore (pc)
	outputtext+= GetMagicResistance (pc)
	outputtext+= GetPartyReputation (pc)
	outputtext+= GetSkills (pc)
	outputtext+= GetActiveAIscript (pc)
	outputtext+= GetSavingThrows (pc)
	outputtext+= GetWeaponProficiencies (pc)
	outputtext+= GetACBonuses (pc)
	outputtext+= GUIRECCommon.GetAbilityBonuses (pc)
	outputtext+= GUIRECCommon.GetBonusSpells (pc)
	outputtext+= GetResistances (pc)
	outputtext+= GetWeaponStyleBonuses (pc, cdet)

	return outputtext

########################################################################
# The following functions have been split into categories,
# so that they can be used for eg mouse over events  if desired
########################################################################
def GetClassTitles (pc,LevelDiff):
	# class levels
	# 16480 <CLASS>: Level <LEVEL>
	# Experience: <EXPERIENCE>
	# Next Level: <NEXTLEVEL>
	stats = []
	# collecting tokens for stat overview
	ClassTitle = GUICommon.GetActorClassTitle (pc)
	GemRB.SetToken ("CLASS", ClassTitle)
	Class = GUICommon.GetClassRowName (pc)
	Dual = GUICommon.IsDualClassed (pc, 1)
	Multi = GUICommon.IsMultiClassed (pc, 1)
	XP = GemRB.GetPlayerStat (pc, IE_XP)
	LevelDrain = GS (pc, IE_LEVELDRAIN)

	if GS (pc, IE_STATE_ID) & STATE_DEAD:
		stats.append ( (11829,1,'c') ) # DEAD
		stats.append ("\n")

	if Multi[0] > 1: # we're multiclassed
		print("\tMulticlassed")
		Levels = [GemRB.GetPlayerStat (pc, IE_LEVEL), GemRB.GetPlayerStat (pc, IE_LEVEL2), GemRB.GetPlayerStat (pc, IE_LEVEL3)]

		stats.append ( (19721,1,'c') )
		for i in range (Multi[0]):
			Class = GUICommon.GetClassRowName (Multi[i+1], "class")
			# level 1 npc mod kits some multiclasses
			Kit = GUICommon.GetKitIndex (pc)
			KitClass = CommonTables.KitList.GetValue (str(Kit), "CLASS", GTV_INT)
			if Kit and KitClass == Multi[i+1]:
				ClassTitle = CommonTables.KitList.GetValue (str(Kit), "MIXED", GTV_REF)
			else:
				ClassTitle = CommonTables.Classes.GetValue (Class, "CAP_REF", GTV_REF)
			GemRB.SetToken ("CLASS", ClassTitle)
			GemRB.SetToken ("LEVEL", str (Levels[i] + LevelDiff[i] - LevelDrain // Multi[0]))
			GemRB.SetToken ("EXPERIENCE", str (XP // Multi[0]) )
			if LevelDrain:
				stats.append ( (GemRB.GetString (19720),1,'d') )
				stats.append ( (GemRB.GetString (57435),1,'d') ) # LEVEL DRAINED
			else:
				GemRB.SetToken ("NEXTLEVEL", str(LUCommon.GetNextLevelExp (Levels[i]+LevelDiff[i], Class)))
				stats.append ( (GemRB.GetString (16480),"",'d') )
			stats.append ("\n")
			print("\t\tClass (Level): " + str(Class) + " (" + str(Levels[i]) + ")")

	elif Dual[0] > 0: # dual classed; first show the new class
		print("\tDual classed")
		stats.append ( (19722,1,'c') )

		Levels = [GemRB.GetPlayerStat (pc, IE_LEVEL), GemRB.GetPlayerStat (pc, IE_LEVEL2), GemRB.GetPlayerStat (pc, IE_LEVEL3)]

		# the levels are stored in the class order (eg. FIGHTER_MAGE)
		# the current active class does not matter!
		if GUICommon.IsDualSwap (pc):
			Levels = [Levels[1], Levels[0], Levels[2]]

		Levels[0] += LevelDiff[0]

		if Dual[0] == 3:
			ClassID = CommonTables.KitList.GetValue (Dual[2], 7)
			Class = GUICommon.GetClassRowName (ClassID, "class")
			ClassTitle = CommonTables.KitList.GetValue (Dual[2], 2, GTV_REF)
		else:
			Class = GUICommon.GetClassRowName (Dual[2], "index")
			ClassTitle = CommonTables.Classes.GetValue (Class, "CAP_REF", GTV_REF)
		GemRB.SetToken ("CLASS", ClassTitle)
		GemRB.SetToken ("LEVEL", str (Levels[0]-LevelDrain))
		XP2 = GemRB.GetPlayerStat (pc, IE_XP)
		GemRB.SetToken ("EXPERIENCE", str (XP2) )
		if LevelDrain:
			stats.append ( (GemRB.GetString (19720),1,'d') )
			stats.append ( (GemRB.GetString (57435),1,'d') ) # LEVEL DRAINED
		else:
			GemRB.SetToken ("NEXTLEVEL", str(LUCommon.GetNextLevelExp (Levels[0], Class)))
			stats.append ( (GemRB.GetString (16480),"",'d') )
		stats.append ("\n")

		# the first class (shown second)
		if Dual[0] == 1:
			ClassTitle = CommonTables.KitList.GetValue (Dual[1], 2, GTV_REF)
		else:
			Class = GUICommon.GetClassRowName (Dual[1], "index")
			ClassTitle = CommonTables.Classes.GetValue (Class, "CAP_REF", GTV_REF)
		GemRB.SetToken ("CLASS", ClassTitle)
		GemRB.SetToken ("LEVEL", str (Levels[1]) )

		# the xp table contains only classes, so we have to determine the base class for kits
		if Dual[0] > 1:
			BaseClass = CommonTables.Classes.GetRowName (Dual[1])
		else:
			BaseClass = GUICommon.GetKitIndex (pc)
			BaseClass = CommonTables.KitList.GetValue (BaseClass, 7)
			BaseClass = GUICommon.GetClassRowName (BaseClass, "class")
		# the first class' XP is discarded and set to the minimum level
		# requirement, so if you don't dual class right after a levelup,
		# the game would eat some of your XP
		XP1 = CommonTables.NextLevel.GetValue (BaseClass, str (Levels[1]))
		GemRB.SetToken ("EXPERIENCE", str (XP1) )

		# inactive until the new class SURPASSES the former
		if Levels[0] <= Levels[1]:
			# inactive
			stats.append ( (19719,1,'c') )
		else:
			stats.append ( (19720,1,'c') )
		stats.append ("\n")
	else: # single classed
		print("\tSingle classed")
		Level = GemRB.GetPlayerStat (pc, IE_LEVEL) + LevelDiff[0]
		GemRB.SetToken ("LEVEL", str (Level-LevelDrain))
		GemRB.SetToken ("EXPERIENCE", str (XP) )
		if LevelDrain:
			stats.append ( (19720,1,'c') )
			stats.append ( (57435,1,'c') ) # LEVEL DRAINED
		else:
			GemRB.SetToken ("NEXTLEVEL", str(LUCommon.GetNextLevelExp (Level, Class)))
			stats.append ( (16480,1,'c') )
		stats.append ("\n")
		print("\t\tClass (Level): " + str(Class) + " (" + str(Level) + ")")
	return GUIRECCommon.TypeSetStats (stats, pc)

########################################################################

def GetEffectIcons(pc,LevelDiff):

	StateTable = GemRB.LoadTable ("statdesc")
	stats = []

	# effect icons
	# but don't display them in levelup stat view
	if sum (LevelDiff) == 0:
		effects = GemRB.GetPlayerStates (pc)
		if len (effects):
			for c in effects:
				tmp = StateTable.GetValue (str(c - 66), "DESCRIPTION")
				stats.append ((tmp, c, 'a'))
	return GUIRECCommon.TypeSetStats (stats, pc)

########################################################################

def GetProficiencies(pc, cdet):

	stats = []
	tohit = cdet["ToHitStats"]

	#proficiencies
	stats.append ( (8442,1,'c') )

	# look ma, I can use both hands
	
	if GameCheck.IsBG2OrEE ():
		stats.append ( (61932, tohit["Base"], '0') )
		if (GemRB.IsDualWielding(pc)):
			stats.append ( (56911, tohit["Total"], '0') ) # main
			stats.append ( (56910, GemRB.GetCombatDetails(pc, 1)["ToHitStats"]["Total"], '0') ) # offhand
		else:
			stats.append ( (9457, tohit["Total"], '0') )
	else:
		stats.append ( (9457, str(tohit["Base"])+" ("+str(tohit["Total"])+")", '0') )

	tmp = cdet["APR"]
	tmp2 = str(tmp // 2)
	if (tmp&1):
		tmp2 += "[+int=" + str(189) + "]" #must use one higher than the frame count
	else:
		tmp2 += " " # add some trailing padding to ensure display in bg2

	stats.append ( (9458, tmp2, '') )
	return GUIRECCommon.TypeSetStats (stats, pc)

########################################################################

def GetLore(pc):
	stats = []
	lore = GemRB.GetPlayerStat (pc, IE_LORE)
	if lore < 0:
		lore = 0
	stats.append ( (9459, lore, '0') )
	return GUIRECCommon.TypeSetStats (stats, pc)

########################################################################

def GetMagicResistance(pc):
	stats = []

	if GameCheck.IsBG1() or GameCheck.IsIWD1():
		stats.append ( (19224, GS (pc, IE_RESISTMAGIC), '') )
	return GUIRECCommon.TypeSetStats (stats, pc)

########################################################################

def GetPartyReputation(pc):
	stats = []
	# party's reputation
	reptxt = GetReputation (GemRB.GameGetReputation () // 10)
	stats.append ( (9465, reptxt, '') )
	return GUIRECCommon.TypeSetStats (stats, pc)

########################################################################

def GetSkills(pc):
	stats = []
	className = GUICommon.GetClassRowName (pc)
	stats.append ( (9460, GUIRECCommon.GetValidSkill (pc, className, IE_LOCKPICKING), '') )
	stats.append ( (9462, GUIRECCommon.GetValidSkill (pc, className, IE_TRAPS), '') )
	stats.append ( (9463, GUIRECCommon.GetValidSkill (pc, className, IE_PICKPOCKET), '') )
	stats.append ( (9461, GUIRECCommon.GetValidSkill (pc, className, IE_STEALTH), '') )
	HatedRace = GS (pc, IE_HATEDRACE)
	if HatedRace:
		HateTable = GemRB.LoadTable ("haterace")
		Racist = HateTable.FindValue (1, HatedRace)
		if Racist is not None:
			HatedRace = HateTable.GetValue (Racist, 0, GTV_REF)
			stats.append ( (15982, HatedRace, '') )

	# these skills were new in bg2
	if GameCheck.IsBG2OrEE () or GameCheck.IsIWD1():
		stats.append ( (34120, GUIRECCommon.GetValidSkill (pc, className, IE_HIDEINSHADOWS), '') )
		stats.append ( (34121, GUIRECCommon.GetValidSkill (pc, className, IE_DETECTILLUSIONS), '') )
		stats.append ( (34122, GUIRECCommon.GetValidSkill (pc, className, IE_SETTRAPS), '') )
	stats.append ( (12128, GS (pc, IE_BACKSTABDAMAGEMULTIPLIER), 'x') )
	stats.append ( (12126, GS (pc, IE_TURNUNDEADLEVEL), '') )

	# the original ignored layhands.2da, hardcoding the values and display
	# the table has only a class entry, not kits
	# the values are handled by the spell, but there is an unused stat too
	if (Spellbook.HasSpell (pc, IE_SPELL_TYPE_INNATE, 0, "SPCL211") >= 0):
		stats.append ( (12127, GS (pc, IE_LAYONHANDSAMOUNT), '') )
	return GUIRECCommon.TypeSetStats (stats, pc)

########################################################################

def GetActiveAIscript(pc):
	#script
	stats = []
	aiscript = GemRB.GetPlayerScript (pc )
	stats.append ( (2078, aiscript, '') )
	stats.append ("\n")
	return GUIRECCommon.TypeSetStats (stats, pc)

########################################################################

def GetSavingThrows(pc):
	stats = []
	# 17379 Saving throws
	stats.append (17379)
	# 17380 Paralyze/Poison/Death
	stats.append ( (17380, IE_SAVEVSDEATH, 's') )
	# 17381 Rod/Staff/Wand
	stats.append ( (17381, IE_SAVEVSWANDS, 's') )
	# 17382 Petrify/Polymorph
	stats.append ( (17382, IE_SAVEVSPOLY, 's') )
	# 17383 Breath weapon
	stats.append ( (17383, IE_SAVEVSBREATH, 's') )
	# 17384 Spells
	stats.append ( (17384, IE_SAVEVSSPELL, 's') )
	stats.append ("\n\n")
	return GUIRECCommon.TypeSetStats (stats, pc)

########################################################################

def GetWeaponProficiencies(pc):
	stats = []
	# 9466 Weapon proficiencies
	stats.append (9466)
	table = GemRB.LoadTable ("weapprof")
	RowCount = table.GetRowCount ()
	# the first 7 profs are foobared (bg1 style)
	if GameCheck.IsBG2OrEE ():
		offset = 8
	else:
		offset = 0
	for i in range (offset, RowCount):
		# iwd has separate field for capitalised strings
		if GameCheck.IsIWD1():
			text = table.GetValue (i, 3, GTV_INT)
		else:
			text = table.GetValue (i, 1, GTV_INT)
		stat = table.GetValue (i, 0)
		if GameCheck.IsBG1():
			stat = stat + IE_PROFICIENCYBASTARDSWORD
		stats.append ( (text, GS (pc, stat)&0x07, '+') )
	stats.append ("\n")
	return GUIRECCommon.TypeSetStats (stats, pc)

########################################################################

def GetACBonuses(pc):
	stats = []
	# 11766 AC Bonuses
	stats.append (11766)
	# 11770 AC vs. Crushing
	stats.append ((11770, GS (pc, IE_ACCRUSHINGMOD), 'p'))
	# 11767 AC vs. Missile
	stats.append ((11767, GS (pc, IE_ACMISSILEMOD), 'p'))
	# 11769 AC vs. Piercing
	stats.append ((11769, GS (pc, IE_ACPIERCINGMOD), 'p'))
	# 11768 AC vs. Slashing
	stats.append ((11768, GS (pc, IE_ACSLASHINGMOD), 'p'))
	stats.append ("\n")
	return GUIRECCommon.TypeSetStats (stats, pc)

########################################################################

def GetResistances(pc):
	stats = []
	# only bg2 displayed all the resistances, but it is useful information
	# Resistances
	if GameCheck.IsBG2OrEE ():
		stats.append(32204)
	elif not GameCheck.IsBG1():
		stats.append (15544)
	# 32213 Normal Fire
	# 32222 Magic Fire
	# 32214 Normal Cold
	# 32223 Magic Cold
	if GameCheck.IsBG2OrEE ():
		stats.append ((32213, GS (pc, IE_RESISTFIRE), '%'))
		stats.append ((32222, GS (pc, IE_RESISTMAGICFIRE), '%'))
		stats.append ((32214, GS (pc, IE_RESISTCOLD), '%'))
		stats.append ((32223, GS (pc, IE_RESISTMAGICCOLD), '%'))
	elif GameCheck.IsBG1():
		stats.append ((14012, GS (pc, IE_RESISTFIRE), '%'))
		stats.append ((14077, GS (pc, IE_RESISTMAGICFIRE), '%'))
		stats.append ((14014, GS (pc, IE_RESISTCOLD), '%'))
		stats.append ((14078, GS (pc, IE_RESISTMAGICCOLD), '%'))
	else:
		stats.append ((15545, GS (pc, IE_RESISTFIRE), '%'))
		stats.append ((15579, GS (pc, IE_RESISTMAGICFIRE), '%'))
		stats.append ((15546, GS (pc, IE_RESISTCOLD), '%'))
		stats.append ((15580, GS (pc, IE_RESISTMAGICCOLD), '%'))
	# 32220 Electricity
	if GameCheck.IsBG1() or GameCheck.IsIWD1():
		stats.append ((14013, GS (pc, IE_RESISTELECTRICITY), '%'))
	else:
		stats.append ((32220, GS (pc, IE_RESISTELECTRICITY), '%'))
	# 32221 Acid
	if GameCheck.IsBG1() or GameCheck.IsIWD1():
		stats.append ((14015, GS (pc, IE_RESISTACID), '%'))
	else:
		stats.append ((32221, GS (pc, IE_RESISTACID), '%'))
	if GameCheck.IsBG2OrEE ():
		# Magic (others show it higher up)
		stats.append ((62146, GS (pc, IE_RESISTMAGIC), '%'))
	# Magic Damage
	if GameCheck.IsIWD2():
		stats.append ((40319, GS (pc, IE_MAGICDAMAGERESISTANCE), '%'))
	else: # bg2
		stats.append ((32233, GS (pc, IE_MAGICDAMAGERESISTANCE), '%'))
	# Missile
	stats.append ((11767, GS (pc, IE_RESISTMISSILE), '%'))
	# Slashing
	stats.append ((11768, GS (pc, IE_RESISTSLASHING), '%'))
	# Piercing
	stats.append ((11769, GS (pc, IE_RESISTPIERCING), '%'))
	# Crushing
	stats.append ((11770, GS (pc, IE_RESISTCRUSHING), '%'))
	# Poison
	stats.append ((14017, GS (pc, IE_RESISTPOISON), '%'))
	stats.append ("\n")

	return GUIRECCommon.TypeSetStats (stats, pc)

########################################################################

def GetWeaponStyleBonuses(pc, cdet):

	stats = []
	if GameCheck.IsBG2OrEE ():
		# Weapon Style bonuses
		stats.append (32131)
		wstyle = cdet["Style"] # equipped weapon style + 1000 * proficiency level
		profcount = wstyle // 1000
		if profcount:
			wstyletables = { IE_PROFICIENCY2WEAPON:"wstwowpn", IE_PROFICIENCY2HANDED:"wstwohnd", IE_PROFICIENCYSINGLEWEAPON:"wssingle", IE_PROFICIENCYSWORDANDSHIELD:"wsshield" }
			bonusrefs = { "THAC0BONUSRIGHT":56911, "THAC0BONUSLEFT":56910, "DAMAGEBONUS":10336, "CRITICALHITBONUS":32140, "PHYSICALSPEED":32141, "AC":10339, "ACVSMISSLE":10340 }
			WStyleTable = GemRB.LoadTable (wstyletables[wstyle % 1000])
			for col in range(WStyleTable.GetColumnCount()):
				colName = WStyleTable.GetColumnName (col);
				value = WStyleTable.GetValue (str(profcount), colName, GTV_INT)
				stats.append ((bonusrefs[colName], value, ''))
		stats.append ("\n")
	return GUIRECCommon.TypeSetStats (stats, pc)

def GetReputation (repvalue):
	table = GemRB.LoadTable ("reptxt")
	if repvalue>20:
		repvalue=20
	txt = table.GetValue (repvalue, 0, GTV_REF)
	return txt+" ("+str (repvalue)+")"

def OpenInformationWindow ():
	global InformationWindow

	InformationWindow = Window = GemRB.LoadWindow (4, "GUIREC")

	# Biography
	Button = Window.GetControl (26)
	Button.SetText (18003)
	Button.OnPress (GUIRECCommon.OpenBiographyWindow)

	# Done
	Button = Window.GetControl (24)
	Button.SetText (11973)
	Button.OnPress (InformationWindow.Close)
	Button.MakeEscape()

	TotalPartyExp = 0
	ChapterPartyExp = 0
	TotalPartyKills = 0
	ChapterCount = 0
	for i in range (1, GemRB.GetPartySize () + 1):
		stat = GemRB.GetPCStats(i)
		TotalPartyExp = TotalPartyExp + stat['KillsTotalXP']
		ChapterPartyExp = ChapterPartyExp + stat['KillsChapterXP']
		TotalPartyKills = TotalPartyKills + stat['KillsTotalCount']
		ChapterCount = ChapterCount + stat['KillsChapterCount']

	# These are used to get the stats
	pc = GemRB.GameGetSelectedPCSingle ()
	stat = GemRB.GetPCStats (pc)

	Label = Window.GetControl (0x10000000)
	Label.SetText (GemRB.GetPlayerName (pc, 1))
	# class
	ClassTitle = GUICommon.GetActorClassTitle (pc)
	Label = Window.GetControl (0x10000018)
	Label.SetText (ClassTitle)

	#most powerful vanquished
	Label = Window.GetControl (0x10000005)
	#we need getstring, so -1 will translate to empty string
	Label.SetText (GemRB.GetString (stat['BestKilledName']))

	Label = Window.GetControl (0x10000006)
	time = GUICommon.SetCurrentDateTokens (stat)
	Label.SetText (time)

	#favourite spell
	Label = Window.GetControl (0x10000007)
	Label.SetText (stat['FavouriteSpell'])

	#favourite weapon
	Label = Window.GetControl (0x10000008)
	#actually it is 10479 <WEAPONNAME>, but weaponname is translated to
	#the real weapon name (which we should set using SetToken)
	#there are other strings like bow+wname/xbow+wname/sling+wname
	#are they used?
	Label.SetText (stat['FavouriteWeapon'])

	#total party xp
	Label = Window.GetControl (0x10000013)
	if TotalPartyExp != 0:
		PartyExp = int ((stat['KillsTotalXP'] * 100) / TotalPartyExp)
		Label.SetText (str (PartyExp) + '%')
	else:
		Label.SetText ("0%")

	# chapter party xp
	Label = Window.GetControl (0x1000000f)
	if ChapterPartyExp != 0:
		PartyExp = int ((stat['KillsChapterXP'] * 100) / ChapterPartyExp)
		Label.SetText (str (PartyExp) + '%')
	else:
		Label.SetText ("0%")

	# total kills
	Label = Window.GetControl (0x10000014)
	if TotalPartyKills != 0:
		PartyKills = int ((stat['KillsTotalCount'] * 100) / TotalPartyKills)
		Label.SetText (str (PartyKills) + '%')
	else:
		Label.SetText ("0%")

	# chapter kills
	Label = Window.GetControl (0x10000010)
	if ChapterCount != 0:
		PartyKills = int ((stat['KillsChapterCount'] * 100) / ChapterCount)
		Label.SetText (str (PartyKills) + '%')
	else:
		Label.SetText ("0%")

	Label = Window.GetControl (0x10000011)
	Label.SetText (str (stat['KillsChapterXP']))
	Label = Window.GetControl (0x10000015)
	Label.SetText (str (stat['KillsTotalXP']))

	#count of kills in chapter/game
	Label = Window.GetControl (0x10000012)
	Label.SetText (str (stat['KillsChapterCount']))
	Label = Window.GetControl (0x10000016)
	Label.SetText (str (stat['KillsTotalCount']))

	Window.ShowModal (MODAL_SHADOW_GRAY)
	return

def OpenKitInfoWindow ():
	global KitInfoWindow

	KitInfoWindow = GemRB.LoadWindow (24, "GUIREC")

	#back button (setting first, to be less error prone)
	DoneButton = KitInfoWindow.GetControl (2)
	DoneButton.SetText (11973)
	DoneButton.OnPress (KitDonePress)

	#kit or class description
	TextArea = KitInfoWindow.GetControl (0)

	pc = GemRB.GameGetSelectedPCSingle ()
	ClassName = GUICommon.GetClassRowName (pc)
	Multi = GUICommon.HasMultiClassBits (pc)
	Dual = GUICommon.IsDualClassed (pc, 1)
	text = ""
	if Multi and Dual[0] == 0: # true multi class
		text = CommonTables.Classes.GetValue (ClassName, "DESC_REF")
	else:
		KitIndex = GUICommon.GetKitIndex (pc)

		if Dual[0]: # dual class
			# first (previous) kit or class of the dual class
			if Dual[0] == 1:
				text = CommonTables.KitList.GetValue (Dual[1], 3, GTV_REF)
			else:
				text = CommonTables.Classes.GetValue (GUICommon.GetClassRowName(Dual[1], "index"), "DESC_REF", GTV_REF)
	
			text += "\n\n"
			if Dual[0] == 3:
				text += CommonTables.KitList.GetValue (Dual[2], 3, GTV_REF)
			else:
				text += CommonTables.Classes.GetValue (GUICommon.GetClassRowName(Dual[2], "index"), "DESC_REF", GTV_REF)
	
		else: # ordinary class or kit
			if KitIndex:
				text = CommonTables.KitList.GetValue (KitIndex, 3)
			else:
				text = CommonTables.Classes.GetValue (ClassName, "DESC_REF")

	TextArea.SetText (text)

	KitInfoWindow.ShowModal (MODAL_SHADOW_GRAY)
	return

def KitDonePress():
	if KitInfoWindow:
		KitInfoWindow.Close ()
	return

def OpenColorWindow ():
	global PaperdollButton
	global HairButton, SkinButton, MajorButton, MinorButton
	global HairColor, SkinColor, MajorColor, MinorColor

	pc = GemRB.GameGetSelectedPCSingle ()
	MinorColor = GemRB.GetPlayerStat (pc, IE_MINOR_COLOR)
	MajorColor = GemRB.GetPlayerStat (pc, IE_MAJOR_COLOR)
	SkinColor = GemRB.GetPlayerStat (pc, IE_SKIN_COLOR)
	HairColor = GemRB.GetPlayerStat (pc, IE_HAIR_COLOR)
	Window = GemRB.LoadWindow (21, "GUIREC")
	Window.AddAlias("SUB_WIN", 0)

	PaperdollButton = Window.GetControl (0)
	PaperdollButton.SetFlags (IE_GUI_BUTTON_PICTURE|IE_GUI_BUTTON_NO_IMAGE,OP_SET)
	PaperdollButton.SetState (IE_GUI_BUTTON_LOCKED)

	HairButton = Window.GetControl (3)
	SkinButton = Window.GetControl (4)
	MajorButton = Window.GetControl (5)
	MinorButton = Window.GetControl (6)

	DoneButton = Window.GetControl (12)
	DoneButton.SetText (11973)
	DoneButton.MakeDefault()

	CancelButton = Window.GetControl (13)
	CancelButton.SetText (13727)
	CancelButton.MakeEscape()

	HairButton.OnPress (SetHairColor)
	SkinButton.OnPress (SetSkinColor)
	MajorButton.OnPress (SetMajorColor)
	MinorButton.OnPress (SetMinorColor)
	DoneButton.OnPress (DoneColorWindow)
	CancelButton.OnPress (Window.Close)
	UpdatePaperDoll ()

	Window.ShowModal (MODAL_SHADOW_GRAY)
	return

def DoneColorWindow ():
	pc = GemRB.GameGetSelectedPCSingle ()
	GemRB.SetPlayerStat (pc, IE_MINOR_COLOR, MinorColor)
	GemRB.SetPlayerStat (pc, IE_MAJOR_COLOR, MajorColor)
	GemRB.SetPlayerStat (pc, IE_SKIN_COLOR, SkinColor)
	GemRB.SetPlayerStat (pc, IE_HAIR_COLOR, HairColor)
	GemRB.GetView("SUB_WIN", 0).Close()
	return

def UpdatePaperDoll ():
	pc = GemRB.GameGetSelectedPCSingle ()
	Color1 = GemRB.GetPlayerStat (pc, IE_METAL_COLOR)
	MinorButton.SetBAM ("COLGRAD", 0, 0, MinorColor&0xff)
	MajorButton.SetBAM ("COLGRAD", 0, 0, MajorColor&0xff)
	SkinButton.SetBAM ("COLGRAD", 0, 0, SkinColor&0xff)
	Color5 = GemRB.GetPlayerStat (pc, IE_LEATHER_COLOR)
	Color6 = GemRB.GetPlayerStat (pc, IE_ARMOR_COLOR)
	HairButton.SetBAM ("COLGRAD", 0, 0, HairColor&0xff)
	PaperdollButton.SetPLT (GUICommon.GetActorPaperDoll (pc),
		Color1, MinorColor, MajorColor, SkinColor, Color5, Color6, HairColor, 0, 0)
	return

def SetHairColor ():
	global ColorIndex, PickedColor

	ColorIndex = 0
	PickedColor = HairColor
	OpenColorPicker ()
	return

def SetSkinColor ():
	global ColorIndex, PickedColor

	ColorIndex = 1
	PickedColor = SkinColor
	OpenColorPicker ()
	return

def SetMinorColor ():
	global ColorIndex, PickedColor

	ColorIndex = 2
	PickedColor = MinorColor
	OpenColorPicker ()
	return

def SetMajorColor ():
	global ColorIndex, PickedColor

	ColorIndex = 3
	PickedColor = MajorColor
	OpenColorPicker ()
	return

def OpenColorPicker ():
	Window = GemRB.LoadWindow (22, "GUIREC")
	Window.AddAlias("SUB_WIN", 1)

	GemRB.SetVar ("Selected", None)
	for i in range (1,35):
		Button = Window.GetControl (i)
		Button.SetState (IE_GUI_BUTTON_LOCKED)
		Button.SetFlags (IE_GUI_BUTTON_PICTURE,OP_OR)

	for i in range (34):
		MyColor = ColorTable.GetValue (ColorIndex, i)
		if MyColor == "*":
			break
		Button = Window.GetControl (i+1)
		Button.SetBAM("COLGRAD", 2, 0, MyColor)
		if PickedColor == MyColor:
			GemRB.SetVar ("Selected",i)
		Button.SetState (IE_GUI_BUTTON_ENABLED)
		Button.SetVarAssoc("Selected",i)
		Button.OnPress (DonePress)

	Window.ShowModal (MODAL_SHADOW_GRAY)
	return

def DonePress():
	global HairColor, SkinColor, MajorColor, MinorColor
	global PickedColor

	GemRB.GetView("SUB_WIN", 1).Close()
	PickedColor=ColorTable.GetValue (ColorIndex, GemRB.GetVar ("Selected"))
	if ColorIndex==0:
		HairColor=PickedColor
		UpdatePaperDoll ()
		return
	if ColorIndex==1:
		SkinColor=PickedColor
		UpdatePaperDoll ()
		return
	if ColorIndex==2:
		MinorColor=PickedColor
		UpdatePaperDoll ()
		return

	MajorColor=PickedColor
	UpdatePaperDoll ()
	return

###################################################
# End of file GUIREC.py
