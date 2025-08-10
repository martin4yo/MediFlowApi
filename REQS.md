Gestión de consultorios.

ABMs
	⁃	Usuarios
	⁃	Perfiles

A cada perfil se le asignan permisos para acceder a las funciones definidas (administrador, recepción, profesional, etc).

	⁃	Centros Médicos
	⁃	Especialidades
	⁃	Prácticas

Las prácticas se asocian a las especialidades para que el usuario tenga la posibilidad de seleccionarlas al dar de alta un profesional.
A cada práctica se le puede definir un procedimiento de preparación (hs de ayuno, requisitos para las imágenes, etc.)
Es obligatorio que cada Especialidad tenga al menos una práctica.
Las especialidades no se asocian a cada Centro porque esa información sale de los profesionales que se asignan a cada centro. Cada profesional tiene asociadas las especialidades y de esta forma se sabe qué atención se brinda en cada Centro.

	⁃	Profesionales
	⁃	Coberturas

A cada profesional se le asocian las especialidades y las prácticas que corresponda. 
Cada profesional tiene asociado un usuario del sistema.
Cada profesional se puede asignar a uno o varios centros, indicando días y horarios de atención en cada uno, tiempo de atención de cada paciente y cantidad de días de agenda para asignar turnos.
Las coberturas permiten registrar las obras sociales y prepagas, a las cuales se les puede asignar las especialidades y practicas que cubre.
Luego se pueden asociar a cada profesional y comparando las prácticas de la cobertura con las prácticas del profesional se recupera la lista de prácticas cubiertas, permitiendo eliminar prácticas en las cuales el profesional no cursa a través de la cobertura (particular).
Cuando una práctica es particular se debe permitir indicar si la cobra el centro o la cobra directamente el profesional.

De esta forma se define que profesionales trabajan en cada centro, que especialidades se atienden en cada uno y cuáles tienen cobertura y cuáles son particulares.

	⁃	Pacientes

Registra los datos de cada paciente indicando entre otra información que cobertura tiene.

	⁃	Gestion de Turnos
	⁃	Gestion de Historias Clinicas

SOLICITUD DE TURNOS
Se selecciona la especialidad.
Se selecciona la práctica.
Se selecciona el profesional.
Se muestra la agenda del profesional con los días y horarios disponibles.
Se selecciona un horario.
Se informa el centro al que debe concurrir el paciente.
Se le informa al paciente la preparación previa que requiera.
Al reservar el turno se envía un mail al paciente para informarle la reserva.
El día previo al turno solicitado la aplicación envía al paciente un recordatorio solicitando cancelar el turno telefónicamente o por WhatsApp si no va a concurrir.

ATENCIÓN DIARIA
Se recupera la agenda del día con la lista de profesionales que van a atender en el centro mostrando el horario en que estarán disponibles.
Cuando llega el profesional recupera su agenda e informa que está disponible para la atención.
Al llegar el paciente se lo busca en la lista de turnos asignados, se marca como presente en espera y le aparece el paciente al profesional que corresponda.
El profesional llama al paciente que está en espera e indica en el sistema que está en atención.
En este momento puede acceder a la historia clínica que permite por cada fecha escribir texto libre, registrar indicaciones, pegar imágenes, asociar archivos y generar la receta con la prescripción y las indicaciones.
(Receta digital se usa solo para medicamentos o es para cualquier práctica? Imágenes, laboratorio, etc.)
Una vez que el paciente es atendido el profesional indica el fin de la atención.

A DEFINIR
	⁃	Reportes de control 
	⁃	Facturación a Coberturas
	⁃	Gestión de proveedores
	⁃	Reportes de atención, rendimiento
