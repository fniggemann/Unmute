# settings.py
# A part of the NVDA Unmute add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020-2021 Olexandr Gryshchenko <grisov.nvaccess@mailnull.com>

import addonHandler
import gui
from gui import guiHelper, nvdaControls
import wx
import config
from typing import Callable
from logHandler import log
from . import addonName, addonSummary

try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	log.warning("Unable to init translations. This may be because the addon is running from NVDA scratchpad.")
_: Callable[[str], str]


class UnmuteSettingsPanel(gui.SettingsPanel):
	"""Add-on settings panel object"""
	title: str = addonSummary

	def __init__(self, parent: wx.Window) -> None:
		"""Initializing the add-on settings panel object.
		@param parent: parent top level window
		@type parent: wx.Window
		"""
		super(UnmuteSettingsPanel, self).__init__(parent)

	def makeSettings(self, sizer: wx.Sizer) -> None:
		"""Populate the panel with settings controls.
		@param sizer: The sizer to which to add the settings controls.
		@type sizer: wx.Sizer
		"""
		self.sizer = sizer
		helpLabel = wx.StaticText(
			self,
			# Translators: Help message for a dialog.
			label=_("Select the initial sound system settings that will be set when NVDA starts:"),
			style=wx.ALIGN_LEFT
		)
		helpLabel.Wrap(helpLabel.GetSize()[0])
		sizer.Add(helpLabel, flag=wx.EXPAND)

		soundSizer = wx.BoxSizer(wx.VERTICAL)
		self._customVolumeSlider = guiHelper.LabeledControlHelper(
			self,
			# Translators: A setting in addon settings dialog.
			_("Set &custom volume level:"),
			nvdaControls.EnhancedInputSlider,
			value=config.conf[addonName]['volume'], minValue=0, maxValue=100, size=(250, -1)
		).control
		soundSizer.Add(self._customVolumeSlider)

		self._minVolumeSlider = guiHelper.LabeledControlHelper(
			self,
			# Translators: A setting in addon settings dialog.
			_("Increase the volume if it is &lower than:"),
			nvdaControls.EnhancedInputSlider,
			value=config.conf[addonName]['minlevel'], minValue=0, maxValue=100, size=(250, -1)
		).control
		soundSizer.Add(self._minVolumeSlider)
		sizer.Add(soundSizer, flag=wx.EXPAND)

		driverSizer = wx.BoxSizer(wx.VERTICAL)
		# Translators: A setting in addon settings dialog.
		self._driverChk = wx.CheckBox(self, label=_("&Repeat attempts to initialize the voice synthesizer driver"))
		driverSizer.Add(self._driverChk)
		self._driverChk.SetValue(config.conf[addonName]['reinit'])

		self._retriesCountSpin = guiHelper.LabeledControlHelper(
			self,
			# Translators: A setting in addon settings dialog.
			_("&Number of retries (0 - infinitely):"),
			nvdaControls.SelectOnFocusSpinCtrl,
			value=str(config.conf[addonName]['retries']), min=0, max=10000000
		).control
		driverSizer.Add(self._retriesCountSpin)
		self._retriesCountSpin.Show(self._driverChk.GetValue())
		self._driverChk.Bind(wx.EVT_CHECKBOX, self.onDriverChk)
		sizer.Add(driverSizer, flag=wx.EXPAND)
		self.sizer.Fit(self)

		# Translators: A setting in addon settings dialog.
		self._switchDeviceChk = wx.CheckBox(self, label=_("Switch to the default audio output &device"))
		sizer.Add(self._switchDeviceChk, flag=wx.EXPAND)
		self._switchDeviceChk.SetValue(config.conf[addonName]['switchdevice'])
		sizer.Fit(self)

		# Translators: A setting in addon settings dialog.
		self._playSoundChk = wx.CheckBox(self, label=_("Play &sound when audio has been successfully turned on"))
		sizer.Add(self._playSoundChk, flag=wx.EXPAND)
		self._playSoundChk.SetValue(config.conf[addonName]['playsound'])
		sizer.Fit(self)

	def onDriverChk(self, event: wx.PyEvent) -> None:
		"""Performed when a "self._driverChk" check box is selected or removed.
		@param event: event binder object which processes changing of the wx.Checkbox
		@type event: wx.PyEvent
		"""
		self._retriesCountSpin.Show(self._driverChk.GetValue())
		self._retriesCountSpin.GetParent().Layout()
		self.sizer.Fit(self)

	def postInit(self) -> None:
		"""Set system focus to source language selection dropdown list."""
		self._customVolumeSlider.SetFocus()

	def onSave(self) -> None:
		"""Update Configuration when clicking OK."""
		config.conf[addonName]['volume'] = self._customVolumeSlider.GetValue()
		config.conf[addonName]['minlevel'] = self._minVolumeSlider.GetValue()
		config.conf[addonName]['reinit'] = self._driverChk.GetValue()
		config.conf[addonName]['retries'] = self._retriesCountSpin.GetValue()
		config.conf[addonName]['switchdevice'] = self._switchDeviceChk.GetValue()
		config.conf[addonName]['playsound'] = self._playSoundChk.GetValue()
