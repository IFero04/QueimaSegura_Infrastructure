# QUEIMADAS API

## Users

### Register

- **Endpoint:** `/users/`
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

- **Endpoint:** `/login/`
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

- **Endpoint:** `/logout/?user_id=c2e6f444-55a6-4e7a-be8c-6640bd378c1a&session_id=3bdbf7a4-d15c-4391-a29c-9f091c6832ad`
- **Método:** DELETE

Retorna:

```json
{
    "status": "OK!",
    "message": "User logged out successfully!"
}
```

### Update

- **Endpoint:** `/users/{user_id}/{session_id}/`
- **Método:** PUT

Login de usuário:

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
    "message": "User updated successfully!"
}
```

## Fires

### Register
