# Production Deployment

## Setup cron jobs:

After the application is running, you have to set up cron jobs to send out emails. Do the following:

- Open the terminal and run `crontab -e` to open the cron jobs file.
- Add the following line to the file: `0 18 * * * curl -X POST https://reflect.iik.ntnu.no/api/send-notifications`
  - If using a different port or url, change the url accordingly.
- Save and exit: If your in vim, press `esc` and then `:wq` and then `enter`.
- Verify Crontab: Run `crontab -l` to verify that the cron job is added.
- Then restart the cron service by running `sudo service cron restart`.
- Note: If you are unsure it work, check the system date by running `date` and see if the cron job is executed at the correct time.

Note: this cron job will send out emails every day at 18:00 and works only for linux. If you are using windows, you can use the windows task scheduler to do the same thing, but it is not covered in this documentation as it is not used in production.

## Running containers:

In production we have dockerized all the applications and use Postgres as the database. Docker compose is used to setup all the containers together and [traefik](https://doc.traefik.io/) is used as a reverse proxy to the containers and handle ssl.

**Requirements:**

- Docker
- Docker compose

## Environment:

In the `backend` folder, create`.env` containing the following:

- `production = true`
- `SECRET_KEY` is set
- `client_id` is set
- `client_secret` is set
- `OPENAI_KEY` is set

Mailing environment variables: (used for sending emails, this can you get from Ntnu IT or use a different mailing service)
- `MAIL_USERNAME` is set
- `MAIL_PASSWORD` is set
- `MAIL_SERVER` is set
- `MAIL_PORT` is set
- `MAIL_FROM` is set

**the client secrets corresponds to your feide instance**

- the following postgres variables is set: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`.
- REDIRECT_URI = "https://reflect.iik.ntnu.no/auth"
- BASE_URL = "https://reflect.iik.ntnu.no"

In `frontend` folder:

- create `.env.production` with PUBLIC_API_URL="https://reflect.iik.ntnu.no/api"

_See .env.template for what to include in the .env file!_

Also make sure that there exists a `certs` folder with the ssl privatekey and certificate (More on this below).

## Running containers:

```bash
docker-compose build
docker-compose up -d
```

**OBS:**

If you have a firewall on the production server, make sure port 443 is open.

Frontend is running on URL/
Backend api is running on URL/api/
Backend docs is running on URL/api/docs
Backend auth is running on URL/auth

## Setting up certificates

This section is for how to set up a certificate for a production server. Only use this if theres a need for hosting the application on a new server.
In order for the server to use HTTPS, a TLS certificate is needed.
Instructions:

1. Set up a certificate on [cert manager](https://cert-manager.com/customer/Uninett/idp/ssl/vUMoaUELCX71mTS4x7NC/select).
2. Choose "Feide", not "FEIDE" when logging in. Here you can enroll a new certificate. Click the "enroll certificate" button. On this page you can upload a CSR (Certificate Signing Request) file.
3. Create a new CSR file using this [tutorial](https://www.ssl.com/how-to/manually-generate-a-certificate-signing-request-csr-using-openssl/). You need [openSSL](https://www.openssl.org/source/) in order to do this.
4. When creating the CSR file, you will be asked to fill in some information. Some of these you dont need to fill in. You should rather not fill in organization details in CSR. The important ones is:

   1. `country(CO)`. Set this to `"NO"`.
   2. `CN (Common Name)`. Set this to the domain name of the server. In our case `"reflect.iik.ntnu.no"`
   3. The rest is filled out automatically using the information stored on NTNU on sectigo. In case the fields are obligatory, it is important that you fill in; `organization(O)`, `organization unit(OU)`, `city(L)`, `state or province(ST)`.
      `O` and `OU` is `"Norges Teknisk-Naturvitenskapelige Universitet NTNU"`, `L` is `"Trondheim"`, `ST` is `"Trøndelag"`.
   4. For those who need it, prefix www. is added to the GÉANT OV SSL-certificate type.

5. Remember to save the CSR file someplace you'll find it. Then upload this on cert-manager.
6. Certificates are controlled consecutively by the administrators. You will recieve a mail when the certificate is approved and ready.
7. When the certificate is approved, you can download the certificate and the private key.
8. The certificate is a `.pem` file, and the private key is a `.key` file. These files should be placed in a `certs` folder in the root of the project. The `.key` file was generated when creating the CSR file.
9. The certificate is now ready to be used by traefik. Change the `traefik.yaml` file to use the new certificate.
   This is done by changing the following lines in the `traefik.toml`file:
   ```bash
   tls:
   certificates:
       - certFile: /certs/ref_iik_ntnu_no.pem
       keyFile: /certs/refPRIVATEKEY_nopass.key
   ```
10. Note, make sure that the private key file is not password protected. If it is, you have to remove the password from the key file. This can be done by running the following command:
    ```bash
    openssl rsa -in refPRIVATEKEY_nopass.key -out refPRIVATEKEY_nopass.key
    ```
    This will remove the password from the key file.
11. The application should now be able to run on the new server.
12. Note: If you are using a different domain, you have to change the domain name in the `docker-compose.yml` file. And in the url in `format_email()` function in the `backend/api/main.py` file.

## Useful docker commands

**List all containers**

```bash
docker ps
```

**Get logs of a container**

After running `docker ps` to get the container id, run:

```bash
docker logs `<CONTAINER ID>`
```

You dont need to fill in the entire ID, just enough to make it unique.

**Take down all containers**

```bash
docker-compose down
```

**Delete all images and volumes**

```bash
docker system prune -a
```
