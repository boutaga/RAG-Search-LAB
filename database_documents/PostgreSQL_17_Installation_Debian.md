# PostgreSQL 17 Installation Procedure on Debian

This document provides a step-by-step guide for installing PostgreSQL 17 on a Debian-based system.

## Prerequisites
- Debian 11 (Bullseye) or later installed.
- Root or sudo user privileges.
- Internet connectivity to download packages.

## Step 1: Update System Packages
```bash
sudo apt update
sudo apt upgrade -y
```

## Step 2: Add PostgreSQL Official Repository
```bash
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
```

## Step 3: Install PostgreSQL 17
```bash
sudo apt install -y postgresql-17
```

## Step 4: Verify Installation
```bash
psql --version
```
Expected output: `psql (PostgreSQL) 17.x`

## Step 5: Start and Enable PostgreSQL Service
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## Step 6: Configure PostgreSQL
- Switch to the postgres user:
```bash
sudo -i -u postgres
```
- Access the PostgreSQL prompt:
```bash
psql
```
- Set a password for the postgres user:
```sql
\password postgres
```
- Exit psql:
```sql
\q
```
- Exit postgres user shell:
```bash
exit
```

## Step 7: Adjust Firewall (if applicable)
```bash
sudo ufw allow 5432/tcp
sudo ufw reload
```

## Step 8: Configure Remote Access (Optional)
- Edit `postgresql.conf` to listen on all interfaces:
```bash
sudo nano /etc/postgresql/17/main/postgresql.conf
```
Change:
```
listen_addresses = 'localhost'
```
to
```
listen_addresses = '*'
```
- Edit `pg_hba.conf` to allow remote connections:
```bash
sudo nano /etc/postgresql/17/main/pg_hba.conf
```
Add:
```
host    all             all             0.0.0.0/0               md5
```
- Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## Step 9: Verify Remote Connection
From a remote machine:
```bash
psql -h <server_ip> -U postgres -d postgres
```

## Additional Notes
- Secure your PostgreSQL installation by restricting access and using strong passwords.
- Regularly update PostgreSQL packages using apt.
