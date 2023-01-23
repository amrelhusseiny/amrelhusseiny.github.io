---
title: Python's Netmiko starter template
date: 2022-07-17T12:36:51+02:00
draft: false
---
{{< toc >}}
The following is a ready to go netlike template , you just need to choose your way of authentication and the device type , you can find the supported devices on both the documentation and the Git for the Netmiko library :

**Netmiko Source Code :** [Netmiko Github](https://github.com/ktbyers/netmiko)
**API reference** _(must check for more functionality)_ : [Netmiko Doc](https://ktbyers.github.io/netmiko/docs/netmiko/index.html)

```
# netmiko_starter.py 
from netmiko import ConnectHandler

device_dictionary = {
                    'device_type': 'DEVICE_TYPE',  
                    'host': 'DEVICE_IP_ADDRESS',
                    'username': 'USERNAME',
                    'password' : 'PASSWORD',
                    # 'verbose': False ,
                    # 'session_log': 'log.txt', 
                    # 'global_delay_factor': 2, 
                }
net_connect = ConnectHandler(**device_dictionary)
output = net_connect.send_command("show version")
net_connect.disconnect()
```

## Comments on the code : 
  * uncomment _verbose_ if you want to disable Netmiko's Logs .
  * uncomment _session_log_ to debug the connection failures .
  * uncomment _ global_delay_factor_ to add delay when waiting for commands output , very useful if the devices are slow , note that this is not in seconds but in multiple , so "2" mean multiply the default delay by 2 and so on 

For more functionality , like the types of devices supported ,  please check the API docs .

Also check the textfsm templates part of the guide , this helps a lot with parsing the output instead of using the normal Regex way , it supports a lot of well known devices outputs .

good luck 
