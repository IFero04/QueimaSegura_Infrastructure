# QUEIMADAS API

## Users

### Register

- **Endpoint:** `/api/users/register`
- **Método:** POST

Registro de usuário:

```json
{
    "full_name": "Teste", //Mais de 3 caracteres
    "email": "af@gmail.com", //Formato de email
    "password": "MD5Hash", //Tem de ser uma hash MD5
    "NIF": "123456789" //validação de NIF
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

### Login

- **Endpoint:** `/api/users/login`
- **Método:** POST

Login de usuário:

```json
{
    "email": "af@gmail.com", //formato de email
    "password": "MD5Hash" //Tem de ser uma hash MD5
}
```

Retorna:

```json
{
    "status": "OK!",
    "message": "User logged in successfully!",
    "result": {
        "user_id": "user_id", //UUID
        "session_id": "session" //UUID
    }
}
```

### Logout

- **Endpoint:** `/api/users/logout/<user_id>/<session_id>`
- **Método:** DELETE

Retorna:

```json
{
    "status": "OK!",
    "message": "User logged out successfully!"
}
```

### Update

- **Endpoint:** `/api/users/update`
- **Método:** PATCH

Login de usuário:

```json
{
    "user": {
        "user_id": "user_id", //UUID
        "session_id": "session" //UUID
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
    "message": "User updated successfully!"
}
```

## Fires

### Register
