import { Context } from '../Types';
import fs from 'fs';
import DeisResults from '../deis/DeisResults';
import DeisClient from '../deis/DeisClient';
import { COMUNAS } from '../Constants';

interface Payload {
	// key is name, value is description
	[key: string]: string;
}

const PAYLOADS: Payload = {
	// Atenciones de salud mental
	/*
		Corresponde a la Intervención ambulatoria individual o grupal, realizada por un profesional, técnico y/o gestor comunitario. La intervención incluye consejería, evaluación y confirmación diagnóstica, elaboración de plan de cuidados integrales, psicoeducación, acciones de emergencia y desastres, entre otras prestaciones.
		Estas atenciones que se describen en este apartado, se analizan desde un punto de vista territorial a nivel nacional, región y Servicio de Salud. Además, se describe los resultados según sexo, grupo de edad y tipo de prestación (profesional/técnico) según año y mes.
 		Fuente: REMA 06
	*/
	'AttendanceByGender': 'Total Atenciones del Programa de Salud Mental según sexo',
	'AttendanceByAge': 'Total Atenciones del Programa de Salud Mental por Grupo de edad',
	'AttendanceByProfessional': 'Distribución Porcentual de Atenciones del Programa de Salud Mental por profesional',
	'AttendanceByMonth': 'Atenciones del Programa de Salud Mental por mes y Año',

	// Consultas medicas
	'ConsultationByGender': 'Total Consultas Médicas del Programa de Salud Mental según sexo',
	'ConsultationByAge': 'Consultas Médicas del Programa de Salud Mental por Grupo de edad',
	'ConsultationBySpecialGroup': 'Consultas Médicas del Programa de Salud Mental grupos de especial protección',
	'ConsultationByMonth': 'Número de Consultas Médicas por mes y Año',

	// consultas medicas de especialidad
	'ConsultationSpecialist': 'Total Atenciones Médicas  Especialidad  Salud Mental',
	'ConsultationSpecialistByGender': 'Porcentaje de Atenciones Médicas Especialidad Salud Mental por sexo',
	'ConsultationSpecialistByAge': 'Consultas Médicas Especialidad Salud Mental por Grupo de edad',
	'ConsultationSpecialistByMonth': 'Consultas Médicas Especialidad Salud Mental por mes',

	// Evaluaciones de salud mental
	'EdimburgPregnant': 'Evaluaciones a Gestantes con Escala de Edimburgo según resultado',
	'EdimburgPostPartum': 'Evaluaciones a Mujeres Post Parto con Escala de Edimburgo según resultado',
	'MCHAT18month': 'Aplicación Tamizaje Trastorno Espectro Autista (MCHAT) - Niños(as) con Control a los 18 meses según sexo',
	'MCHAT30month': 'Aplicación Tamizaje Trastorno Espectro Autista (MCHAT) - Evaluación Niños 16 a 30 meses según sexo',

	// Ingresos al programa de salud mental
	'IngressByGender': 'Total de Ingresos al Programa de Salud Mental según sexo',
	'IngressByAge': 'Total de Ingresos al Programa de Salud Mental por grupo de edad',
	'IngressBySpecialGroup': 'Ingresos al Programa de Salud Mental grupos de especial protección',
	'IngressByMonth': 'Ingresos Programa de Salud Mental por mes y año',

	// Ingresos al programa de salud mental - diagnosticos

	// Egresos del programa de salud mental

	// Egresos del programa de salud mental - diagnosticos

	// Atenciones remotas contexto COVID

	// Intervenciones por patron de consumo

	// Poblacion en control

	// Poblacion en control - diagnosticos

	// Atenciones de urgencia

	// Egresos hospitalarios

	// Egresos hospitalarios por diagnosticos

	// Mortalidad por suicidio

	// Atenciones de urgencia. Analisis comunal

	// Indicador reingreso hospitalario
};

export default class Edimburg {
	public static getRequiredPayloads(): string[] {
		return Object.keys(PAYLOADS);
	}

	public static write(_context: Context, _client: DeisClient, results: DeisResults): void {
		Object.entries(PAYLOADS).forEach(([payload, description]) =>
		{
			for (const commune of COMUNAS) {
				const comuna = commune.commune;
				for (const establishment of commune.establishments) 
				{
					// get all the data from the results
					console.log(`Writing result for ${payload}-${comuna}-${establishment}`);

					const result = results.get(`${payload}-${comuna}-${establishment}`);

					// if no valueList, skip
					if (!result['data']['valueList']) {
						continue;
					}
					const data = result['data']['valueList'];

					// get columns
					// result['variables']
					const columns = [];
					const variables = result['variables'];
					for (let i = 0; i < variables.length; i++) {
						columns.push(variables[i]['label']);
					}

					// get stringtable
					let stringTable = null;
					try {
						stringTable = result['stringTable']['valueList'];
					}
					catch(e) {
						stringTable = null;
					}

					const result_string  = JSON.stringify({
						'report': payload,
						'commune': comuna,
						'establishment': establishment,
						'stringTable': stringTable, 
						'columns': columns,
						'data': data,
						'description': description
					});

					fs.writeFile(`data/${payload}-${comuna}-${establishment}.json`, result_string, function (err: any) {
						if (err) throw err;
					});
				}
			}
		});
	}
}