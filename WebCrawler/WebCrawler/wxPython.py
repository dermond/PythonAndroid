
# First things, first. Import the wxPython package.

import wx
import wx.xrc
import shlex
import shutil
import os
import sys
import traceback
import time
import datetime
import uuid
import requests
from io import StringIO
import pandas as pd
import numpy as np
import pyodbc
from selenium import webdriver
import Public.PublicFun as PublicFun
from selenium.webdriver.common.action_chains import ActionChains
from goto import with_goto


class MyFrame2 ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		gSizer2 = wx.GridSizer( 0, 2, 0, 0 )

		self.m_button1 = wx.Button( self, wx.ID_ANY, u"開始", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer2.Add( self.m_button1, 0, wx.ALL, 5 )


		self.SetSizer( gSizer2 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.m_button1.Bind( wx.EVT_BUTTON, self.test )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def test( self, event ):
		print('sergergergerg')
		event.Skip()

def main():        
    app = wx.App(False) 
    frame = MyFrame2(None) 
    frame.Show(True) 
    #start the applications 
    app.MainLoop() 

if __name__ == '__main__':
    main()