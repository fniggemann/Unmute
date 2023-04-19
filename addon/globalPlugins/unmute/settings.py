# settings.py
# A part of the NVDA Unmute add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020-2023 Olexandr Gryshchenko <grisov.nvaccess@mailnull.com>

import addonHandler
import gui
from gui import guiHelper, nvdaControls
import wx
import config
from typing import Any, Callable, Dict
from logHandler import log
from . import ADDON_NAME, ADDON_SUMMARY

try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	log.warning("Unable to init translations. This may be because the addon is running from NVDA scratchpad.")
_: Callable[[str], str]


class UnmuteSettingsPanel(gui.SettingsPanel):
	"""Add-on settings panel object"""
	title: str = ADDON_SUMMARY

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
		addonHelper = guiHelper.BoxSizerHelper(self, sizer=sizer)
		addonHelper.addItem(
			wx.StaticText(
				self,
				# Translators: Help message for a dialog.
				label=_("Select the initial sound system settings that will be set when NVDA starts:"),
				style=wx.ALIGN_LEFT
			)
		)
		self._customVolumeSlider = addonHelper.addLabeledControl(
			# Translators: A setting in addon settings dialog.
			_("Set &custom volume level:"),
			nvdaControls.EnhancedInputSlider,
			value=config.conf[ADDON_NAME]['volume'], minValue=0, maxValue=100, size=(250, -1)
		)
		self._minVolumeSlider = addonHelper.addLabeledControl(
			# Translators: A setting in addon settings dialog.
			_("Increase the volume if it is &lower than:"),
			nvdaControls.EnhancedInputSlider,
			value=config.conf[ADDON_NAME]['minlevel'], minValue=0, maxValue=100, size=(250, -1)
		)
		self._driverChk = addonHelper.addItem(
			# Translators: A setting in addon settings dialog.
			wx.CheckBox(self, label=_("&Repeat attempts to initialize the voice synthesizer driver"))
		)
		self._driverChk.SetValue(config.conf[ADDON_NAME]['reinit'])
		self._retriesCountSpin = addonHelper.addLabeledControl(
			# Translators: A setting in addon settings dialog.
			_("&Number of retries (0 - infinitely):"),
			nvdaControls.SelectOnFocusSpinCtrl,
			value=str(config.conf[ADDON_NAME]['retries']), min=0, max=10000000
		)
		self._retriesCountSpin.Show(self._driverChk.GetValue())
		self._driverChk.Bind(wx.EVT_CHECKBOX, self.onDriverChk)
		self._switchDeviceChk = addonHelper.addItem(
			# Translators: A setting in addon settings dialog.
			wx.CheckBox(self, label=_("Switch to the default audio output &device"))
		)
		self._switchDeviceChk.SetValue(config.conf[ADDON_NAME]['switchdevice'])
		self._playSoundChk = addonHelper.addItem(
			# Translators: A setting in addon settings dialog.
			wx.CheckBox(self, label=_("Play &sound when audio has been successfully turned on"))
		)
		self._playSoundChk.SetValue(config.conf[ADDON_NAME]['playsound'])
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
		"""Update Configuration when clicking OK.
		Add-on parameters are always stored in the basic configuration profile.
		"""
		parameters: Dict[str, Any] = {
			'volume': self._customVolumeSlider.GetValue(),
			'minlevel': self._minVolumeSlider.GetValue(),
			'reinit': self._driverChk.GetValue(),
			'retries': self._retriesCountSpin.GetValue(),
			'switchdevice': self._switchDeviceChk.GetValue(),
			'playsound': self._playSoundChk.GetValue(),
		}
		try:
			config.conf.profiles[0][ADDON_NAME].update(parameters)
		except (KeyError, AttributeError,):
			config.conf.profiles[0][ADDON_NAME] = parameters
