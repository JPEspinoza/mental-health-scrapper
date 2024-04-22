import { Context } from '../Types';
import fs from 'fs';
import DeisResults from '../deis/DeisResults';
import DeisClient from '../deis/DeisClient';
import { COMUNAS } from '../Constants';

const PAYLOADS = [
	// 'AttendanceByMonth',
	// 'ConsultationByMonth',
	'ConsultationSpecialistByMonth',
];

export default class Month {
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

					let month_order;

					try {
						month_order = results.get(`${payload}-${comuna}-${establishment}`)['stringTable']['valueList'];
					}
					catch(e) {
						month_order = ['Abril', 'Agosto', 'Diciembre', 'Enero', 'Febrero', 'Julio', 'Junio', 'Marzo', 'Mayo', 'Noviembre', 'Octubre', 'Septiembre'];
					}

					const result_string  = JSON.stringify({
						'report': payload,
						'commune': comuna,
						'establishment': establishment,
						'columns': ['month', 'year', 'value'],
						'month_order': month_order,
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