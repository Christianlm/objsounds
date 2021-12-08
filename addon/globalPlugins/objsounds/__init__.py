# -*- coding: UTF-8 -*-

# objsounds addon for NVDA created by Tyler Spivey.
# Version 21.11.14-dev.
# Last update by Chris Leo <llajta2012@gmail.com> on 14 nov 2021.
# Copyright (C)2019-2021.
# Released under GPL 2
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import addonHandler
import os
import winsound
import globalPluginHandler
import speech
import config
import ui
import scriptHandler
from scriptHandler import script
from globalCommands import SCRCAT_TOOLS, SCRCAT_CONFIG
from . import objdata

# Suggested by @ABuffEr https://nvda-addons.groups.io/g/nvda-addons/message/17328

import controlTypes as ct
if hasattr(ct, "Role"):
	for r in ct.Role: setattr(ct, r.__str__().replace("Role.", "ROLE_"), r)
else:
	setattr(ct, Role, type('Enum', (), dict([(x.split("ROLE_")[1], getattr(ct, x)) for x in dir(ct) if x.startswith("ROLE_")])))
if hasattr(ct, "Role"):
	for r in ct.OutputReason:
		setattr(ct, r.__str__().replace("OutputReason.", "REASON_"), r)
else:
	setattr(ct, OutputReason, type('Enum', (), dict([(x.split("REASON_")[1], getattr(ct, x)) for x in dir(ct) if x.startswith("REASON_")])))

addonHandler.initTranslation()

#The part that turns off the role announcement is a huge hack, and might break. Set this to False to get rid of it
hook = True
loc = os.path.abspath(os.path.dirname(objdata.__file__))
old = None

def getPropertiesSpeech2(reason=ct.OutputReason.QUERY, *args, **kwargs):
	role = kwargs.get('role', None)
	if 'role' in kwargs and role in sounds and os.path.exists(sounds[role]):
		del kwargs['role']
	return old(reason, *args, **kwargs)

def play(role):
	"""plays sound for role."""
	f = sounds[role]
	if os.path.exists(f):
		winsound.PlaySound(f, winsound.SND_ASYNC)

#Add all the roles, looking for name.wav.
sounds = {}
for role in [x for x in dir(ct) if x.startswith('ROLE_')]:
	r = os.path.join(loc, role[5:].lower()+".wav")
	sounds[getattr(ct, role)] = r
 
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self, *args, **kwargs):
		globalPluginHandler.GlobalPlugin.__init__(self, *args, **kwargs)
		global old
		old = speech.getPropertiesSpeech
		if 'objsounds' not in config.conf:
			config.conf['objsounds'] = {"enabled": True}

	def event_gainFocus(self, obj, nextHandler):
		##huge hack. Why is configobj not saving the boolean as a boolean?
		if config.conf['objsounds']['enabled'] == u'False' or config.conf['objsounds']['enabled'] == False:
			nextHandler()
			return
		if hook:
			speech.getPropertiesSpeech = getPropertiesSpeech2
		play(obj.role)
		nextHandler()
		if hook:
			speech.getPropertiesSpeech = old

	@script(
		# Translators: Message presented in input help mode.
		description=_("Turns off obj sound"),
		category = SCRCAT_TOOLS,
		gesture="kb:NVDA+shift+delete"
	)
	def script_toggle(self, gesture):
		config.conf['objsounds']['enabled'] = not (str2bool(config.conf['objsounds']['enabled']))
		if config.conf['objsounds']['enabled']:
			ui.message(_("on"))
		else:
			ui.message(_("off"))

def str2bool(s):
	if s == 'True' or s == True: return True
	if s == 'False' or s == False: return False
