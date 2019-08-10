''' 
  Proxy Web server for HTTP GET requests
  Run python <filename> <port>

  Note: This server does not handle HTTPS requests
'''
import socket
import sys
import thread
import time
import hashlib
import os.path
import pdb

def GetCurrentTime():
  return time.clock() 

# Returns md5 checksum, used in making cache key of a request
def GetCacheKey(host_url):
  return hashlib.md5('/'.join(host_url)).hexdigest()

def IsCached(host_url):
  return os.path.isfile(GetCacheKey(host_url))

def ReadFromCache(host_url,client_socket):
  start_time = GetCurrentTime()
  cache_content = open(GetCacheKey(host_url), "r")
  contents = cache_content.readlines()
  for i in range(0, len(contents)):
      print (contents[i])
      client_socket.send(contents[i]) # sends requested page back to browser/client
  end_time = GetCurrentTime()
  print "The above is the file read from Cache\n", "Time taken to read from Cache:",end_time - start_time , " Secs"

def WriteInCache(host_url,client_socket):
  start_time = GetCurrentTime()
  request_header = 'GET /'+'/'.join(host_url[1:])+' HTTP/1.0\r\nHost: '+ host_url[0] +'\r\n\r\n'
  cache = open(GetCacheKey(host_url), "a") # cache
  proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    proxy_socket.connect((host_url[0], 80))
    proxy_socket.send(request_header)
    data = proxy_socket.recv(1024)
    while(len(data)>0):
      cache.write(data);
      client_socket.send(data) # sends requested page back to browser/client
      data = proxy_socket.recv(1024)
      print data
  except socket.error as e:
    data =  "Error : Host["+host_url[0]+"] ::\n %s" % e
    client_socket.send(data) # sends requested page back to browser/client
    print data
  finally:  
    end_time = GetCurrentTime()
    proxy_socket.close()
    cache.close()
    print "Time taken to read from Server:",end_time - start_time," Secs"


def ProxyServer(message, client_socket):
  http_method_name = message[0]
  host_url = message[1].split("//")[1].split('/')
  if IsCached(host_url):
    ReadFromCache(host_url,client_socket)
  else:
    WriteInCache(host_url,client_socket)
  client_socket.close
def main():
  if len(sys.argv) <= 1: 
    print ('Port number must be passed: python <filename> <port> ')
    sys.exit(2)
  port = int(sys.argv[1]) 
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_socket.bind(('', port))
  server_socket.listen(5)
  while True:
    print ("Bind Successful\n")
    print ("Connection Accepted\n")
    print ("-------------------------------------")
    client_socket, addr = server_socket.accept() 
    message = client_socket.recv(1024) 
    message = message.split()
    if len(message) <= 1:
      continue  
    
    thread.start_new_thread(ProxyServer ,(message, client_socket))

if __name__ == '__main__':
  main()