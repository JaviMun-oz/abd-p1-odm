"""Populate EnVivo using the existing ODM. Run from the project directory."""
from datetime import datetime, timedelta
from random import Random
from pymongo import MongoClient
import ODM

rng = Random(2026)
ODM.initApp()
Recinto, Artista, Evento, Asistente = (getattr(ODM, n) for n in ('Recinto','Artista','Evento','Asistente'))
db = MongoClient('mongodb://localhost:27017/')['abd']

venues = [
 ('Movistar Arena Madrid','Av. de Felipe II, s/n, 28009 Madrid, Spain',17000),
 ('Palau Sant Jordi','Passeig Olimpic, 5-7, 08038 Barcelona, Spain',17000),
 ('WiZink Hall Fictional','Calle de Alcala, 100, Madrid, Spain',1200),
 ('Sala Apolo','Carrer Nou de la Rambla, 113, Barcelona, Spain',1300),
 ('La Riviera','Paseo Bajo de la Virgen del Puerto, 3, Madrid, Spain',1800),
 ('Bilbao Arena','Askatasuna Etorbidea, 13, Bilbao, Spain',10000),
 ('Auditorio de Zaragoza','Calle Eduardo Ibarra, 3, Zaragoza, Spain',2000),
 ('Sala Razzmatazz','Carrer dels Almogavers, 122, Barcelona, Spain',2000),
 ('Baluarte','Plaza del Baluarte, Pamplona, Spain',1500),
 ('Cartuja Center','Calle Leonardo da Vinci, 7, Sevilla, Spain',2000),
]
artists = [
 ('Rosalia',['pop','flamenco'],'Espana',2013), ('Vetusta Morla',['indie','rock'],'Espana',1998),
 ('Aitana',['pop'],'Espana',2017), ('Love of Lesbian',['indie','rock'],'Espana',1997),
 ('Amaral',['pop','rock'],'Espana',1992), ('C Tangana',['urbano','rap'],'Espana',2005),
 ('Leiva',['rock','pop'],'Espana',2011), ('Izal',['indie'],'Espana',2010),
 ('Dorian',['electronica','indie'],'Espana',2004), ('Zahara',['indie','pop'],'Espana',2005),
 ('Arde Bogota',['rock'],'Espana',2017), ('La La Love You',['pop','punk'],'Espana',2007),
 ('Lori Meyers',['indie','rock'],'Espana',1998), ('Nathy Peluso',['urbano','pop'],'Argentina',2017),
 ('Carolina Durante',['rock','punk'],'Espana',2017)
]

# Re-runnable: skip existing records, avoiding duplicate-key errors.
venue_ids=[]
for name,address,capacity in venues:
    existing=db.Recinto.find_one({'nombre':name})
    if existing:
        venue_ids.append(existing['_id']); continue
    zones={'pista':int(capacity*.6),'grada':capacity-int(capacity*.6)}
    obj=Recinto(nombre=name,direccion=address,aforo=capacity,zonas=zones,servicios=['aseos','accesibilidad','bar'])
    obj.save(); venue_ids.append(obj._data['_id']); print('Saved venue:',name,flush=True)

artist_ids=[]
for name,genres,country,year in artists:
    existing=db.Artista.find_one({'nombre':name})
    if existing:
        artist_ids.append(existing['_id']); continue
    obj=Artista(nombre=name,generos=genres,pais_origen=country,anio_inicio=year)
    obj.save(); artist_ids.append(obj._data['_id'])

for i in range(20):
    title=f'EnVivo Festival Session {i+1:02d}'
    if db.Evento.find_one({'titulo':title}): continue
    venue=i%len(venues)
    capacity=venues[venue][2]
    obj=Evento(titulo=title,artistas_ids=[artist_ids[i%15],artist_ids[(i+4)%15]],
        recinto_id=venue_ids[venue],fecha=datetime(2024+(i//7), 1+(i%12), 10+(i%15),20,0),
        precios_zona={'pista':35+(i%6)*5,'grada':25+(i%5)*5},
        entradas_vendidas=rng.randint(100,min(capacity,3000)))
    obj.save()

for i in range(20):
    email=f'asistente{i+1:02d}@example.com'
    if db.Asistente.find_one({'email':email}): continue
    obj=Asistente(nombre=f'Asistente Ejemplo {i+1:02d}',email=email,
        fecha_registro=datetime(2024,1,1)+timedelta(days=i*30),
        generos_preferidos=[artists[i%15][1][0]])
    obj.save()

for name in ('Recinto','Artista','Evento','Asistente'):
    print(name,db[name].count_documents({}))
print('Finished. Export the four collections to JSON.')
