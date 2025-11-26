# Guía de Despliegue en Vercel

## Paso 1: Instalar Vercel CLI (si no lo tienes)

```bash
npm install -g vercel
```

## Paso 2: Iniciar sesión en Vercel

```bash
vercel login
```

Esto abrirá tu navegador para autenticarte.

## Paso 3: Desplegar el proyecto

Desde la carpeta del proyecto, ejecuta:

```bash
vercel
```

Responde las preguntas:
- **Set up and deploy?** → `Y` (Yes)
- **Which scope?** → Selecciona tu cuenta
- **Link to existing project?** → `N` (No)
- **What's your project's name?** → `mantenimiento-vehicular-api` (o el nombre que prefieras)
- **In which directory is your code located?** → `.` (punto, directorio actual)

## Paso 4: Configurar Variables de Entorno

En el dashboard de Vercel o usando el CLI:

```bash
vercel env add DATABASE_URL
```

Pega esta URL cuando te lo pida:
```
postgresql://postgres.okaohmivnskagfacrkwm:laloeduardo123489@aws-1-us-east-2.pooler.supabase.com:6543/postgres
```

Repite para cada variable:

```bash
vercel env add SECRET_KEY
# Pega: 8n!$3u1z@l6p0&g#r2-w5!q9f^b1$e7t$0x&k3u@j8m2s4c

vercel env add DEBUG
# Pega: False

vercel env add ALLOWED_HOSTS
# Pega: .vercel.app,.now.sh
```

## Paso 5: Redesplegar con las variables

```bash
vercel --prod
```

## Paso 6: Obtener la URL de tu documentación

Una vez desplegado, Vercel te dará una URL como:
```
https://mantenimiento-vehicular-api-xxx.vercel.app
```

Tus URLs de documentación serán:

**Swagger UI:**
```
https://tu-proyecto.vercel.app/api/schema/swagger/
```

**ReDoc:**
```
https://tu-proyecto.vercel.app/api/schema/redoc/
```

**Endpoints de la API:**
```
https://tu-proyecto.vercel.app/api/vehiculos/
https://tu-proyecto.vercel.app/api/talleres/
https://tu-proyecto.vercel.app/api/mantenimientos/
```

---

## Solución de Problemas

### Error 500 en producción:

1. Verifica las variables de entorno en el dashboard de Vercel
2. Revisa los logs: `vercel logs`

### Static files no cargan:

```bash
vercel --prod --force
```

### Cambios no se reflejan:

```bash
vercel --prod
```

---

## Comandos Útiles

```bash
# Ver logs en tiempo real
vercel logs --follow

# Ver información del proyecto
vercel ls

# Eliminar despliegue
vercel rm nombre-del-proyecto
```
