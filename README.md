# 🍺 KaliaBot

Telegram botti, joka on tehty pääasiassa Kaliakunta telegram ryhmään, mutta botin voi lisätä myös muihin ryhmiin tai käyttää yksityisviesteissä.
Botin löytää telegrammista @kaliaa_bot

## Komennot

### 🍻 Kalia

Käyttäjät voi käyttää */kalia* komentoa kuvan otsikossa. Tämä lisää käyttäjälle yhden juodun kalian.

### 🍻 Pyha

Käyttäjät voi käyttää */pyha* komentoa kuvan otsikossa. Tämä lisää käyttäjälle yhden juodun Guinnessin.

### 🍻 Hoplop

Käyttäjät voi käyttää */hoplop* komentoa kuvan otsikossa. Tämä lisää käyttäjälle yhden juodun holitomman kalian, rimmeriä.

### 🍻 Kaliacount

Käyttäjä voi käyttää */kaliacount* komentoa. Botti kertoo montako kaliaa käyttäjä on juonut.

### 🍻 Groupcount

Käyttäjä voi käyttää */groupcount* komentoa. Botti kertoo monta kaliaa ryhmässä on juotu yhteensä.

### 🍻 Kaliatop

Käyttäjä voi käyttää */kaliatop* tai */scoreboard* komentoa. Botti näyttää taulukon missä näkyy ryhmän top 10 kalian juojaa.

### 🍻 Pyhatop

Käyttäjä voi käyttää */pyhatop* tai */pyhascoreboard* komentoa. Botti näyttää taulukon missä näkyy ryhmän top 10 Guinnessin juojaa

### 🍻 Kuukausiraportti

Botti lähettää kuukauden 1. päivä raportin montako kaliaa kuukaudessa on juotu.


## Käyttäjäkuvat

### 🍺 /Kalia
<img width="558" height="706" alt="kalia kuva" src="https://github.com/user-attachments/assets/0843b997-b5ea-42d4-b199-3f207f17eaea" />

### 🍺 /Pyha
<img width="552" height="710" alt="pyha kuva" src="https://github.com/user-attachments/assets/e5925035-a4c8-4fb4-92d6-2329e29fc953" />

### 🍺 Botin reagointi kuviin
<img width="578" height="881" alt="reagointi kuva" src="https://github.com/user-attachments/assets/8ff3e3b8-f3d9-4180-8985-de500e86f123" />

### 🍺 /Kaliacount
<img width="417" height="86" alt="kaliacount kuva" src="https://github.com/user-attachments/assets/6a55fad1-120f-41cc-b825-92553bb356cb" />

### 🍺 /Groupcount
<img width="417" height="82" alt="groupcount kuva" src="https://github.com/user-attachments/assets/acb5ef70-4347-4c17-b009-da28ab26d407" />

### 🍺 /Kaliatop
<img width="417" height="461" alt="kaliatop kuva" src="https://github.com/user-attachments/assets/6f5bd54f-0c9d-4611-939d-dc49ea12082f" />

### 🍺 /Pyhatop
<img width="417" height="434" alt="pyhatop kuva" src="https://github.com/user-attachments/assets/dc4fa5e5-a531-4a1f-bf7b-d1222f706e87" />


## Tekniset tiedot

Botti on tehty @BotFather tokenin avulla ja se rullaa dockerilla Renderissä. Botti käyttää PostgreSQL-tietokantaa, ja `DATABASE_URL`-ympäristömuuttuja on pakollinen myös paikallisessa ajossa. Jokainen `/kalia`-komento tallentuu `kalia_events`-tauluun UTC-aikaleiman ja Telegram-viestin tunnisteen kanssa Power BI -raportointia varten.


## Muut tiedot

Botti on ihan täysin vapaa-aika projekti, päivityksiä tulee joskus ja joulun jos tulee. Parannusvinkkejä voi laitella tg privassa @oliverkauppi.
