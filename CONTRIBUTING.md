# Guía de Contribución

¡Gracias por tu interés en contribuir a este repositorio de proyectos de TI y ciberseguridad! Esta guía te ayudará a entender el proceso de contribución y los estándares que seguimos.

## Código de Conducta

Al participar en este proyecto, te comprometes a mantener un ambiente respetuoso y colaborativo. Esperamos que todos los contribuyentes:

- Sean respetuosos y considerados con los demás
- Acepten críticas constructivas
- Se enfoquen en lo que es mejor para la comunidad
- Muestren empatía hacia otros miembros de la comunidad

## Cómo Contribuir

### Reportar Bugs

Si encuentras un bug, por favor crea un issue siguiendo estas pautas:

1. Verifica que el bug no haya sido reportado previamente
2. Usa el template de bug report
3. Incluye pasos detallados para reproducir el problema
4. Describe el comportamiento esperado y el actual
5. Incluye capturas de pantalla si es posible
6. Proporciona información sobre tu entorno (SO, versiones, etc.)

### Sugerir Mejoras

Para sugerir mejoras:

1. Verifica que la mejora no haya sido sugerida previamente
2. Usa el template de feature request
3. Describe claramente la mejora y su caso de uso
4. Explica por qué esta mejora sería útil para el proyecto

### Contribuir con Código

Para contribuir con código:

1. Fork del repositorio
2. Crea una rama para tu contribución (`git checkout -b feature/nueva-caracteristica`)
3. Realiza tus cambios siguiendo las convenciones de código
4. Asegúrate de que tu código pase todas las pruebas
5. Añade o actualiza la documentación según sea necesario
6. Haz commit de tus cambios (`git commit -am 'Añadir nueva característica'`)
7. Push a tu rama (`git push origin feature/nueva-caracteristica`)
8. Crea un Pull Request

## Estándares de Código

### Convenciones Generales

- Usa nombres descriptivos para variables, funciones y clases
- Escribe comentarios claros y útiles
- Mantén el código DRY (Don't Repeat Yourself)
- Sigue los principios SOLID cuando sea aplicable

### Python

- Sigue PEP 8 para el estilo de código
- Usa docstrings para documentar funciones y clases
- Mantén una cobertura de pruebas adecuada

### JavaScript/TypeScript

- Sigue las guías de estilo de ESLint/Prettier
- Usa JSDoc para documentar funciones y clases
- Prefiere funciones puras cuando sea posible

### Terraform/IaC

- Usa nombres descriptivos para recursos
- Organiza los recursos en módulos lógicos
- Documenta las variables y outputs
- Sigue el principio de infraestructura inmutable

### Documentación

- Mantén la documentación actualizada con los cambios de código
- Usa Markdown para toda la documentación
- Incluye ejemplos prácticos cuando sea posible
- Asegúrate de que la documentación sea clara y accesible

## Proceso de Pull Request

1. Asegúrate de que tu PR aborde un issue específico o implemente una mejora clara
2. Incluye una descripción detallada de los cambios
3. Vincula el PR con cualquier issue relacionado
4. Asegúrate de que todas las pruebas automatizadas pasen
5. Solicita revisión de al menos un mantenedor del proyecto
6. Aborda cualquier comentario o sugerencia de la revisión

## Estructura del Repositorio

Respeta la estructura actual del repositorio:

```
proyectos-ti/
├── [proyecto]/
│   ├── docs/
│   ├── src/
│   ├── ejemplos/
│   ├── README.md
│   └── LICENSE
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

## Consideraciones de Seguridad

- No incluyas credenciales o secretos en el código
- Usa variables de entorno o archivos de configuración para secretos
- Sigue las mejores prácticas de seguridad para cada tecnología
- Reporta cualquier problema de seguridad directamente a los mantenedores

## Licencia

Al contribuir a este proyecto, aceptas que tus contribuciones estarán bajo la misma licencia MIT que cubre el proyecto.

---

¡Gracias por contribuir a mejorar estos proyectos de TI y ciberseguridad!

