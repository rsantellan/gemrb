# GemRB - Infinity Engine Emulator
# Copyright (C) 2003 The GemRB Project
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#


# GUIJRNL.py - scripts to control journal/diary windows from GUIJRNL winpack

# GUIJRNL:
# 0 - main journal window
# 1 - quests window
# 2 - beasts window
# 3 - log/diary window

###################################################
import GemRB
import GUICommon
import GUICommonWindows
from GUIDefines import *

# list of all assigned (0) or completed (1) quests
global quests
quests = [ [], [] ]

# whether user has chosen assigned (0) or completed (1) quests
global selected_quest_class
selected_quest_class = 0

# list of all PC (0) or NPC (1) beasts/creatures
global beasts
beasts = [ [], [] ]

# whether user has chosen PC (0) or NPC (1) beasts
global selected_beast_class
selected_beast_class = 0

global BeastImage
BeastImage = None
StartTime = 0

###################################################
def InitJournalWindow (JournalWindow):
	global StartTime

	Table = GemRB.LoadTable("YEARS")
	StartTime = Table.GetValue("STARTTIME", "VALUE")

	# Quests
	Button = JournalWindow.GetControl (0)
	Button.SetText (20430)
	Button.OnPress (OpenQuestsWindow)

	# Beasts
	Button = JournalWindow.GetControl (1)
	Button.SetText (20634)
	Button.OnPress (OpenBeastsWindow)

	# Journal
	Button = JournalWindow.GetControl (2)
	Button.SetText (20635)
	Button.OnPress (OpenLogWindow)

	# Done
	Button = JournalWindow.GetControl (3)
	Button.SetText (20636)
	Button.OnPress (JournalWindow.Close)
	Button.MakeEscape()

	return

ToggleJournalWindow = GUICommonWindows.CreateTopWinLoader(0, "GUIJRNL", GUICommonWindows.ToggleWindow, InitJournalWindow)
OpenJournalWindow = GUICommonWindows.CreateTopWinLoader(0, "GUIJRNL", GUICommonWindows.OpenWindowOnce, InitJournalWindow)

def CloseAll(win):
	win.Close ()
	GUICommonWindows.CloseTopWindow ()

###################################################
def OpenQuestsWindow ():
	global QuestsList, QuestDesc
	
	QuestsWindow = GemRB.LoadWindow (1, "GUIJRNL")
	
	def OnJournalAssignedPress ():
		global selected_quest_class

		# Assigned Quests
		Label = QuestsWindow.GetControl (0x10000005)
		Label.SetText (38585)

		selected_quest_class = 0
		PopulateQuestsList ()
		
	def OnJournalCompletedPress ():
		global selected_quest_class

		# Completed Quests
		Label = QuestsWindow.GetControl (0x10000005)
		Label.SetText (39527)

		selected_quest_class = 1
		PopulateQuestsList ()

	# Assigned
	Button = QuestsWindow.GetControl (8)
	Button.SetText (39433)
	Button.OnPress (OnJournalAssignedPress)

	# Completed
	Button = QuestsWindow.GetControl (9)
	Button.SetText (39434)
	Button.OnPress (OnJournalCompletedPress)

	# Back
	Button = QuestsWindow.GetControl (5)
	Button.SetText (46677)
	Button.OnPress (QuestsWindow.Close)
	Button.MakeEscape()
	Button.Focus()

	# Done
	Button = QuestsWindow.GetControl (0)
	Button.SetText (20636)
	Button.OnPress (lambda: CloseAll(QuestsWindow))

	QuestsList = List = QuestsWindow.GetControl (1)
	List.SetVarAssoc ('SelectedQuest', None)
	List.OnSelect (OnJournalQuestSelect)

	QuestDesc = QuestsWindow.GetControl (3)

	EvaluateAllQuests ()
	PopulateQuestsList ()
	

def OnJournalQuestSelect ():
	row = GemRB.GetVar ('SelectedQuest')
	q = quests[selected_quest_class][row]
	QuestDesc.SetText (int (q[1])) 
	
def PopulateQuestsList ():
	GemRB.SetVar ('SelectedQuest', None)
	QuestDesc.Clear ()
	
	lookup = lambda quest: int(GemRB.GetINIQuestsKey (str (quest[0]), 'title', '0'))
	opts = ['- ' + GemRB.GetString(lookup(q)) for q in quests[selected_quest_class]]
	QuestsList.SetOptions(opts)
	
def EvaluateCondition (var, value, condition):
	cur_value = int (GemRB.GetGameVar (var))

	if condition == 'EQ':
		return cur_value == int (value)
	if condition == 'NE':
		return cur_value != int (value)
	elif condition == 'GT':
		return cur_value > int (value)
	elif condition == 'LT':
		return cur_value < int (value)
	else:
		print('Unknown condition in quests.ini:', condition)
		return None

def EvaluateQuest (index):
	tag = str (index)

	endings = int (GemRB.GetINIQuestsKey (tag, 'possibleEndings', '1'))

	for e in range (endings):
		if e == 0:
			suff = ''
		else:
			suff = chr (ord ('A') + e)

		completed = 1
		cc = int (GemRB.GetINIQuestsKey (tag, 'completeChecks' + suff, '0'))
		for i in range (1, cc + 1):
			var = GemRB.GetINIQuestsKey (tag, 'cVar' + suff + str (i), '')
			value = GemRB.GetINIQuestsKey (tag, 'cValue' + suff + str (i), '0')
			condition = GemRB.GetINIQuestsKey (tag, 'cCondition' + suff + str (i), 'EQ')

			completed = completed and EvaluateCondition (var, value, condition)

			if not completed: break

		if completed:
			desc = GemRB.GetINIQuestsKey (tag, 'descCompleted' + suff, '0')
			return (1, desc)


	assigned = 1
	ac = int (GemRB.GetINIQuestsKey (tag, 'assignedChecks', '0'))
	for i in range (1, ac + 1):
		var = GemRB.GetINIQuestsKey (tag, 'aVar' + str (i), '')
		value = GemRB.GetINIQuestsKey (tag, 'aValue' + str (i), '0')
		condition = GemRB.GetINIQuestsKey (tag, 'aCondition' + str (i), 'EQ')

		assigned = assigned and EvaluateCondition (var, value, condition)

		if not assigned: break

	if assigned:
		desc = GemRB.GetINIQuestsKey (tag, 'descAssigned', '0')
		return (0, desc)

	return None


def EvaluateAllQuests ():
	del quests[0][:]
	del quests[1][:]

	count = int (GemRB.GetINIQuestsKey ('init', 'questcount', '0'))
	for i in range (count):
		res = EvaluateQuest (i)
		if res:
			quests[res[0]].append ((i, res[1]))
			

###################################################

def OpenBeastsWindow ():
	global BeastsList, BeastImage, BeastDesc
	
	BeastsWindow = GemRB.LoadWindow (2, "GUIJRNL")

	# PC
	Button = BeastsWindow.GetControl (5)
	Button.SetText (20637)
	Button.OnPress (OnJournalPCPress)

	# NPC
	Button = BeastsWindow.GetControl (6)
	Button.SetText (20638)
	Button.OnPress (OnJournalNPCPress)

	# Back
	Button = BeastsWindow.GetControl (7)
	Button.SetText (46677)
	Button.OnPress (BeastsWindow.Close)
	Button.MakeEscape()
	Button.Focus()

	# Done
	Button = BeastsWindow.GetControl (4)
	Button.SetText (20636)
	Button.OnPress (lambda: CloseAll(BeastsWindow))

	BeastsList = List = BeastsWindow.GetControl (0)
	List.SetVarAssoc ('SelectedBeast', None)
	List.OnSelect (OnJournalBeastSelect)

	BeastImage = BeastsWindow.CreateButton (8, 19, 19, 281, 441)
	BeastImage.SetFlags (IE_GUI_BUTTON_PICTURE | IE_GUI_BUTTON_NO_IMAGE, OP_SET)

	BeastDesc = BeastsWindow.GetControl (2)
	
	EvaluateAllBeasts ()
	PopulateBeastsList ()
	
	return

def OnJournalBeastSelect ():
	row = GemRB.GetVar ('SelectedBeast')
	b = beasts[selected_beast_class][row]
	
	desc = GemRB.GetINIBeastsKey (str (b), 'desc0', '0')
	BeastDesc.SetText (int (desc)) 

	image = GemRB.GetINIBeastsKey (str (b), 'imageKnown', '')
	BeastImage.SetPicture (image)
	
def OnJournalPCPress ():
	global selected_beast_class

	selected_beast_class = 0
	PopulateBeastsList ()
	
def OnJournalNPCPress ():
	global selected_beast_class

	selected_beast_class = 1
	PopulateBeastsList ()


def PopulateBeastsList ():
	GemRB.SetVar ('SelectedBeast', None)
	BeastDesc.Clear ()
	BeastImage.SetPicture ('default')

	lookup = lambda beast: int(GemRB.GetINIBeastsKey (str (beast), 'name', '0'))
	opts = [GemRB.GetString(lookup(b)) for b in beasts[selected_beast_class]]
	BeastsList.SetOptions(opts)

def EvaluateAllBeasts ():
	del beasts[0][:]
	del beasts[1][:]

	count = int (GemRB.GetINIBeastsKey ('init', 'beastcount', '0'))
	
	for i in range (count):
		if not GemRB.GameIsBeastKnown (i):
			continue

		klass = int (GemRB.GetINIBeastsKey (str (i), 'class', '0'))
		beasts[klass].append (i)
		
	beasts[0].sort()
	beasts[1].sort()


###################################################

def OpenLogWindow ():
	LogWindow = GemRB.LoadWindow (3, "GUIJRNL")

	# Back
	Button = LogWindow.GetControl (1)
	Button.SetText (46677)
	Button.OnPress (LogWindow.Close)
	Button.MakeEscape()
	Button.Focus()

	# Done
	Button = LogWindow.GetControl (0)
	Button.SetText (20636)
	Button.OnPress (lambda: CloseAll(LogWindow))

	# text area
	Text = LogWindow.GetControl (2)

	# limit the log to the last entries (original did something similar)
	js = GemRB.GetJournalSize (0)
	frame = 250
	journalText = ""
	for i in range (js-frame, js):
		je = GemRB.GetJournalEntry (0, i)

		if je == None:
			continue

		# FIXME: the date computed here is wrong by approx. time
		#   of the first journal entry compared to journal in
		#   orig. game. So it's probably computed since "awakening"
		#   there instead of start of the day.

		gt = StartTime + je["GameTime"]
		dt = int (gt/86400)
		date = str (1 + dt)
		#time = str (gt - dt*86400)
		
		journalText += "[color=FFFF00]" + GemRB.GetString(19310)+" "+date+":[/color]"
		journalText += " " + GemRB.GetString (je['Text']) + "\n\n"
			
	Text.SetText (journalText)
	LogWindow.Focus()
	
###################################################
# End of file GUIJRNL.py
