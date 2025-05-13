# Oracle 19c Installation Procedure on RHEL

This document provides a step-by-step guide for installing Oracle Database 19c on a Red Hat Enterprise Linux (RHEL) system.

## Prerequisites
- RHEL 7 or 8 installed and updated.
- Root or sudo user privileges.
- Sufficient disk space and memory (minimum 2GB RAM recommended).
- Oracle 19c installation media or access to Oracle Software Delivery Cloud.

## Step 1: Prepare the System

### Update System Packages
```bash
sudo yum update -y
```

### Install Required Packages
```bash
sudo yum install -y oracle-database-preinstall-19c
```
This package installs required dependencies and creates oracle user and groups.

### Verify Kernel Parameters and Limits
The preinstall package sets most parameters, but verify `/etc/sysctl.conf` and `/etc/security/limits.conf` for:
- `fs.file-max`
- `kernel.sem`
- `kernel.shmmax`
- `kernel.shmall`
- User limits for oracle user (`nofile`, `nproc`)

## Step 2: Create Oracle Directories
```bash
sudo mkdir -p /u01/app/oracle
sudo chown -R oracle:oinstall /u01
sudo chmod -R 775 /u01
```

## Step 3: Configure Oracle User Environment
Switch to oracle user:
```bash
sudo su - oracle
```
Set environment variables in `.bash_profile`:
```bash
export ORACLE_BASE=/u01/app/oracle
export ORACLE_HOME=$ORACLE_BASE/product/19.0.0/dbhome_1
export ORACLE_SID=ORCLCDB
export PATH=$PATH:$ORACLE_HOME/bin
```
Source the profile:
```bash
source ~/.bash_profile
```

## Step 4: Extract Oracle Installation Files
Upload and extract Oracle 19c installation zip files to a staging directory, e.g. `/home/oracle/install`.
```bash
unzip linux.x64_19c_database.zip -d /home/oracle/install
```

## Step 5: Run Oracle Universal Installer (OUI)
Navigate to the database directory:
```bash
cd /home/oracle/install/database
```
Start the installer:
```bash
./runInstaller
```
- Follow GUI prompts:
  - Select "Create and configure a single instance database".
  - Choose installation location (`$ORACLE_HOME`).
  - Configure database name and administrative passwords.
  - Select memory and storage options.
- At the end, run root scripts as prompted:
```bash
sudo /u01/app/oraInventory/orainstRoot.sh
sudo /u01/app/oracle/product/19.0.0/dbhome_1/root.sh
```

## Step 6: Post-Installation Configuration

### Configure Listener
Edit `listener.ora` and `tnsnames.ora` in `$ORACLE_HOME/network/admin` as needed.

### Start Listener
```bash
lsnrctl start
```

### Verify Database Status
```bash
sqlplus / as sysdba
SQL> select status from v$instance;
```

## Step 7: Enable Automatic Startup
Create systemd service or use Oracle provided scripts to start database and listener on boot.

## Step 8: Firewall Configuration
Allow Oracle ports (default 1521):
```bash
sudo firewall-cmd --add-port=1521/tcp --permanent
sudo firewall-cmd --reload
```

## Additional Notes
- Regularly patch Oracle using OPatch utility.
- Backup database before major changes.
- Monitor alert logs and performance metrics.
