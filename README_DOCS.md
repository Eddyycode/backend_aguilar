# Documentación Estática de API - Despliegue en Vercel

## 📚 Archivos Generados

✅ `schema.yml` - Schema OpenAPI/Swagger de tu API (58KB)
✅ `index.html` - Página HTML con ReDoc
✅ `vercel.json` - Configuración para Vercel (sitio estático)

## 🚀 Desplegar en Vercel (3 pasos)

### Opción 1: Usando la Web de Vercel (MÁS FÁCIL - 2 minutos)

1. **Ve a https://vercel.com** e inicia sesión con GitHub

2. **Click en "Add New..." > "Project"**

3. **Importa tu repositorio** o arrastra los archivos:
   - `index.html`
   - `schema.yml`
   - `vercel.json`

4. **Click en "Deploy"**

5. **¡Listo!** Tu documentación estará en:
   ```
   https://tu-proyecto.vercel.app
   ```

### Opción 2: Usando Vercel CLI (Rápido)

```bash
# 1. Instalar Vercel CLI
npm install -g vercel

# 2. Hacer login
vercel login

# 3. Deploy
vercel

# 4. Para producción
vercel --prod
```

**Resultado**: Te dará una URL como `https://tu-proyecto.vercel.app`

## 🎨 Vista Previa Local

Antes de desplegar, puedes ver cómo se ve:

```bash
# Opción 1: Con Python
python3 -m http.server 8080

# Opción 2: Con Node.js
npx serve

# Luego abre: http://localhost:8080
```

## 📦 ¿Qué incluye la documentación?

- ✅ Todos los endpoints de tu API
- ✅ Modelos de datos con ejemplos
- ✅ Parámetros y respuestas
- ✅ Filtros de fecha documentados
- ✅ Ejemplos de llamadas
- ✅ Códigos de respuesta HTTP
- ✅ Interfaz interactiva con ReDoc

## 🔄 Actualizar la Documentación

Cuando modifiques tu API, regenera el schema:

```bash
# 1. Activar entorno virtual
source env/bin/activate

# 2. Regenerar schema
python manage.py spectacular --file schema.yml

# 3. Hacer commit
git add schema.yml
git commit -m "Actualizar documentación API"
git push

# Vercel desplegará automáticamente los cambios
```

## 🌐 Compartir la Documentación

Una vez desplegada, comparte la URL:

```
https://tu-proyecto.vercel.app
```

**Características**:
- ✅ Acceso público (sin necesidad de login)
- ✅ HTTPS automático
- ✅ CDN global (carga rápida en todo el mundo)
- ✅ Gratis para proyectos personales
- ✅ Deploy automático desde GitHub

## 📱 Personalizar

### Cambiar nombre del proyecto:

Edita `vercel.json`:
```json
{
  "version": 2,
  "name": "mi-api-docs",
  "cleanUrls": true,
  "trailingSlash": false
}
```

### Agregar favicon o logo:

Agrega en `index.html`:
```html
<link rel="icon" href="favicon.ico">
```

## ❓ Problemas Comunes

### No se ve el ReDoc:

- Verifica que `schema.yml` esté en la misma carpeta que `index.html`
- Revisa la consola del navegador para errores

### Cambios no se reflejan:

```bash
# Limpiar caché de Vercel
vercel --prod --force
```

### Error 404:

- Asegúrate de que `index.html` esté en la raíz del proyecto

## 🎯 Próximos Pasos

1. ✅ Deploy en Vercel
2. ✅ Comparte la URL con tu equipo
3. ✅ Configura deploy automático desde GitHub
4. ✅ Personaliza el diseño si lo deseas

## 💡 Ventajas de Documentación Estática

- ✅ **Sin servidor**: No necesitas mantener un backend corriendo
- ✅ **Gratis**: Hosting gratuito en Vercel
- ✅ **Rápido**: Se carga instantáneamente
- ✅ **Simple**: Solo HTML y YAML
- ✅ **Seguro**: No expone tu base de datos

## 📖 Recursos

- [ReDoc](https://redocly.com/redoc)
- [Vercel Docs](https://vercel.com/docs)
- [OpenAPI Specification](https://swagger.io/specification/)

---

**¿Necesitas ayuda?** Pregúntame cualquier cosa sobre el deployment.
# Forzar redespliegue jueves, 27 de noviembre de 2025, 09:46:06 CST
