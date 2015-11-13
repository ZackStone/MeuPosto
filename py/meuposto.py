#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import json
import collections
import cgi, cgitb 

cgitb.enable()  # for troubleshooting

#####################################
# Servidor web sem framework
#####################################

# get input (POST)

data = cgi.FieldStorage()
jsonin = str(data.value)

# Comentar a linha abaixo se usar servidor webPy
print BuscarPostos(queryString)

#####################################
# Servidor web com framework python
#####################################

def application(environ, start_response):
    if environ.get('PATH_INFO') == '/MeuPosto/':
        status = '200 OK'
        f = open('/var/www/MeuPosto/index.html','r')
        content = f.read()
        f.close()
        contentType = 'text/html'

    elif '/MeuPosto/' in environ.get('PATH_INFO'):
        path = environ.get('PATH_INFO')
        ext = path[path.index('.')+1:]
        arquivo = path
        if '?' in path:
            arquivo = path[0:path.index('?')]
        status = '200 OK'
        f = open('/var/www' + arquivo ,'r')
        content = f.read()
        f.close()
        contentType = 'text/' + ext
        if 'js' in path:
            contentType = 'application/javascript'

    elif environ.get('PATH_INFO') == '/':
        status = '200 OK'
        queryString = environ.get('QUERY_STRING')
        content = BuscarPostos(queryString)
        contentType = 'application/json'

    else:
        status = '404 NOT FOUND'
        content = 'Page not found.'
        contentType = 'text/html'

    response_headers = [('Content-Type', contentType), ('Content-Length', str(len(content))), ('Access-Control-Allow-Origin','http://yitzhakstone.github.io'), ('Access-Control-Allow-Headers','Origin, X-Requested-With, Content-Type, Accept, Key')];
    start_response(status, response_headers)
    yield content

#####################################
# Métodos
#####################################

def BuscarPostos(jsonin):

  # separate params of input
  
  jsonin = jsonin.replace("(", "").replace(")", "").replace(" ", "");
  coords = jsonin.split(',');
  latMin = coords[0];
  lngMin = coords[1];
  latMax = coords[2];
  lngMax = coords[3];
  
  db = MySQLdb.connect(host="localhost", user="root", passwd="balde", db="MeuPosto")
  cur = db.cursor() 
  
  '''
  cur.execute(""" 
    SELECT 
      P.ID, P.Nome, P.Logr, P.Num, P.Bairro, P.Lat, P.Lng, A.Avaliacao 
    FROM 
      Posto P LEFT JOIN 
      PostoAvaliacao A ON P.ID = A.IDPosto 
    WHERE """
      "P.Lat BETWEEN " + latMin + " AND " + latMax + " AND "
      "P.Lng BETWEEN " + lngMin + " AND " + lngMax + " "
    ";")
  '''
  
  cur.execute("""
    SELECT
      P.ID, P.Nome, P.Logr, P.Num, P.Bairro, P.Lat, P.Lng, T.Avaliacao,
      (SELECT C.Valor FROM PostoCombustivel C WHERE C.IDPosto = P.ID AND C.IDComb = 1) AS Valor_Alcool,
      (SELECT C.Valor FROM PostoCombustivel C WHERE C.IDPosto = P.ID AND C.IDComb = 2) AS Valor_Gasolina,
      (SELECT C.Valor FROM PostoCombustivel C WHERE C.IDPosto = P.ID AND C.IDComb = 3) AS Valor_GNV,
      (SELECT C.Valor FROM PostoCombustivel C WHERE C.IDPosto = P.ID AND C.IDComb = 4) AS Valor_Diesel,
      (SELECT C.Valor FROM PostoCombustivel C WHERE C.IDPosto = P.ID AND C.IDComb = 5) AS Valor_GasolinaAdt,
      (SELECT C.Valor FROM PostoCombustivel C WHERE C.IDPosto = P.ID AND C.IDComb = 6) AS Valor_GasolinaPremium
    FROM
      Posto P LEFT JOIN
      (
    	SELECT A.IDPosto, AVG(A.Avaliacao) AS Avaliacao FROM PostoAvaliacao A GROUP BY A.IDPosto
      ) AS T ON T.IDPosto = P.ID
    WHERE """
      "P.Lat BETWEEN " + latMin + " AND " + latMax + " AND "
      "P.Lng BETWEEN " + lngMin + " AND " + lngMax + " "
    ";")
  
  rows = cur.fetchall()
  
  # Convert query to row arrays
  
  rowarray_list = []
  for row in rows:
      t = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
      rowarray_list.append(t)
  
  # Convert query to row arrays
  
  rowarray_list = []
  for row in rows:
      t = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13])
      rowarray_list.append(t)
  
  # Convert query to objects of key-value pairs
  
  objects_list = []
  for row in rows:
  
      d = collections.OrderedDict()
      d['ID'] = row[0]
      d['Nome'] = row[1]
      d['Logr'] = row[2]
      d['Num'] = row[3]
      d['Bairro'] = row[4]
      d['Lat'] = str(row[5])
      d['Lng'] = str(row[6])
      d['Avaliacao'] = str(row[7])
      d['Valor_Alcool'] = str(row[8])
      d['Valor_Gasolina'] = str(row[9])
      d['Valor_GNV'] = str(row[10])
      d['Valor_Diesel'] = str(row[11])
      d['Valor_GasolinaAdt'] = str(row[12])
      d['Valor_GasolinaPremium'] = str(row[13])
      objects_list.append(d)
  
  # convert to json
  
  j = json.dumps(objects_list, encoding='ISO-8859-1')
  
  # output
  
  return "Content-type: application/json\n\n" + j
