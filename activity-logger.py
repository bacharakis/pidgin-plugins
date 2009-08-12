""" This script is meant to log the number of logged on users at any given point of time. So this is what I will do.
	Whenever a person logs on or logs off Pidgin emits signals notifying that something has happened. I would take the
	initial person count and then add/del the users according to the emmited signal!"""

# Dbus connectivity for pidgin
	
import dbus, gobject
from dbus.mainloop.glib import DBusGMainLoop

# Set the basic variables
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
obj = bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
purple = dbus.Interface(obj, "im.pidgin.purple.PurpleInterface")
bus = dbus.SessionBus()

# Import Datetime for timestamping purposes
import datetime


class PidginActivityLogger:

	def __init__(self):
	
		# Initialize the counter to zero
		self.users_online = 0
		
		# Add the initially active users
		self.users_online = self.getTotalOnlineCount()
		
		# Open a stream to write to
		self.DB = file('activity.log','a')
		
		# Print information to DB
		self.writeInfoToDB()	
		
		

	def writeInfoToDB(self):
		# Obtain the time right now!
		time = datetime.datetime.now()

		# Prepare a string to be printed into the DB
		entry = str(time) +" "+str(self.users_online)+"\n"
		
		# Write the string to the DB
		self.DB.writelines(entry)
		
		# Flush the entry from the buffer to disk
		self.DB.flush()
		
		print entry
	
	def getTotalOnlineCount(self):
	
		# Initialize count to zero
		count = 0
		
		# Get all the active accounts
		accounts = purple.PurpleAccountsGetAllActive()
		
		# Print the info
		for account in accounts:
			print purple.PurpleAccountGetUsername(account)
		
		buddies = purple.PurpleFindBuddies(accounts[0], "")
		
		for buddy in buddies:
			
			presence = purple.PurpleBuddyGetPresence(buddy)
			print purple.PurpleBuddyGetAlias(buddy), purple.PurplePresenceIsOnline(presence)
			is_online = purple.PurplePresenceIsOnline(presence)
			if is_online == 1:
				count = count +1
			
		return count
		
	def registerSignals(self):
		print "inside register signals... "
		
		bus.add_signal_receiver(self.incrBuddyCount,
                        dbus_interface="im.pidgin.purple.PurpleInterface",
                        signal_name="BuddySignedOn")
                        
		bus.add_signal_receiver(self.decrBuddyCount,
                        dbus_interface="im.pidgin.purple.PurpleInterface",
                        signal_name="BuddySignedOff")
		
	def incrBuddyCount(self, buddy):
	
		self.users_online = self.users_online + 1
		
		# Print information to DB
		self.writeInfoToDB()
		
	def decrBuddyCount(self, buddy):
		
		self.users_online = self.users_online - 1
		
		# Print information to DB
		self.writeInfoToDB()
		
		
if __name__ == '__main__':

	pal = PidginActivityLogger()
	pal.registerSignals()
	loop = gobject.MainLoop()
	loop.run()
	
 
		
