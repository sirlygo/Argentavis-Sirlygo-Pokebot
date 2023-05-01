
# Mew Pokébot Wip

This is a discord bot that allows random pokemon to spawn in a server. as users chat, they accrue battle points that they can spend to buy items.


## Changelog


#### 0.1.0


* Original release.

#### 0.1.1


* Hardcoded a home channel

* Doubled pokemon spawn rate

* Catching a pokemon autosaves your profile

* You can see your pokeballs count on your profile

* updated admin help



# Install Instructions

1. unzip the zip file into an empty directory. the folder can be named anything, but i suggest the same name as the zip.

2. visit the Discord Developer Portal.
	https://discord.com/developers/applications

3. in the top right, click new application, and name it something. this name is not important or visible.

4. on the left, click 🧩 Bot. on the right, click add bot.

5. THIS name and icon are visible. this is your bot's discord account. Customize it to your heart's content.

6. where it says "copy" and "view token", click copy. You have your bot's password.

7. paste this code into bot_key.txt and save it. the main file is programmed to open that text file and read it. to log in.

8. scroll down to the switches, and flick the one labelled MESSAGE CONTENT INTENT. click save.

9. on the left, click 🔧 Oauth2. underneath, click ↪ URL generator.

10. in the scopes menu, please just check bot.

11. scroll down, and you will see a bot permissions menu.
	-send messages, manage messages, embed links, attatch files, read message history, mention everyone, use extrnal emojis, add reactions...
	-manage roles, manage channels, manage nicknames, manage emojis, read messages/view channels

12. copy the link underneath the menus. visit that link, or ask server admins to visit that link. visiting the link allows you to invite the bot's account to a server.

13. make sure you have the latest version of python installed on your computer
	https://www.python.org/downloads/
	
14. Right click on main.py open with notepad(just once) Scroll down till you see admin_uids = this is gives admin to a user add the id of you user you want to add as 
admin here (example:admin_uids = 6301002102) home_channel = this is your spawn channel add your channel id here (example:home_channel = 6301002102)

15. double click on main.py to run.
