# QUEIMADAS API

## Register

- **Endpoint:** `/api/users/register`
- **Método:** POST

Registro de usuário:
```json
{
    "user": {
        "full_name": "Teste", //Mais de 3 caracteres
        "email": "af@gmail.com", //Formato de email
        "password": "MD5Hash", //Tem de ser uma hash MD5
        "NIF": "123456789" //validação de NIF
    }
}
```
Retorna:
```json
{
    "status": "OK!",
    "message": "User created successfully!",
    "result": {
        "user_id": "user_id", //UUID
        "session_id": "session" //UUID
    }
}
```

## Login

- **Endpoint:** `/api/users/login`
- **Método:** POST

Login de usuário:
```json
{
    "user": {
        "email": "af@gmail.com", //formato de email
        "password": "MD5Hash", //Tem de ser uma hash MD5
    }
}
```
Retorna:
```json
{
    "status": "OK!",
    "message": "User logged in successfully!",
    "result": {
        "user_id": user_id (UUID),
        "session_id": session (UUID)
    }
}
```

# Logout

- **Endpoint:** `/api/users/logout/<id>/<session_id>`
- **Método:** DELETE

Retorna:
```json
{
    "status": "OK!",
    "message": "User logged out successfully!",
}
```
