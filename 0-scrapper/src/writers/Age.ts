import { Context } from '../Types';
import fs from 'fs';
import DeisResults from '../deis/DeisResults';
import DeisClient from '../deis/DeisClient';
import { COMUNAS } from '../Constants';

const PAYLOADS = [
	// 'AttendanceByAge',
	// 'ConsultationByAge',
	'ConsultationSpecialistByAge',
];

const COLUMNS = ['year', '0 to 9', '10 to 14', '15 to 19', '20 to 29', '30 to 44', '45 to 59', '60+'];

export default class Age {
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