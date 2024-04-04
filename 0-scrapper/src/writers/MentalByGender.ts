/*
Corresponde a la Intervención ambulatoria individual o grupal, realizada por un profesional, técnico y/o gestor comunitario. La intervención incluye consejería, evaluación y confirmación diagnóstica, elaboración de plan de cuidados integrales, psicoeducación, acciones de emergencia y desastres, entre otras prestaciones.
Estas atenciones que se describen en este apartado, se analizan desde un punto de vista territorial a nivel nacional, región y Servicio de Salud. Además, se describe los resultados según sexo, grupo de edad y tipo de prestación (profesional/técnico) según año y mes.
 Fuente: REMA 06
*/

import { Context } from '../Types';
import fs from 'fs';
import DeisResults from '../deis/DeisResults';
import DeisClient from '../deis/DeisClient';
import { COMUNAS } from '../Constants';

const PAYLOADS = [
	'MentalByGender',
];

const COLUMNS = ['year', 'male', 'female'];

export default class MentalByGender {
	public static getRequiredPayloads(): string[] {
		return PAYLOADS;
	}

	public static write(_context: Context, _client: DeisClient, results: DeisResults): void {
		for (const payload of PAYLOADS)
		{
			for (const commune of COMUNAS) {
				const comuna = commune.commune;
				for (const establishment of commune.establishments) 
				{
					// get all the data from the results
					console.log(`Writing result for ${payload}-${comuna}-${establishment}`);
					const results_array = results.get(`${payload}-${comuna}-${establishment}`)['data']['valueList'];

					const result_string  = JSON.stringify({
						'report': payload,
						'commune': comuna,
						'establishment': establishment,
						'columns': COLUMNS,
						'data': results_array
					});

					fs.writeFile(`data/${payload}-${comuna}-${establishment}.json`, result_string, function (err: any) {
						if (err) throw err;
					});
				}
			}
		}
	}
}