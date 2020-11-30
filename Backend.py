import asyncio
import json
import websockets

clients={}

async def lista_usuarios():
  users = []
  for key in clients.keys():
    users.append(key)
  users_message = json.dumps({
    'type': 'users',
    'message': users
  })
  print("Broadcasting:", users_message)
  await mensagem_broadcast(users_message)

async def recebe_mensagem(websocket, path):
  async for i in websocket:
    message = json.loads(i)
    if message['type'] == 'signup':
      if not clients.get(message['user']):
        clients[message['user']] = [websocket, message['userId']]
        await nome_aceito(message['user'], message['userId'])
        await lista_usuarios()
      else:
        await nome_invalido(websocket, message['user'], message['userId'])
    if message['type'] == 'message':
      if message['message'][0] == "~":
        user = message['message'].split()[0][1:]
        print(user)
        await enviar_privado(user, message)
      elif clients.get(message['user']):
        await mensagem_broadcast(i)

async def nome_invalido(websocket, username,userId):
  reject_message = json.dumps({
    'type': 'reject',
    'user':username,
    'message':'Username already in use',
    'userId':userId}
  )
  await websocket.send(reject_message)

async def mensagem_broadcast(message):
  global clients
  disconnectedUsers = []
  for user in clients.keys():
    client = clients.get(user)[0]
    try:
      await client.send(message)
    except:
      disconnectedUsers.append(user)

  for user in disconnectedUsers:
    clients.pop(user)
  if len(disconnectedUsers) > 0:
    await lista_usuarios()

async def nome_aceito(username,userId):
  accept_message = json.dumps({
    'type': 'accepted',
    'user':username,
    'message':'Username accepted',
    'userId':userId}
  )
  await mensagem_broadcast(accept_message)

async def enviar_privado(user,message):
  global clients
  if clients.get(user):
    client = clients.get(user)[0]
    realMessage = message['message'].split()
    print(realMessage)
    realMessage = realMessage[1:]
    print(realMessage)
    message['message'] = " ".join(realMessage)
    print("To:",user,"; Message: ", message)
    try:
      await client.send(json.dumps(message))
    except:
      clients.pop(user)
      await lista_usuarios()

start_server = websockets.serve(recebe_mensagem, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever() 