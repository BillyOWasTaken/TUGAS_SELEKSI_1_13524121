<h1 align="center">
  <br>
  Seleksi Warga Basdat 2026 <br>
  ETL Project
  <br>
  <br>
</h1>

## Deskripsi Singkat 
Dalam repositori ini terdapat data persona - persona Roger dari American Dad yang di*scrape* dari [personaassistant.dad](https://personaassistant.dad/)* dan disimpan dalam database MariaDB. 
#### Why American Dad? Why Roger? 
~~Ide yang lain sudah keambil and this was the only scrapable data i could think of~~  
I wanted to be niche. Also, because [Seth MacFarlane  is awesome](https://www.youtube.com/watch?v=nwlLUmnLM_0).

<sub>*alternative data source: https://americandad.fandom.com/wiki/Roger%27s_Disguises namun Fandom melarang scraping</sub>

## Data Scraping

```
cd "Data Scraping"/src
pip install -r requirements.txt
python scrape.py
```
Setelah proses scraping selesai,
```
python cleanup.py
```
``personas.json`` dan ``episodes.json`` akan tersimpan dalam folder ``Data Scraping/data/`` dengan struktur berikut:
``` 
"name":               <-- nama persona
"first_appeared":     <-- id episode untuk episode debut persona
"appeared_in_intro":  <-- id episode di mana persona muncul dalam intro
"quotes": []          <-- memorable quotes dari persona
"notes":              <-- catatan tertentu untuk persona
"occupation":         <-- pekerjaan persona
```
```
"id":                 <-- id episode 
"title":              <-- judul episode
"season":             <-- musim tayang episode
"episode":            <-- nomor urut episode
"air_date":           <-- tanggal tayang episode
"runtime":            <-- durasi episode
"summary":            <-- ringkasan episode
"tvdb_url":           <-- url tvdb dengan id episode
```
## Data Modelling

#### ERD
![ERD](Data%20Storing/design/ERD.png)

#### Relational 
![Relational](Data%20Storing/design/Relational.png)

Tabel Appearance merupakan hasil translasi relasi many to many antara Persona dan Episode  
Tabel Quotes merupakan hasil translasi multivalue attribute entity Persona  

Some notes: 
* Penggunaan surrogate key pada Quotes merupakan hasil akhir [pertimbangan](https://stackoverflow.com/questions/25300821/difference-between-varchar-and-text-in-mysql) [panjang](https://rusanu.com/2010/03/22/performance-comparison-of-varcharmax-vs-varcharn/)
* Penggunaan surrogate key pada tabel Persona dan Appearance berdasarkan [artikel](https://towardsdev.com/sql-trade-off-natural-keys-vs-surrogate-keys-9e0cb1c73c51) [berikut](https://liambx.com/blog/why-surrogate-keys-win) (dan juga sedikit bias dari keputusan sebelumnya)
* Attribute notes dan is_intro ditambahkan untuk menjaga keutuhan data tambahan dari hasil scraping

## Data Storing

```
cd "Data Storing"/src
pip install -r requirements.txt
python storing.py
```

## AI Usage
#### Bagian-bagian yang dibantu AI:
Perbaikan `scrape.py` untuk scrape quotes dan notes

#### Bagian-bagian yang tetap dikerjakan sendiri:
Everything else
#### Refleksi dari penggunaan AI
<img src="https://media1.tenor.com/m/leFCTAEGtuEAAAAd/speed-speed-nodding.gif" width="200" alt="speed nod">

## Screenshots

![persona](Data%20Storing/screenshot/persona.png)

![quotes](Data%20Storing/screenshot/quotes.png)

![appearance](Data%20Storing/screenshot/appearance.png)

## References
Libraries: Playwright, MariaDB Connector/Python


## Author

 <div align="center" id="contributor">
   <strong>
     <table align="center">
       <tr align="center">
         <td>NIM</td>
         <td>Nama</td>
         <td>GitHub</td>
       </tr>
       <tr align="center">
         <td>13524121</td>
         <td>Billy Ontoseno Irawan</td>
         <td><a href="https://github.com/BillyOWasTaken">@BillyOWasTaken</a></td>
       </tr>
     </table>
   </strong>
 </div>