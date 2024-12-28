# MonitorPythonScripts
 
## Install packages
```sh
apt install libfbclient2 pkg-config default-libmysqlclient-dev
python3 -m pip install mysqlclient fdb telepot
```

## Scripts

- ### **monitorAdaosOrdonataDepasit.py**

- ### **monitorDiferentaLDI.py**

- ### **monitorNewCIFinSPV.py**
```sql
CREATE USER 'efacturauser_remote_181'@'192.168.60.181' IDENTIFIED BY '1234';
GRANT SELECT on efactura.* TO 'efacturauser_remote_181'@'192.168.60.181';
FLUSH PRIVILEGES;
```

- ### **monitorNirAdaos.py**

- #### unused_monitorNirAvizeDublu.py

## Crontab
```sh
45 20 * * * python3 /root/MonitorPythonScripts/monitorNirAdaos.py
55 20 * * * python3 /root/MonitorPythonScripts/monitorDiferentaLDI.py
30 21 * * * python3 /root/MonitorPythonScripts/monitorAdaosOrdonataDepasit.py
0 22 * * * python3 /root/MonitorPythonScripts/monitorNewCIFinSPV.py

#05 21 * * * python3 /root/MonitorPythonScripts/unused_monitorNirAvizeDublu.py 3
```
