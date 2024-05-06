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
	/*
		En este apartado se identifican todas las atenciones realizadas por un médico general, o especialista (APS o Especialidad).
		Estas atenciones que se describen en este apartado, se analizan desde un punto de vista territorial a nivel nacional, región y Servicio de Salud. Además, se describen los resultados según sexo, grupo de edad y tipo de prestación (profesional/técnico) según año y mes.
		Fuente: REM A04
	*/
	'ConsultationByGender': 'Total Consultas Médicas del Programa de Salud Mental según sexo',
	'ConsultationByAge': 'Consultas Médicas del Programa de Salud Mental por Grupo de edad',
	'ConsultationBySpecialGroup': 'Consultas Médicas del Programa de Salud Mental grupos de especial protección',
	'ConsultationByMonth': 'Número de Consultas Médicas por mes y Año',

	// consultas medicas de especialidad
	/*
		En este apartado se identifican todas las atenciones realizadas por un médico general, o especialista  en el nivel de Especialidad.
		Estas atenciones que se describen en este apartado, se analizan desde un punto de vista territorial a nivel nacional, región y Servicio de Salud. Además, se describen los resultados según sexo, grupo de edad y tipo de prestación (profesional/técnico) según año y mes.
		Fuente: REM A07
	*/
	'ConsultationSpecialist': 'Total Atenciones Médicas  Especialidad  Salud Mental',
	'ConsultationSpecialistByGender': 'Porcentaje de Atenciones Médicas Especialidad Salud Mental por sexo',
	'ConsultationSpecialistByAge': 'Consultas Médicas Especialidad Salud Mental por Grupo de edad',
	'ConsultationSpecialistByMonth': 'Consultas Médicas Especialidad Salud Mental por mes',

	// Evaluaciones de salud mental
	/*
		Test de Edimburgo: Corresponde a un test de evaluación que permiten identificar sintomatología depresiva en mujeres en etapa Pre y Post natal .

		M-CHAT:
		Instrumento que permite evaluar la Sospecha de Trastornos del Espectro Autista  (TEA) en Niños y niñas de 16 a 30 meses de edad.
		Sus criterios de aplicación, entre otros, considera una evaluación de desarrollo psicomotor (EEDP) con alteración de las áreas de Lenguaje y/o Social y derivación a especialidad cuando el diagnóstico del instrumento resulta alterado.
		Fuente: REM A03
	*/
	'EdimburgPregnant': 'Evaluaciones a Gestantes con Escala de Edimburgo según resultado',
	'EdimburgPostPartum': 'Evaluaciones a Mujeres Post Parto con Escala de Edimburgo según resultado',
	'MCHAT18month': 'Aplicación Tamizaje Trastorno Espectro Autista (MCHAT) - Niños(as) con Control a los 18 meses según sexo',
	'MCHAT30month': 'Aplicación Tamizaje Trastorno Espectro Autista (MCHAT) - Evaluación Niños 16 a 30 meses según sexo',

	// Ingresos al programa de salud mental
	/*
		Ingresos al Programa de Salud Mental: Corresponde a las personas que se atienden por primera vez o reingresan a control en el Programa de Salud Mental.
		Si una persona presenta uno o más factores de riesgo, o uno o más diagnósticos, se considera como un solo ingreso a dicho programa y uno o mas ingresos a cada uno de los factores de riesgo y/o diagnósticos. Este registro no permite el análisis por comorbilidad, ni permite el análisis por persona.
		Egresos del Programa de Salud Mental: Corresponde a las personas que egresan del Programa de Salud Mental luego que un profesional responsable da término a la modalidad de control de un paciente.
		Fuente: REM A05
	*/
	'IngressByGender': 'Total de Ingresos al Programa de Salud Mental según sexo',
	'IngressByAge': 'Total de Ingresos al Programa de Salud Mental por grupo de edad',
	'IngressBySpecialGroup': 'Ingresos al Programa de Salud Mental grupos de especial protección',
	'IngressByMonth': 'Ingresos Programa de Salud Mental por mes y año',

	// Ingresos al programa de salud mental - diagnosticos
	/*
		Ingresos al Programa de Salud Mental: Corresponde a las personas que se atienden por primera vez o reingresan a control en el Programa de Salud Mental.
		Si una persona presenta uno o más factores de riesgo, o uno o más diagnósticos, se considera como un solo ingreso a dicho programa y uno o mas ingresos a cada uno de los factores de riesgo y/o diagnósticos. Este registro no permite el análisis por comorbilidad, ni permite el análisis por persona.
		Egresos del Programa de Salud Mental: Corresponde a las personas que egresan del Programa de Salud Mental luego que un profesional responsable da término a la modalidad de control de un paciente.
		Fuente: REM A05
	*/
	'IngressDiagnosticMood': 'Ingresos al Programa de Salud Mental - Trastornos del Humor (Afectivos)',
	'IngressDiagnosticAnxiety': 'Ingresos al Programa de Salud Mental - Trastornos Ansiosos',
	'IngressDiagnosticDementia': 'Ingresos al Programa de Salud Mental - Otras Demencias',
	'IngressDiagnosticSubstance': 'Ingresos al Programa de Salud Mental - Consumo de sustancias',
	'IngressDiagnosticDevelopment': 'Ingresos al Programa de Salud Mental - Trastornos del Desarrollo',

	// Egresos del programa de salud mental
	/*
		Ingresos al Programa de Salud Mental: Corresponde a las personas que se atienden por primera vez o reingresan a control en el Programa de Salud Mental.
		Si una persona presenta uno o más factores de riesgo, o uno o más diagnósticos, se considera como un solo ingreso a dicho programa y uno o mas ingresos a cada uno de los factores de riesgo y/o diagnósticos. Este registro no permite el análisis por comorbilidad, ni permite el análisis por persona.
		Egresos del Programa de Salud Mental: Corresponde a las personas que egresan del Programa de Salud Mental luego que un profesional responsable da término a la modalidad de control de un paciente.
		Fuente: REM A05
	*/
	'EgressByGender': 'Total de Egresos del Programa de Salud Mental según sexo',
	'EgressByAge': 'Egresos del Programa por grupo de edad',
	// NOT INDEXED CORRECTLY 'EgressBySpecialGroup': 'Egresos Programa de Salud Mental Grupos de especial protección', 
	'EgressByMonth': 'Egresos Programa de Salud Mental por mes y año',

	// Egresos del programa de salud mental - diagnosticos
	/*
		Ingresos al Programa de Salud Mental: Corresponde a las personas que se atienden por primera vez o reingresan a control en el Programa de Salud Mental.
		Si una persona presenta uno o más factores de riesgo, o uno o más diagnósticos, se considera como un solo ingreso a dicho programa y uno o mas ingresos a cada uno de los factores de riesgo y/o diagnósticos. Este registro no permite el análisis por comorbilidad, ni permite el análisis por persona.
		Egresos del Programa de Salud Mental: Corresponde a las personas que egresan del Programa de Salud Mental luego que un profesional responsable da término a la modalidad de control de un paciente.
		Fuente: REM A05
	*/
	'EgressDiagnosticMood': 'Ingresos al Programa de Salud Mental - Trastornos del Humor (Afectivos)',
	'EgressDiagnosticAnxiety': 'Ingresos al Programa de Salud Mental - Trastornos Ansiosos',
	'EgressDiagnosticDementia': 'Egresos Programa de Salud Mental - Alzheimer y Otras Demencias',
	'EgressDiagnosticSubstance': 'Ingresos al Programa de Salud Mental - Consumo de sustancias',
	'EgressDiagnosticDevelopment': 'Ingresos al Programa de Salud Mental - Trastornos del Desarrollo',

	// Atenciones remotas contexto COVID
	/*
		Corresponden a los registros de todas aquellas actividades implementadas, tanto de atención Primaria como Secundaria, ante la eventualidad de una emergencia Sanitaria, que impida realizar las atenciones de forma presencial en los Centros de Salud, obligando a incluir modalidades remotas de atención.
		Fuente: REM F (2020), REM A32 (2021)
	*/

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
		let skipped = 0;
		let correct = 0;
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
						skipped++;
						continue;
					}
					const data = result['data']['valueList'];

					// get columns
					// result['variables']
					const columns: string[] = [];
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
					correct++;
				}
			}
		});
		console.log(`Skipped ${skipped} results`);
		console.log(`Wrote ${correct} results`);
	}
}