# GVM Script
GVM Script is an automation wrapper tool used to automate GVM commands and provide callbacks to finished GVM scans. Also includes formatter from csv to syslog, Wazuh decoder, and Wazuh rules, to enable GVM integration into Wazuh.

### Requirements
This script requires a GNU/Linux environment to execute. Additionally, it also requires:
1. Python 3.10.12
2. Flask (Ver. 3.0.3)
3. Gvm-tools (Ver. 24.7.0)
4. Python-gvm (Ver. 4.8)
5. Gunicorn (Ver. 23.0.0)

### Installation
This script requires no installation. Allow execution of script using
```
./chmod +x gvm_commands.py
```

### Usage
This script is cli based, show list of commands using
```
./gvm_commands.py -h
```

Alternatively, gvm_commands can also be used like
```
./gvm_commands.py <file name at ./libraries/scripts> <args>
```

### Notable Features
- Simple flask webhook to respond to finished scans
- Constant configuration file to reduce arguments in script calls
- Report formatter to format report files into Syslog
- Wazuh decoder for decoding formatted GVM report
- Wazuh rule to create an alert from formatted GVM report

## Credits
> [MuhamadAjiW](https://github.com/MuhamadAjiW) <br/>
> [akmaldika](https://github.com/akmaldika) <br/>
> [martinboller](https://github.com/martinboller). Libraries taken and extended from this [repository](https://github.com/martinboller/greenbone-gmp-scripts)