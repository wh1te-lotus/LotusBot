LotusBot is a Discord server moderation bot with the capability to warn, mute, kick, and ban members.   
You can add the bot by clicking on https://discord.com/api/oauth2/authorize?client_id=975511452045680650&permissions=1099780139014&scope=bot and following the steps on screen.  
  
List of commands and the proper syntax:  
!help   
Sends a list of all commands, what they do, and the permissions necessary to run them. Effectively the same as this section.  

!ping  
Returns the bot latency from the server, in milliseconds.  

!warn <member> <reason>  
Adds an official warning to the !case logs and DMs the user.  
Requires the MANAGE_ROLES permission.  

!mutedrole <@role>  
Sets the role used for the !mute command.  
Requires the MANAGE_ROLES permission.  

!mute <member> <duration> <reason>   
Temporarily adds the role defined by !mutedrole.  
Automatically removes it after the given period of time. Requires the MANAGE_ROLES permission.  

!kick <member> <reason>  
Kicks a member from the server; however, they can still rejoin.  
Requires the KICK_MEMBERS permission.  

!ban <member> <reason>  
Permanently bans a member from the server.  
Requires the BAN_MEMBERS permission.  
